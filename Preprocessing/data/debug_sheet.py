import pandas as pd
import os
import sys

# --- CONFIGURATION: UPDATE THESE FILENAMES ---
FILE1_NAME = "Hp_data.xlsx"
FILE2_NAME = "Digital_duo.xlsx"
# --------------------------------------------

# Define paths
raw_data_path = 'raw_data'
file1_path = os.path.join(raw_data_path, FILE1_NAME)
file2_path = os.path.join(raw_data_path, FILE2_NAME)

all_sheets = {}
try:
    all_sheets.update(pd.read_excel(file1_path, sheet_name=None, header=None))
    all_sheets.update(pd.read_excel(file2_path, sheet_name=None, header=None))
except FileNotFoundError as e:
    print(f"\nERROR: File not found - {e}.")
    sys.exit()

try:
    sheet_name = next((s for s in all_sheets if 'Marketing Channel Breakdown' in s.lower()), None)
    if not sheet_name:
        raise ValueError("Sheet with keyword 'Marketing Channel Breakdown' not found.")
    
    df_debug = all_sheets[sheet_name]
    
    print(f"--- Displaying first 10 rows of the '{sheet_name}' tab ---")
    print(df_debug.head(10).to_string())
    
except (ValueError, KeyError, IndexError) as e:
    print(f"\nERROR: {e}")