import pandas as pd
import os
import sys

# --- CONFIGURATION: UPDATE THESE FILENAMES ---
# Make sure these match the names of your files in the 'raw_data' folder.
FILE1_NAME = "Hp_data.xlsx"
FILE2_NAME = "Digital_duo.xlsx"
# --------------------------------------------

raw_data_path = 'raw_data'
all_sheet_names = []

try:
    file1_path = os.path.join(raw_data_path, FILE1_NAME)
    print(f"Reading sheets from '{FILE1_NAME}'...")
    xls1 = pd.ExcelFile(file1_path)
    all_sheet_names.extend(xls1.sheet_names)

    file2_path = os.path.join(raw_data_path, FILE2_NAME)
    print(f"Reading sheets from '{FILE2_NAME}'...")
    xls2 = pd.ExcelFile(file2_path)
    all_sheet_names.extend(xls2.sheet_names)

    print("\n--- Detected Sheet Names ---")
    print("The script found the following tabs in your Excel files:")
    for name in all_sheet_names:
        print(f"- {name}")

except FileNotFoundError as e:
    print(f"\nERROR: File not found - {e}.")
    print("Please ensure your Excel files are in the 'raw_data' folder and the filenames in this script are correct.")
    sys.exit()
except Exception as e:
    print(f"\nAn error occurred: {e}. Please ensure 'openpyxl' is installed.")
    sys.exit()