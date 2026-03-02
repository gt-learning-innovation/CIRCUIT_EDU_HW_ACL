from dotenv import load_dotenv
import os
load_dotenv()
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

import argparse
from dataset_val import SimpleHomeworkDataset
from torch.utils.data import Dataset, DataLoader
import shutil
from tqdm import tqdm
import glob
import pandas as pd
import numpy as np
import re

# === Import Judge Tool ===
from utils.judge_ocr_diff import judge_difference_v7 as judge_difference

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run LLM as a judge on the data debug full data.",
    )
    parser.add_argument(
        "--task_name", type=str, default="Test",
        help=f"The task name to store all generated comparison images. Default: v6_gemini2p5"
    )
    parser.add_argument(
        "--model_name", type=str, default="gemini-2.5-pro",
        help=f"The model name to use. Default: gemini-3-pro-preview"
    )
    parser.add_argument(
        "--split_name", type=str, default="observation",
        help=f"Split name (observation, test, debug (contains only one example for debugging)) to store all generated comparison images. Default: debug"
    )
    args = parser.parse_args()
    set_type_map = {"observation": "obsetf"}
    if args.split_name not in set_type_map:
        raise ValueError(f"Unsupported split name: {args.split_name}. Valid options are: {list(set_type_map.keys())}")
    SET_TYPE = set_type_map[args.split_name]
    model_name = args.model_name.split("/")[-1]
    JUDGE_MODEL_NAME = "models/gemini-2.5-pro"
    EXAMPLE_FOLDER_PATH = os.path.join("check_recognition_error_val", "LLM-as-a-judge-selection", "fewshot_example_v2") # An example as a reference for the LLM judger to capture the discrepancy between the ground truth and the target model's recognition.
    
    markdown_folder_map = {"obset": "Observationset", "valset1": "Valset", "obset1": "Observationset1", "obsetf": "Observationset_Final"}
    markdown_folder_path = markdown_folder_map[SET_TYPE]
    
    # RANDOM_SELECTED_DATA_INFO_EXCEL_PATH = os.path.join("check_recognition_error_val", "LLM-as-a-judge-selection", "missing_checking", f"Recognition_Detection_{model_name}_{SET_TYPE}_gemini-2.5-pro_full_data.csv")
    RANDOM_SELECTED_DATA_INFO_EXCEL_PATH = os.path.join("check_recognition_error_val", "LLM-as-a-judge-selection", "0_finaloutput_rechecked", f"Recognition_Detection_{model_name}_{SET_TYPE}_gemini-2.5-pro.csv")
    
    # TARGET_MODEL_MARKDOWN_FILE_PATH = os.path.join(markdown_folder_path, args.task_name)
    TARGET_MODEL_MARKDOWN_FILE_PATH = os.path.join("Outputs", f"{args.task_name}")
    ORIGINAL_MARKDOWN_FILE_PATH_LABEL = os.path.join(markdown_folder_path, "v6_Gemini_2p5")
    RECTIFIED_MARKDOWN_FILE_PATH_LABEL = os.path.join("Rectified_recognized_markdown_done_Anon", "Final_4_LLM_judge")
    PROCESSED_EXCEL_FILE_PATH = os.path.join("Processed_final_excel_data_Anon", f"v6_ground_truth_{SET_TYPE}", "Finalized_result_with_comments.xlsx")
    
    random_selected_data_info = pd.read_csv(RANDOM_SELECTED_DATA_INFO_EXCEL_PATH)
    dataset = SimpleHomeworkDataset(excel_path=PROCESSED_EXCEL_FILE_PATH)
    data_loader = DataLoader(dataset, batch_size=1, shuffle=False)
    print("Length of random_selected_data_info: ", len(random_selected_data_info))
    # Core data save list
    judge_results_list = []
    total_count = 0

    for i, batch in tqdm(enumerate(data_loader), total=len(data_loader), desc="Processing OCR Judge"):        
        homework_id = batch["Homework ID"][0]
        student_id = batch["Student ID"][0]
        question_id = batch["Question ID"][0]
        
        # Filter logic: check if the current data is not in the selected list
        if random_selected_data_info[(random_selected_data_info['Homework ID'] == homework_id) & 
                                     (random_selected_data_info['Student ID'] == student_id) & 
                                     (random_selected_data_info['Question ID'] == question_id)].empty:
            continue

        # =========================================================================
        # 1. Load Ground Truth (Label) Markdown
        # =========================================================================
        pattern_str = rf"^{re.escape(str(question_id))}(_[1-9])?_markdown\.md$"
        file_regex = re.compile(pattern_str)

        relative_glob_pattern = os.path.join(
            f"Homework_collected_database_trial_{homework_id}_{student_id}", 
            "models", "gemini-2.5-pro", "Compare", f"{question_id}*_markdown.md"
        )

        def get_filtered_files(base_path, rel_glob):
            full_search_path = os.path.join(base_path, rel_glob)
            candidates = glob.glob(full_search_path)
            return [f for f in candidates if file_regex.match(os.path.basename(f))]
        
        target_label_files = get_filtered_files(RECTIFIED_MARKDOWN_FILE_PATH_LABEL, relative_glob_pattern)
        if not target_label_files:
            target_label_files = get_filtered_files(ORIGINAL_MARKDOWN_FILE_PATH_LABEL, relative_glob_pattern)
            
        if not target_label_files:
            print(f"Warning: Label markdown not found for {question_id}")
            continue

        markdown_content_label = ""
        for markdown_file in target_label_files:
            with open(markdown_file, "r", encoding="utf-8") as f:
                markdown_read = f.read().split("\n")[1:]
                markdown_content_label += "\n".join(markdown_read)
                
        # =========================================================================
        # 2. Load Target Model Markdown
        # =========================================================================
        relative_glob_pattern_target = os.path.join(
            f"Homework_collected_database_trial_{homework_id}_{student_id}", 
            "models", model_name, "Compare", f"{question_id}*_markdown.md"
        )
        
        markdown_files = get_filtered_files(TARGET_MODEL_MARKDOWN_FILE_PATH, relative_glob_pattern_target)
        if len(markdown_files) == 0:
            print(f"Warning: Target markdown not found for {question_id}")
            continue
        
        markdown_content_target = ""
        for markdown_file in markdown_files:
            with open(markdown_file, "r", encoding="utf-8") as f:
                markdown_read = f.read().split("\n")[1:]
                markdown_content_target += "\n".join(markdown_read)

        # =========================================================================
        # 3. Call LLM Judge to Compare
        # =========================================================================
        print(f"Judging: {homework_id} | {student_id} | {question_id}")
        
        judge_output = judge_difference(
            target_content=markdown_content_target, 
            label_content=markdown_content_label,
            model_name=JUDGE_MODEL_NAME,
            example_folder_path=EXAMPLE_FOLDER_PATH
        )
                
        # Save the result directly into the list
        judge_results_list.append({
            "Homework ID": homework_id,
            "Student ID": student_id,
            "Question ID": question_id,
            "Recognition Errors": judge_output
        })
        
        total_count += 1
        if total_count > 19:
            break

    # =========================================================================
    # 4. Save Results to CSV
    # =========================================================================
    if judge_results_list:
        output_df = pd.DataFrame(judge_results_list)
        
        # Construct the output path
        safe_judge_name = JUDGE_MODEL_NAME.split('/')[-1]
        output_csv_filename = os.path.join("Recognition_Detection_outputs", "original", f"Recognition_Detection_{args.task_name}_{SET_TYPE}_{safe_judge_name}.csv")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_csv_filename), exist_ok=True)
        
        # Save as CSV (using utf-8-sig encoding to support Excel opening without garbled characters)
        output_df.to_csv(output_csv_filename, index=False, encoding="utf-8-sig")
        
        print("\n" + "="*40)
        print("PROCESS COMPLETED")
        print("="*40)
        print(f"Total entries processed: {total_count}")
        print(f"Results saved to: {output_csv_filename}")
        print("="*40)
    else:
        print("No results to save.")