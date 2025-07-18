import os
import pandas as pd
import hashlib
import logging
import shutil
from pathlib import Path

# --- 1. LOGGING CONFIGURATION ---
# Create logs directory if it doesn't exist
Path("logs").mkdir(exist_ok=True)

# Pipeline action logger
pipeline_logger = logging.getLogger('PipelineLogger')
pipeline_logger.setLevel(logging.INFO)
pipeline_handler = logging.FileHandler('logs/pipeline.log')
pipeline_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
pipeline_logger.addHandler(pipeline_handler)

# Data error logger
error_logger = logging.getLogger('ErrorLogger')
error_logger.setLevel(logging.WARNING)
error_handler = logging.FileHandler('logs/data_errors.log')
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
error_logger.addHandler(error_handler)


# --- 2. SCHEMA AND CORE FUNCTIONS ---

def setup_project_structure():
    """Creates the necessary directories for the pipeline."""
    Path("data/new").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    pipeline_logger.info("Project directories ensured to exist.")

def hash_user_id(email):
    """Hashes an email using SHA-256 for privacy."""
    if not isinstance(email, str):
        return None
    return hashlib.sha256(email.encode('utf-8')).hexdigest()

def validate_and_process_order_lines(df, file_name):
    """
    Validates the order-line dataframe against the schema and rules.
    Logs bad rows and returns a dataframe with only good rows.
    """
    required_cols = {'order_id', 'customer_id', 'order_datetime', 'sku', 'qty', 'unit_price', 'discount'}
    if not required_cols.issubset(df.columns):
        return None # Not an order-line file

    initial_rows = len(df)
    
    # Rule: No null IDs
    df.dropna(subset=['order_id', 'customer_id'], inplace=True)
    
    # Convert types before validation
    df['qty'] = pd.to_numeric(df['qty'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df.dropna(subset=['qty', 'unit_price'], inplace=True)

    # Rule: qty >= 1 and unit_price >= 0
    condition = (df['qty'] >= 1) & (df['unit_price'] >= 0)
    
    bad_rows = df[~condition]
    if not bad_rows.empty:
        error_logger.warning(f"Found {len(bad_rows)} bad rows in {file_name} failing qty/price rules.")
        for index, row in bad_rows.iterrows():
            error_logger.warning(f"SKIPPED ROW from {file_name} (Index {index}): {row.to_dict()}")

    good_rows = df[condition]
    pipeline_logger.info(f"Validated {file_name}: {len(good_rows)}/{initial_rows} rows are valid.")
    return good_rows

def validate_and_process_sessions(df, file_name):
    """
    Validates the session-level dataframe and applies SHA-256 hashing to user_id.
    """
    required_cols = {'user_id', 'session_id', 'session_start', 'source', 'medium', 'campaign'}
    if not required_cols.issubset(df.columns):
        return None # Not a session file

    pipeline_logger.info(f"Processing {file_name} as session-level data.")
    
    # Hash user_id with SHA-256 before storage
    df['user_id'] = df['user_id'].apply(hash_user_id)
    df.dropna(subset=['user_id'], inplace=True) # Drop rows where hashing failed (e.g., not a string)

    pipeline_logger.info(f"Hashed user_id column for {file_name}.")
    return df

# --- 3. DUMMY DATA CREATION ---

def create_dummy_files():
    """Creates dummy CSV files for testing purposes as per the brief."""
    # Dummy Order-Line CSV
    orders_data = {
        'order_id': [1001, 1002, 1003, 1004, 1005],
        'customer_id': ['cust_a', 'cust_b', None, 'cust_d', 'cust_e'],
        'order_datetime': pd.to_datetime(['2025-07-02 10:00', '2025-07-02 11:00', '2025-07-02 12:00', '2025-07-02 13:00', '2025-07-02 14:00']),
        'sku': ['SKU01', 'SKU02', 'SKU03', 'SKU04', 'SKU05'],
        'qty': [2, 0, 5, 1, 3], # Row with qty=0 should be skipped
        'unit_price': [10.0, 15.0, 20.0, -5.0, 30.0], # Row with price<0 should be skipped
        'discount': [0.1, 0.0, 0.2, 0.0, 0.1]
    }
    orders_df = pd.DataFrame(orders_data)
    orders_df.to_csv('data/new/order_lines_2025-07-02.csv', index=False)

    # Dummy Session-Level CSV
    sessions_data = {
        'user_id': ['user1@example.com', 'user2@example.com', 'user3@example.com'],
        'session_id': ['sess001', 'sess002', 'sess003'],
        'session_start': pd.to_datetime(['2025-07-02 09:00', '2025-07-02 09:15', '2025-07-02 09:30']),
        'source': ['google', 'facebook', 'google'],
        'medium': ['cpc', 'social', 'organic'],
        'campaign': ['summer_sale', 'brand_awareness', '(not set)']
    }
    sessions_df = pd.DataFrame(sessions_data)
    sessions_df.to_csv('data/new/session_level_2025-07-02.csv', index=False)
    
    pipeline_logger.info("Created dummy files in data/new/ for processing.")


# --- 4. MAIN INGESTION PIPELINE ---

def run_ingestion_pipeline():
    """
    Main function to run the ingestion pipeline.
    Scans /data/new, validates files, appends to master tables, and moves processed files.
    """
    pipeline_logger.info("--- Starting Ingestion Pipeline Run ---")
    
    new_files_path = Path("data/new")
    processed_files_path = Path("data/processed")
    
    # Define master table paths
    master_orders_file = Path("data/master_orders.csv")
    master_sessions_file = Path("data/master_sessions.csv")
    
    files_to_process = list(new_files_path.glob('*.csv'))
    
    if not files_to_process:
        pipeline_logger.info("No new files found in data/new.")
        return

    for file_path in files_to_process:
        try:
            df = pd.read_csv(file_path)
            
            # Try to validate as order-line file
            processed_df = validate_and_process_order_lines(df, file_path.name)
            if processed_df is not None:
                # Append rows to the relevant master table
                header = not master_orders_file.exists()
                processed_df.to_csv(master_orders_file, mode='a', header=header, index=False)
                pipeline_logger.info(f"Appended {len(processed_df)} rows to {master_orders_file}.")
                shutil.move(file_path, processed_files_path / file_path.name)
                pipeline_logger.info(f"Moved processed file to {processed_files_path / file_path.name}")
                continue # Move to next file

            # Try to validate as session-level file
            processed_df = validate_and_process_sessions(df, file_path.name)
            if processed_df is not None:
                header = not master_sessions_file.exists()
                processed_df.to_csv(master_sessions_file, mode='a', header=header, index=False)
                pipeline_logger.info(f"Appended {len(processed_df)} rows to {master_sessions_file}.")
                shutil.move(file_path, processed_files_path / file_path.name)
                pipeline_logger.info(f"Moved processed file to {processed_files_path / file_path.name}")
                continue # Move to next file
            
            # If neither, log as unrecognized
            error_logger.warning(f"Unrecognized schema for file {file_path.name}. Moving to processed without action.")
            shutil.move(file_path, processed_files_path / file_path.name)

        except Exception as e:
            error_logger.error(f"Failed to process {file_path.name}: {e}")
            # Optionally move failed files to an 'error' directory instead
            # shutil.move(file_path, processed_files_path / 'error' / file_path.name)


    pipeline_logger.info("--- Finished Ingestion Pipeline Run ---")


if __name__ == '__main__':
    print("Setting up project structure...")
    setup_project_structure()
    
    print("Creating dummy files for demonstration...")
    create_dummy_files()
    
    print("Running ingestion pipeline...")
    run_ingestion_pipeline()
    
    print("\nPipeline run complete.")
    print("Check 'logs/pipeline.log' for actions and 'logs/data_errors.log' for skipped rows.")
    print("Processed files have been moved to 'data/processed/'.")
    print("Master data updated in 'data/master_orders.csv' and 'data/master_sessions.csv'.")