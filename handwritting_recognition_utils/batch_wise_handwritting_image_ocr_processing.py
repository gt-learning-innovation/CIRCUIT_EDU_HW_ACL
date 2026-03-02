import os
# Ensure the gemini_inference_utils module in the parent directory can be found
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
import sys
import argparse
import google.generativeai as genai
import PIL.Image
import markdown2
import imgkit
from pathlib import Path
import pandas as pd
from typing import Optional
import re
from dotenv import load_dotenv

# --- Import the newly decoupled module ---
# Assuming gemini_inference_utils.py is located in the handwritting_recognition_utils folder
# or in the same directory as this script.
# Here we assume it is in the utils folder structure relative to the script.
try:
    import handwritting_recognition_utils.MLLM_ocr_utils.gemini_inference_utils as ocr_engine
except ImportError:
    # Compatibility for running directly in the current directory
    sys.path.append(os.path.dirname(__file__))
    import MLLM_ocr_utils.gemini_inference_utils as ocr_engine

load_dotenv()

def normalize_code(s: str) -> str:
    # Match A_B-C or A_B-C_D, take the first three segments A_B-C
    m = re.match(r"^(\d+_\d+-\d+)(?:_\d+)?$", s)
    return m.group(1) if m else s  # If not matched, return the original string

def load_filter_csv(csv_path: Optional[str]):
    """
    If csv_path is empty or None, return None (no filtering).
    Otherwise, read the CSV and check if it contains the required three columns.
    Return a set, elements are (Homework ID, Student ID, Question ID) triplets.
    """
    if not csv_path:  # "" or None -> no filtering
        return None

    df = pd.read_csv(csv_path)

    required_cols = ["Homework ID", "Student ID", "Question ID"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"CSV missing required column: {col}")

    allowed_set = set(
        zip(
            df["Homework ID"].astype(str),
            df["Student ID"].astype(str),
            df["Question ID"].astype(str),
        )
    )

    return allowed_set

def is_allowed(
    homework_id: str, student_id: str, question_id: str, allowed_set
) -> bool:
    """
    If allowed_set is None, return True (no filtering).
    Otherwise, check if the triplet is in allowed_set.
    """
    if allowed_set is None:
        return True

    return (homework_id, student_id, question_id) in allowed_set

# --- 1. Configuration and Constants ---

# --- SECURITY WARNING ---
# API Key should be set in environment variables.
# ---

# (Original load_prompt_from_file function removed, functionality moved to gemini_inference_utils.py)

# --- 2. Gemini API Analysis Function ---

def create_comparison_figure(source_image_path: str, output_dir: str, args: argparse.Namespace):
    """
    Analyzes a single handwriting image, generates a comparison figure,
    and saves it to the specified output directory.

    Args:
        source_image_path (str): The full path to the source image.
        output_dir (str): The directory path to store all output results.
        args (argparse.Namespace): Arguments containing model name, paths, etc.

    Returns:
        str: The full path of the generated comparison image on success,
             or an error message on failure.
    """
    # Get the arguments
    API_model_name = args.API_model_name
    prompt_file_path = args.prompt_file_path
    Official_database_path = args.Official_database_path
    
    # --- Step A: Validate Input ---
    print(f"-> Processing: {source_image_path}")
    if not os.path.exists(source_image_path):
        return f"Error: Source file not found at '{source_image_path}'"

    # --- Step B: Get Markdown from Gemini API (Using Decoupled Module) ---
    print("   - Analyzing image with Gemini (via External Module)...")
    
    try:
        # Call the external module to get the recognized text
        markdown_text = ocr_engine.get_gemini_response(
            source_image_path=source_image_path,
            model_name=API_model_name,
            prompt_file_path=prompt_file_path,
            official_database_path=Official_database_path
        )
    except Exception as e:
        # Catch all exceptions thrown by the external module and return as an error message
        return f"Error: An error occurred during the OCR engine call: {e}"

    print("   - Successfully received Markdown from AI.")

    print("   - Creating side-by-side comparison image...")
    # Note: source_img_pil was also opened in the external module.
    # We open it again here to save the comparison image.
    # For performance optimization, get_gemini_response could return the PIL object,
    # but to keep it fully decoupled, we handle it separately here.
    source_img_pil = PIL.Image.open(source_image_path)

    # --- Step E: Save and Clean Up ---
    path_obj = Path(source_image_path)
    filename = path_obj.name
    # The homework_folder is typically the name of the parent directory.
    homework_folder = path_obj.parent.name
    
    sanitized_filename = filename.replace('.', '_').replace("(", "").replace(")", "").replace("_png", "")
    output_filename = f"{sanitized_filename}_comparison.png"
    final_output_path = os.path.join(output_dir, output_filename)
    
    os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
    
    # (Note: Original code commented out saving comparison_img, keeping as is)
    # print(f"   - Successfully saved comparison image to: {final_output_path}")
    
    # Also save the markdown_text locally.
    markdown_output_path = os.path.join(output_dir, "Text_output", f"{sanitized_filename}_markdown.md")
    os.makedirs(os.path.dirname(markdown_output_path), exist_ok=True)

    abs_path = os.path.abspath(markdown_output_path)
    # Handle long paths on Windows
    with open(f"\\\\?\\{abs_path}", 'w', encoding="utf-8") as md_file:
        md_file.write(markdown_text)

    print(f"   - Markdown content saved to: {markdown_output_path}")

    # Save the markdown file along with source_image_path inserted into the markdown.
    markdown_output_path_compare = os.path.join(output_dir, "Compare", f"{sanitized_filename}_markdown.md")
    os.makedirs(os.path.dirname(markdown_output_path_compare), exist_ok=True)
    
    # Save source_img_pil as a reference in the markdown file.
    img_save_path = os.path.join(output_dir, "Compare", f"{sanitized_filename}_source.png")
    abs_path_img = os.path.abspath(img_save_path)
    source_img_pil.save(f"\\\\?\\{abs_path_img}")
    relative_img_path = f"{sanitized_filename}_source.png"

    markdown_output_path_compare = os.path.abspath(markdown_output_path_compare)
    
    with open(f"\\\\?\\{markdown_output_path_compare}", 'w', encoding="utf-8") as md_file:
        md_file.write(f"![Source Image]({relative_img_path})\n")
        md_file.write(markdown_text)

    print(f"   - Comparison Markdown content saved to: {markdown_output_path_compare}")

    return final_output_path


def main(input_dir_name: str = "Homework_1", output_dir_name: str = "Homework_Trial_1", model_name: str = "models/gemini-2.5-pro", prompt_file_path: str = None):
    """
    Parses command-line arguments, iterates through all PNG images in the input directory,
    and runs the comparison figure generation pipeline for each.
    """
    # --- API Key Setup ---
    # Configure API key globally for the google.generativeai library.
    # This configuration works across modules.
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY environment variable not found.")
    genai.configure(api_key=api_key)

    Official_database_path = None # This is banned because of the copyright issue. If you want to use it, please set it to the path of the official database.
    # --- Argparse Setup ---
    parser = argparse.ArgumentParser(
        description="Traverses a directory and its subdirectories to generate OCR comparison figures for all PNG handwriting images.",
    )
    # Use Path to get the script's directory and build default paths.
    script_parent_dir = "handwritting_recognition_utils"
    default_input = input_dir_name

    parser.add_argument(
        "--input_dir", type=str, default=default_input,
        help=f"The root directory containing Homework subfolders. Default: {default_input}"
    )
    parser.add_argument(
        "--task_name", type=str, default="v6_gemini2p5",
        help=f"The task name to store all generated comparison images. Default: v6_gemini2p5"
    )
    parser.add_argument(
        "--API_model_name", type=str, default=model_name,
        help=f"The Gemini API model to use. Default: {model_name}"
    )
    parser.add_argument(
        "--split_name", type=str, default="debug",
        help=f"Split name (observation, test, debug (contains only one example for debugging)) to store all generated comparison images. Default: debug"
    )
    parser.add_argument(
        "--prompt_file_path", type=str, default=prompt_file_path,
        help="Path to custom prompt file. If not specified, uses default prompt."
    )
    parser.add_argument(
        "--Official_database_path", type=str, default=Official_database_path,
        help="Path to the official database. Default: {Official_database_path}"
    )
    args = parser.parse_args()

    # Determine filter CSV based on split name
    if args.split_name == "observation":
        filter_csv_path = rf"Screenshot_output_anon\set_splitting\obsetf_involved_data.csv"
    elif args.split_name == "test":
        filter_csv_path = rf"Screenshot_output_anon\set_splitting\test_involved_data.csv"
    elif args.split_name == "debug":
        filter_csv_path = rf"Screenshot_output_anon\set_splitting\debug_involved_data.csv"
    else:
        print(f"Invalid split name: {args.split_name}")
        sys.exit(1)
    
    # Simple file existence check to prevent errors in environments without the filter CSV
    if os.path.exists(filter_csv_path):
        allowed_set = load_filter_csv(filter_csv_path)
    else:
        allowed_set = None

    # if allowed_set is None:
    #     print("No filtering applied (CSV not found or None).")
    # else:
    #     print(
    #         f"Filtering applied. Total number of allowed triplets: {len(allowed_set)}"
    #     )

    # --- Run the Pipeline ---
    input_dir = args.input_dir
    # Construct base output directory
    output_dir_base = os.path.join("Outputs", f"{args.task_name}", output_dir_name)

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory does not exist: '{input_dir}'", file=sys.stderr)
        sys.exit(1)

    # Find all PNG files.
    png_files_to_process = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.png'):
                png_files_to_process.append(os.path.join(root, file))

    if not png_files_to_process:
        print("No .png files were found in the specified input directory.")
        sys.exit(0)

    # Process files and record results.
    success_count = 0
    failure_count = 0
    total_files = len(png_files_to_process)
    # print(f"Found {total_files} .png files. Starting processing...\n" + "="*40)

    for i, image_path in enumerate(png_files_to_process):
        # print(f"\n[{i+1}/{total_files}] ", end="")
        
        # Attempt to extract homework_id and student_id from the path, ensuring path depth is as expected
        try:
            homework_id_tmp, student_id_tmp = image_path.split(os.path.sep)[-3:-1]
        except ValueError:
            # If the path structure does not match expectations, skip filter check or handle accordingly
            homework_id_tmp, student_id_tmp = "unknown", "unknown"

        path_obj = Path(image_path)
        filename = path_obj.name
        sanitized_filename = (
            filename.replace(".", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("_png", "")
        )
        question_id = normalize_code(sanitized_filename)

        if not is_allowed(homework_id_tmp, student_id_tmp, question_id, allowed_set):
            # print(
            #     f"Skipping {image_path} because it is not in the allowed "
            #     "Homework/Student/Question set."
            # )
            continue
        
        # Create the final output directory (including model name)
        # Moved outside the loop to prevent recursive path appending
        final_output_dir = os.path.join(output_dir_base, "models", args.API_model_name.split("/")[-1])
        os.makedirs(final_output_dir, exist_ok=True)
        print(f"Input Directory: {input_dir}")
        print(f"Output Directory: {final_output_dir}\n")
        
        result = create_comparison_figure(image_path, final_output_dir, args)
        
        if result.startswith("Error:"):
            print(f"Processing failed. {result}", file=sys.stderr)
            failure_count += 1
        else:
            success_count += 1
    
    # print("\n" + "="*40 + "\nProcessing complete!")
    # print(f"Total files: {total_files}")
    # print(f"Successful: {success_count}")
    # print(f"Failed: {failure_count}")
    # if failure_count == 0:
    #     print("\nAll files were processed successfully.")
    # else:
    #     print(f"\n{failure_count} files failed to process. Please check the error logs above.")

if __name__ == "__main__":
    prompt_version = "v6"
    Student_ids = [f"student_{i}" for i in range(1, 48)]
    # Student_ids = ["student_31"]
    
    # Iterate through specific Homework and Students
    for idx_ in [1, 2, 4, 5, 6, 7, 8]:
        Homework_id = f"Homework{idx_}"
        for Student_id in Student_ids:
            input_dir_name = os.path.join(r"Screenshot_output_anon", Homework_id, Student_id)
            if not os.path.exists(input_dir_name):
                # print(f"Input directory does not exist: {input_dir_name}")
                # If testing or running batch, continue to the next iteration
                continue 
            
            # Use the default model name, or modify it here
            main(input_dir_name=input_dir_name,
                output_dir_name=f"Homework_collected_database_trial_{Homework_id}_{Student_id}",
                model_name="models/gemini-2.5-pro",
                prompt_file_path=rf"handwritting_recognition_utils\Prompts\Initial_prompt_{prompt_version}.txt")