from numpy import False_
import pandas as pd
import re
import os
import argparse
from dotenv import load_dotenv
load_dotenv()
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
from utils.judge_ocr_diff import LLM_judge_content

def build_filter_prompt(error_item):
    return f"""
Analyze the following OCR recognition error report and determine if it is "too strict" or "pedantic" based on the criteria below.

Criteria for deletion (Response: DELETE):
1. Case Sensitivity Only: Differences like 'P' vs 'p', 'V' vs 'v', or 'kWh' vs 'kWH' when the context makes the meaning clear.
2. Mathematical Equivalence: Minor structural changes that are mathematically identical (e.g., $a + (-b)$ vs $a - b$, adding unnecessary parentheses, or switching term order).
3. The "Reason" explicitly mentions that the versions are "mathematically equivalent".
4. Minor LaTeX Nuances: Transcription differences in LaTeX commands that don't change the core meaning (e.g., using `\\sec` instead of `\\text{{sec}}`).
5. Minor Spelling: Simple typos in natural language part that do not hinder understanding.

Criteria for keeping (Response: KEEP):
1. Any numerical errors.
2. Missing entire lines of derivations or equations.
3. Incorrect variable names that change the physics/math meaning (not just case).
4. Wrong operators (e.g., + instead of -).
5. Typos/Differences in variables, symbols (especially in the subscripts, (e.g., R_T, i_L, v_f, etc.)), and units, as they are important for the formula's mathematical/physical meaning.

Error Report to Evaluate:
{error_item}

Instructions:
Respond with ONLY the word "DELETE" if it meets the strictness criteria, or "KEEP" if it is a valid and necessary correction.
"""

def process_recognition_errors(text, model_name):
    text_changed = False
    # 1. Preprocess: convert to string and remove whitespace
    content = str(text).strip() if pd.notna(text) else ""

    # 2. Core judgment: if not starting with "1.", return directly
    if not content.startswith("1."):
        return content, text_changed

    # 3. Improved regular expression split:
    # Must match: newline + number + dot/parenthesis + (optional newline/space) + "Source:"
    # This can effectively avoid the numbering inside the formula (e.g. "3) ["), because the formula will not follow the "Source:" keyword
    split_pattern = r'\n+(?=\d+[\.\)]\s*(?:\n\s*)?Source:)'
    items = re.split(split_pattern, content)
    
    filtered_items = []
    for item in items:
        item = item.strip()
        if not item:
            continue
            
        # Safety check: ensure this item contains the core components of the error report, to prevent accidental cutting
        if "Source:" not in item or "Rectified Version:" not in item:
            # If the content cut out is incomplete, it may be because the regular expression didn't cut it well, merge it with the previous item or skip
            if filtered_items:
                filtered_items[-1] = filtered_items[-1] + "\n" + item
            continue

        # 4. Call LLM to determine
        prompt = build_filter_prompt(item)
        decision = LLM_judge_content(prompt, model_name=model_name).strip().upper()
        
        # Only keep when the model explicitly returns KEEP
        if "KEEP" in decision:
            filtered_items.append(item)
        else:
            text_changed = True
            # Print the filtered items, for debugging
            print(f">>> Filtered (Too Strict): {item}\n")

    # 5. Reassemble the results
    if not filtered_items:
        return "No significant errors found.", text_changed
    
    final_output = []
    for i, item in enumerate(filtered_items, 1):
        # Remove the existing number prefix (only match the starting number)
        # Use count=1 to ensure only the starting number is replaced,不影响 Source 内部可能的编号
        clean_content = re.sub(r'^\d+[\.\)]\s*', '', item, count=1)
        
        # Unified format: number. + newline + content
        final_output.append(f"{i}.\n{clean_content}")
    
    return "\n\n".join(final_output), text_changed

def run_pipeline(input_path, output_path, model_name="gpt-4o", head_name="Recognition Errors"):
    changed_list= []
    # Load data
    if input_path.endswith('.csv'):
        df = pd.read_csv(input_path)
    else:
        df = pd.read_excel(input_path)

    print(f"Starting processing {len(df)} rows using {model_name}...")

    # Iterate through each row
    for index, row in df.iterrows():
        original_errors = row[head_name]
        print(f"Row {row['Homework ID'], row['Student ID'], row['Question ID']} processing...")
        processed_errors, text_changed = process_recognition_errors(original_errors, model_name)
        df.at[index, head_name] = processed_errors if text_changed else original_errors
        if text_changed:
            changed_list.append([row['Homework ID'], row['Student ID'], row['Question ID']])
        
        # break

    # Save results
    df.to_csv(output_path, index=False)
    print(f"Success! Filtered file saved to: {output_path}")
    print("Changed list: \n")
    for item in changed_list:
        print(item)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task_name", type=str, default="v6_Gemini_3")
    parser.add_argument("--model_name", type=str, default="gemini-3-pro-preview")
    parser.add_argument("--split_name", type=str, default="observation")
    args = parser.parse_args()
    
    set_type_map = {"observation": "obsetf"}
    if args.split_name not in set_type_map:
        raise ValueError(f"Unsupported split name: {args.split_name}. Valid options are: {list(set_type_map.keys())}")
    SET_TYPE = set_type_map[args.split_name]
    model_name = args.model_name.split("/")[-1]
    JUDGE_MODEL_NAME = "models/gemini-2.5-pro"
    safe_judge_name = JUDGE_MODEL_NAME.split('/')[-1]
    
    input_path = os.path.join("Recognition_Detection_outputs", "original", f"Recognition_Detection_{args.task_name}_{SET_TYPE}_{safe_judge_name}.csv")
    output_path = os.path.join("Recognition_Detection_outputs", "rechecked", f"Recognition_Detection_{args.task_name}_{SET_TYPE}_{safe_judge_name}.csv")
    head_name = "Recognition Errors"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    model_name = "models/gemini-2.5-pro"
    run_pipeline(input_path, output_path, model_name, head_name)