import pandas as pd
import re
import os
import argparse
from dotenv import load_dotenv
load_dotenv()
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

def process_error_csv(input_path):
    # 1. Load the CSV file
    # Considering that the table may contain LaTeX formulas or multiple lines of text, it is recommended to use utf-8 encoding
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Failed to read file: {e}")
        return

    def count_errors(text):
        # If the text is empty or "No significant errors found.", the number of errors is 0
        if pd.isna(text) or "No significant errors found." in str(text):
            return 0
        
        # Handle exception error cases (such as FinishReason errors for student_38, 1_5-3)
        if str(text).startswith("Error:"):
            return 1
        
        # Matching pattern: find the number dot at the beginning of the line (e.g. "1.", "2.")
        # Use re.MULTILINE to ensure ^ can match the beginning of each line
        error_items = re.findall(r'^\d+\.\s*$', str(text), re.MULTILINE)
        
        # If the number is found, return the number of errors
        if error_items:
            return len(error_items)
        
        # If the text is neither "No errors" nor "1. 2." structure, but has content, conservatively count as 1 error
        if len(str(text).strip()) > 0:
            return 1
        
        return 0

    # 2. Count the number of errors and add a new column
    df['Error Count'] = df['Recognition Errors'].apply(count_errors)

    # 3. Save the new file
    output_path = "processed_" + os.path.basename(input_path)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    # 4. Calculate the statistical data
    total_rows = len(df)
    total_errors = df['Error Count'].sum()
    avg_errors = df['Error Count'].mean()
    
    rows_with_errors = df[df['Error Count'] > 0]
    rows_without_errors = df[df['Error Count'] == 0]
    
    count_has_error = len(rows_with_errors)
    count_no_error = len(rows_without_errors)
    
    percent_has_error = (count_has_error / total_rows) * 100
    percent_no_error = (count_no_error / total_rows) * 100

    # 5. Print the results
    print("-" * 30)
    print(f"Processing completed! New file saved to: {output_path}")
    print("-" * 30)
    print(f"Statistical report:")
    print(f"1. Total number of data rows: {total_rows}")
    print(f"2. Total number of errors (sum of all rows): {total_errors}")
    print(f"3. Average number of errors per row: {avg_errors:.2f}")
    print(f"4. Number of rows with errors: {count_has_error} rows ({percent_has_error:.2f}%)")
    print(f"5. Number of rows without errors: {count_no_error} rows ({percent_no_error:.2f}%)")
    print("-" * 30)


if __name__ == "__main__":    
    parser = argparse.ArgumentParser()
    parser.add_argument("--task_name", type=str, default="Test")
    parser.add_argument("--model_name", type=str, default="models/gemini-2.5-pro")
    parser.add_argument("--split_name", type=str, default="observation")
    args = parser.parse_args()
    
    set_type_map = {"observation": "obsetf"}
    if args.split_name not in set_type_map:
        raise ValueError(f"Unsupported split name: {args.split_name}. Valid options are: {list(set_type_map.keys())}")
    SET_TYPE = set_type_map[args.split_name]
    model_name = args.model_name.split("/")[-1]
    JUDGE_MODEL_NAME = "models/gemini-2.5-pro"
    safe_judge_name = JUDGE_MODEL_NAME.split('/')[-1]
    
    # loaded_csv_filename = os.path.join("Recognition_Detection_outputs", "original", f"Recognition_Detection_{args.task_name}_{SET_TYPE}_{safe_judge_name}.csv")
    loaded_csv_filename = os.path.join("Recognition_Detection_outputs", "rechecked", f"Recognition_Detection_{args.task_name}_{SET_TYPE}_{safe_judge_name}.csv")
    
    print("loaded_csv_filename: ", loaded_csv_filename)
    process_error_csv(loaded_csv_filename)