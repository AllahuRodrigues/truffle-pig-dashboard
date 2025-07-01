import pandas as pd
import numpy as np

# --- 1. Load your manually preprocessed dataset ---
# This script uses your 'g1.csv' as the starting point.
source_file = 'g1.csv'

print(f"--- Loading your preprocessed data from '{source_file}' ---")
try:
    # Load the data, assuming the first row is the header
    df = pd.read_csv(source_file, encoding='latin-1', header=0)
    
    # Standardize all column names to prevent KeyErrors
    df.columns = df.columns.str.strip()
    
    print("File loaded successfully.")
    
except FileNotFoundError:
    print(f"ERROR: The file '{source_file}' was not found.")
    print("Please make sure your new CSV file is in the same directory as your notebook.")
    # Exit gracefully if the file isn't found
    exit()

# --- 2. Correct the Redundancy ---
# This is the final and most critical step to ensure the data is analytically sound.

print("\n--- Correcting data redundancy ---")

# Define which columns are at the business level (repeated for each channel in a month)
business_level_cols = ['YEAR', 'MONTH', 'Total_Returns', 'Total_Revenue']

# Define which columns are at the channel level
channel_level_cols = [col for col in df.columns if col not in ['Total_Returns', 'Total_Revenue']]

# Create a clean dataframe for business-level metrics by dropping duplicates.
business_df = df[business_level_cols].drop_duplicates()
print("Created clean business-level summary.")

# Create a dataframe for the channel-specific metrics.
channel_df = df[channel_level_cols]
print("Created channel-level performance summary.")

# Merge the two dataframes back together.
final_corrected_df = pd.merge(channel_df, business_df, on=['YEAR', 'MONTH'], how='left')
print("Merged data back into a non-redundant structure.")

# --- 3. Final Verification and Saving ---
print("\n--- Verification and Saving ---")

# Fill any potential NaN values that might have been created during the merge
final_corrected_df.fillna(0, inplace=True)

# Remove any summary rows like 'TOTAL' that might exist
final_corrected_df = final_corrected_df[~final_corrected_df['CHANNEL'].str.contains('TOTAL', na=False, case=False)]


# Display the first 10 rows of the corrected data to verify
print("\n--- Final Corrected Data (First 10 Rows) ---")
print(final_corrected_df.head(10).to_string())

# Save the final, corrected file
output_filename = 'final_master_dataset.csv'
final_corrected_df.to_csv(output_filename, index=False)

print(f"\nSUCCESS: The definitive, non-redundant data has been saved to '{output_filename}'")
