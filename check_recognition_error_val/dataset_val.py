import os
import pandas as pd
from torch.utils.data import Dataset

class SimpleHomeworkDataset(Dataset):
    """
    A simplified PyTorch Dataset.
    Used to read Excel files containing 'Homework ID', 'Student ID', 'Question ID'.
    """
    def __init__(self, excel_path: str, root_dir: str = None):
        """
        Args:
            excel_path (str): The path of the Excel file.
            root_dir (str, optional): The root directory path of the dataset.
                                      If this path is provided, __getitem__ will try to automatically generate the full path of the image.
        """
        super().__init__()
        self.root_dir = root_dir
        
        # --- 1. Load Excel file ---
        try:
            # Read Excel, force read as strings, to prevent '1_5-2' from being mistakenly recognized as a date or formula
            self.data = pd.read_excel(excel_path, dtype=str)
        except FileNotFoundError:
            print(f"Error: File not found: {excel_path}")
            self.data = pd.DataFrame()
            return
        
        # Simple check if the necessary columns are included
        required_cols = ["Homework ID", "Student ID", "Question ID"]
        if not all(col in self.data.columns for col in required_cols):
            print(f"Warning: Excel file is missing the necessary columns. Expected to contain: {required_cols}")

        print(f"Data loaded successfully. Total {len(self.data)} rows.")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int):
        """
        Return a dictionary, containing ID information.
        If the root directory is provided, it will also contain 'image_path'.
        """
        if idx >= len(self):
            raise IndexError("Index out of range")
            
        # Get the row data
        row_series = self.data.iloc[idx]
        row_dict = row_series.to_dict()
        
        # --- Optional: if the root directory is provided, automatically build the image path ---
        # This step is to make it easier to read images directly, without having to concatenate paths in the training code
        if self.root_dir:
            # Construct the folder name and file name based on the previous logic
            # Excel format: Homework ID="Homework1", Student ID="student_2", Question ID="1_5-2"
            # Folder name: Homework_collected_database_trial_Homework1_student_2
            
            folder_name = f"Homework_collected_database_trial_{row_dict['Homework ID']}_{row_dict['Student ID']}"
            file_name = f"{row_dict['Question ID']}_comparison.png"
            
            # Construct the full path: root / folder / models / gemini-2.5-pro / file
            full_path = os.path.join(
                self.root_dir, 
                folder_name, 
                "models", 
                "gemini-2.5-pro", 
                file_name
            )
            
            row_dict['image_path'] = full_path
            

        return row_dict