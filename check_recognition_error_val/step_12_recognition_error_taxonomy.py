import pandas as pd
import re
import os
from dotenv import load_dotenv
load_dotenv()
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
from utils.judge_ocr_diff import LLM_judge_content
from tqdm import tqdm
tqdm.pandas()
import argparse

# ================= LLM Accessory Functions =================

def build_classification_prompt(item_content):
    """
    Constructs the prompt for the LLM to categorize the OCR error.
    """
    prompt = f"""
As an expert in Electronic Engineering education and OCR quality assessment, categorize the following recognition error into one of the four major types:

Category 1: Symbol & Character Errors (Low-level OCR)
- Includes: Misreading numbers/letters (e.g., '20000' as '2a000'), missing negative signs, operator misrecognition, and unit/prefix errors (e.g., 'μF' as 'mF' or 'MF').

Category 2: Structural & Mathematical Notation Errors
- Includes: Broken formula structures (e.g., fractions split across lines), missing parentheses, inconsistent variables (e.g., 'vc' becoming 'vo' mid-derivation), and dimensional inconsistencies.

Category 3: Visual & Diagrammatic Reasoning Errors
- Includes: Incorrect circuit topology (e.g., identifying parallel as series), misaligning attributes to wrong components, reversed polarity/direction, and hallucinations regarding diagram elements.

Category 4: Textual & Logical Flow Errors
- Includes: Omission of critical steps, mislabeling physics laws (e.g., writing KVL when KCL was used), and boundary condition mismatches (e.g., 't < 0' misread as 't > 0').

---
Error Item Content:
{item_content}
---

Task: Output ONLY the category number (1, 2, 3, or 4). Do not include any other text.
"""
    return prompt

def LLM_classify_item(item_content, model_name):
    """
    Wrapper for the LLM call. Replace the placeholder logic with your actual LLM API call.
    """
    prompt = build_classification_prompt(item_content)
    
    # Example placeholder: Replace with your actual LLM_judge_content call
    response = LLM_judge_content(prompt, model_name=model_name)
    return response.strip()
    
    # return "1"  # Defaulting to "1" for demonstration purposes

# ================= Core Processing Pipeline =================

def classify_recognition_errors_pipeline(input_path, output_path, model_name="models/gemini-2.5-pro"):
    """
    Reads the CSV, splits error items, classifies them using an LLM, 
    and saves the results with category headers. Includes a progress bar.
    """
    # Load dataset
    df = pd.read_csv(input_path)
    
    # Initialize new columns for the 4 categories
    cat_columns = ['Category 1', 'Category 2', 'Category 3', 'Category 4']
    for col in cat_columns:
        df[col] = ""

    def process_row(row):
        text = row['Recognition Errors']
        content = str(text).strip() if pd.notna(text) else ""

        # Logic: If it doesn't start with "1.", there are no errors to process
        if not content.startswith("1."):
            return row

        # Regex split: Matches a newline followed by "Number. Source:"
        split_pattern = r'\n+(?=\d+[\.\)]\s*(?:\n\s*)?Source:)'
        items = re.split(split_pattern, content)
        
        # Buckets to hold the IDs of items belonging to each category
        buckets = {1: [], 2: [], 3: [], 4: []}
        
        item_id = 1
        for item in items:
            item = item.strip()
            if not item or "Source:" not in item:
                continue
            
            # Get classification from LLM 
            # Note: Ensure LLM_classify_item is defined in your environment
            llm_response = LLM_classify_item(item, model_name)
            
            # Extract number using regex to ensure robustness
            match = re.search(r'[1-4]', llm_response)
            if match:
                cat_id = int(match.group())
                buckets[cat_id].append(item_id)
            
            item_id += 1

        # Populate the category columns with list of IDs (e.g., [1, 3])
        for i in range(1, 5):
            # Using str() or list based on your preference for CSV storage
            row[f'Category {i}'] = buckets[i] if buckets[i] else []
            
        return row

    # Apply the logic across the dataframe with a progress bar
    # progress_apply is provided by tqdm
    print(f"Starting classification using model: {model_name}...")
    processed_df = df.progress_apply(process_row, axis=1)
    
    # Save output CSV (using utf-8-sig to ensure Excel compatibility for special symbols)
    processed_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nClassification complete. Saved to: {output_path}")

# ================= Usage Example =================
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
    
    input_path = os.path.join("Recognition_Detection_outputs", "rechecked", f"Recognition_Detection_{args.task_name}_{SET_TYPE}_{safe_judge_name}.csv")
    output_path = os.path.join("Recognition_Detection_outputs", "rechecked_taxonomy", f"Recognition_Detection_{args.task_name}_{SET_TYPE}_{safe_judge_name}.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    classify_recognition_errors_pipeline(input_path, output_path)