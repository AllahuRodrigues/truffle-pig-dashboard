import os
import pandas as pd
import hashlib
import logging
import shutil
from pathlib import Path
import pandera as pa
from pandera.errors import SchemaError

# --- 1. LOGGING CONFIGURATION ---
Path("logs").mkdir(exist_ok=True)
pipeline_logger = logging.getLogger('PipelineLogger')
pipeline_logger.setLevel(logging.INFO)
if not pipeline_logger.handlers:
    pipeline_handler = logging.FileHandler('logs/pipeline.log')
    pipeline_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    pipeline_logger.addHandler(pipeline_handler)

error_logger = logging.getLogger('ErrorLogger')
error_logger.setLevel(logging.WARNING)
if not error_logger.handlers:
    error_handler = logging.FileHandler('logs/data_errors.log')
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    error_logger.addHandler(error_handler)

# --- 2. PANDERA SCHEMAS (Task 8.1, 2, 3) ---
order_schema = pa.DataFrameSchema(
    {
        "order_id": pa.Column(str, nullable=False),
        "customer_id": pa.Column(str, nullable=False),
        "order_datetime": pa.Column(pa.DateTime, coerce=True),
        "sku": pa.Column(str, nullable=False),
        "qty": pa.Column(int, checks=pa.Check.greater_than_or_equal_to(1), coerce=True),
        "unit_price": pa.Column(float, checks=pa.Check.greater_than_or_equal_to(0.0), coerce=True),
        "discount": pa.Column(float, coerce=True)
    },
    strict=False, # Allow extra columns but only validate specified ones
    ordered=False
)

session_schema = pa.DataFrameSchema(
    {
        "user_id": pa.Column(str, nullable=False),
        "session_id": pa.Column(str, nullable=False),
        "session_start": pa.Column(pa.DateTime, coerce=True),
        "source": pa.Column(str, nullable=False),
        "medium": pa.Column(str, nullable=False),
        "campaign": pa.Column(str, nullable=False)
    },
    strict=False,
    ordered=False
)

# --- 3. CORE FUNCTIONS ---
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

def validate_and_process_data(df, schema, file_name, is_session_file=False):
    """
    Validates a dataframe using a Pandera schema, logs errors, and returns valid rows.
    """
    initial_rows = len(df)
    try:
        # Validate the dataframe, collecting all errors
        validated_df = schema.validate(df, lazy=True)
        pipeline_logger.info(f"Validation successful for {file_name}. All {initial_rows} rows are valid.")
        
        if is_session_file:
            validated_df['user_id'] = validated_df['user_id'].apply(hash_user_id)
            pipeline_logger.info(f"Hashed user_id column for {file_name}.")
        
        return validated_df

    except SchemaError as err:
        error_logger.warning(f"Schema validation failed for {file_name} with {len(err.failure_cases)} failure cases.")
        
        # Log the specific failures
        error_logger.warning(f"Failure cases for {file_name}:\n{err.failure_cases.to_string()}")
        
        # Get the indexes of the rows that failed validation
        failed_indexes = err.failure_cases['index']
        
        # Keep only the rows that did NOT fail
        good_rows_df = df.drop(index=failed_indexes).copy()
        
        pipeline_logger.info(f"Kept {len(good_rows_df)}/{initial_rows} valid rows from {file_name}.")
        
        if is_session_file and not good_rows_df.empty:
            good_rows_df['user_id'] = good_rows_df['user_id'].apply(hash_user_id)
            pipeline_logger.info(f"Hashed user_id column for valid rows in {file_name}.")
            
        return good_rows_df

# --- 4. DUMMY DATA CREATION ---
def create_dummy_files():
    """Creates dummy CSV files with good and bad data for testing."""
    orders_data = {
        'order_id': ['1001', '1002', '1003', '1004', '1005', '1006'],
        'customer_id': ['cust_a', 'cust_b', None, 'cust_d', 'cust_e', 'cust_f'], # Bad: Null ID
        'order_datetime': pd.to_datetime(['2025-07-02 10:00', '2025-07-02 11:00', '2025-07-02 12:00', '2025-07-02 13:00', '2025-07-02 14:00', '2025-07-02 15:00']),
        'sku': ['SKU01', 'SKU02', 'SKU03', 'SKU04', 'SKU05', 'SKU06'],
        'qty': [2, 0, 5, 1, 3, 4], # Bad: qty < 1
        'unit_price': [10.0, 15.0, 20.0, -5.0, 30.0, 50.0], # Bad: price < 0
        'discount': [0.1, 0.0, 0.2, 0.0, 0.1, 0.15]
    }
    orders_df = pd.DataFrame(orders_data)
    orders_df.to_csv('data/new/order_lines_2025-07-03.csv', index=False)

    sessions_data = {
        'user_id': ['user1@example.com', 'user2@example.com', None, 'user4@example.com'], # Bad: Null user_id
        'session_id': ['sess001', 'sess002', 'sess003', 'sess004'],
        'session_start': ['2025-07-02 09:00', '2025-07-02 09:15', 'not_a_date', '2025-07-02 09:45'], # Bad: Invalid date
        'source': ['google', 'facebook', 'google', 'instagram'],
        'medium': ['cpc', 'social', 'organic', 'social'],
        'campaign': ['summer_sale', 'brand_awareness', '(not set)', 'q3_promo']
    }
    sessions_df = pd.DataFrame(sessions_data)
    sessions_df.to_csv('data/new/session_level_2025-07-03.csv', index=False)
    
    pipeline_logger.info("Created dummy files in data/new/ for processing.")

# --- 5. MAIN INGESTION PIPELINE ---
def run_ingestion_pipeline():
    """Main function to run the ingestion pipeline."""
    pipeline_logger.info("--- Starting Ingestion Pipeline Run (with Pandera Validation) ---")
    
    new_files_path = Path("data/new")
    processed_files_path = Path("data/processed")
    master_orders_file = Path("data/master_orders.csv")
    master_sessions_file = Path("data/master_sessions.csv")
    
    files_to_process = list(new_files_path.glob('*.csv'))
    
    if not files_to_process:
        pipeline_logger.info("No new files found in data/new.")
        return

    for file_path in files_to_process:
        try:
            df = pd.read_csv(file_path)
            
            # Identify file type based on columns
            if 'order_id' in df.columns:
                processed_df = validate_and_process_data(df, order_schema, file_path.name)
                if not processed_df.empty:
                    header = not master_orders_file.exists()
                    processed_df.to_csv(master_orders_file, mode='a', header=header, index=False)
                    pipeline_logger.info(f"Appended {len(processed_df)} rows to {master_orders_file}.")
            elif 'session_id' in df.columns:
                processed_df = validate_and_process_data(df, session_schema, file_path.name, is_session_file=True)
                if not processed_df.empty:
                    header = not master_sessions_file.exists()
                    processed_df.to_csv(master_sessions_file, mode='a', header=header, index=False)
                    pipeline_logger.info(f"Appended {len(processed_df)} rows to {master_sessions_file}.")
            else:
                error_logger.warning(f"Unrecognized schema for file {file_path.name}. Moving to processed without action.")
            
            shutil.move(file_path, processed_files_path / file_path.name)
            pipeline_logger.info(f"Moved processed file to {processed_files_path / file_path.name}")

        except Exception as e:
            error_logger.error(f"Failed to process {file_path.name}: {e}")

    pipeline_logger.info("--- Finished Ingestion Pipeline Run ---")

if __name__ == '__main__':
    print("Setting up project structure...")
    setup_project_structure()
    
    print("Creating dummy files for demonstration...")
    create_dummy_files()
    
    print("Running ingestion pipeline with Pandera validation...")
    run_ingestion_pipeline()
    
    print("\nPipeline run complete.")
    print("Check 'logs/pipeline.log' and 'logs/data_errors.log' for details.")
