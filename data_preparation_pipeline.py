import pandas as pd
import numpy as np
import pandera as pa
from pandera.errors import SchemaError
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from pathlib import Path
import logging

# --- 1. CONFIGURATION & SETUP ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define input and output paths
INPUT_DIR = Path(".") # Assumes cleaned files are in the current directory
OUTPUT_DIR = Path("data/analysis_ready")
OUTPUT_DIR.mkdir(exist_ok=True)

# --- 2. PANDERA SCHEMAS for Key DataFrames ---
# We'll define schemas for the most critical dataframes to ensure quality.
# This directly addresses Task 8.1

# Schema for the monthly trends data before it's used in charts
monthly_trends_schema = pa.DataFrameSchema({
    "date": pa.Column(pa.DateTime),
    "mapping_key": pa.Column(str, pa.Check.isin(['paid search', 'paid social', 'affiliates'])),
    "total_spend": pa.Column(float, pa.Check.greater_than_or_equal_to(0)),
    "net_revenue": pa.Column(float, pa.Check.greater_than_or_equal_to(0)),
    "monthly_roas": pa.Column(float),
    "monthly_cac": pa.Column(float)
})

# Schema for the final ROAS dataframe
roas_schema = pa.DataFrameSchema({
    "marketing_channel": pa.Column(str),
    "true_total_ad_spend": pa.Column(float, pa.Check.greater_than_or_equal_to(0)),
    "total_revenue": pa.Column(float),
    "corrected_roas": pa.Column(float)
})


# --- 3. DATA PROCESSING FUNCTIONS ---

def apply_iterative_imputation(df, numeric_cols):
    """
    Applies IterativeImputer to fill missing values in numeric columns
    and adds a boolean flag for imputed rows, as per Task 8.2.
    """
    df_numeric = df[numeric_cols]
    
    # Flag rows with missing data BEFORE imputing
    df['imputed_bool'] = df_numeric.isnull().any(axis=1)
    
    if df_numeric.isnull().sum().sum() > 0:
        logging.info(f"Applying IterativeImputer to columns: {numeric_cols}")
        imputer = IterativeImputer(max_iter=10, random_state=0)
        imputed_data = imputer.fit_transform(df_numeric)
        df[numeric_cols] = imputed_data
    
    return df

def prepare_final_data():
    """
    Loads all cleaned CSVs, applies validation and imputation, performs calculations,
    and saves the final, analysis-ready DataFrames.
    """
    try:
        logging.info("--- Starting Data Preparation Pipeline ---")
        
        # --- 4. LOAD ALL CLEANED DATA ---
        logging.info("Loading cleaned source files...")
        marketing_df = pd.read_csv(INPUT_DIR / "Cleaned_Marketing Channel Breakdown.csv")
        media_spend_df = pd.read_csv(INPUT_DIR / "cleaned_Media Spend by Channel.csv")
        topsheet_df = pd.read_csv(INPUT_DIR / "cleaned_TOPSHEET.csv")
        new_cust_df = pd.read_csv(INPUT_DIR / "cleaned_Cust By Channel-New.csv")
        ext_cust_df = pd.read_csv(INPUT_DIR / "cleaned_Cust By Channel-Ext.csv")
        
        # --- 5. DATA CLEANING & TRANSFORMATION ---
        # (This section contains the core logic from your dashboard's processing function)
        
        # Convert to datetime
        media_spend_df['date'] = pd.to_datetime(media_spend_df['date'])
        topsheet_df['date'] = pd.to_datetime(topsheet_df['date'])
        new_cust_df['date'] = pd.to_datetime(new_cust_df['date'])
        ext_cust_df['date'] = pd.to_datetime(ext_cust_df['date'])

        # Calculate Corrected ROAS
        agency_fees_df = media_spend_df[media_spend_df['channel_name'].str.contains("Agency", na=False, case=False)].copy()
        agency_fees_df['mapping_key'] = agency_fees_df['channel_name'].str.replace(" Agency", "", regex=True, case=False).str.lower().str.strip()
        agency_fees_df['mapping_key'] = agency_fees_df['mapping_key'].replace({'affiliate': 'affiliates'})
        total_agency_fees_agg = agency_fees_df.groupby('mapping_key')['value'].sum().reset_index()
        total_agency_fees_agg.rename(columns={'value': 'agency_fees'}, inplace=True)
        
        channel_summary = marketing_df.groupby('marketing_channel').agg(total_ad_spend=('ad_spend', 'sum'), total_revenue=('gross_discount_(shopify)', 'sum')).reset_index()
        channel_summary = pd.merge(channel_summary, total_agency_fees_agg, left_on='marketing_channel', right_on='mapping_key', how='left')
        channel_summary['agency_fees'] = channel_summary['agency_fees'].fillna(0)
        channel_summary['true_total_ad_spend'] = channel_summary['total_ad_spend'] + channel_summary['agency_fees']
        channel_summary['corrected_roas'] = channel_summary.apply(lambda row: row['total_revenue'] / row['true_total_ad_spend'] if row['true_total_ad_spend'] > 0 else 0, axis=1)
        roas_df = channel_summary.sort_values('corrected_roas', ascending=False).reset_index(drop=True)

        # Calculate Monthly Trends
        media_spend_df['channel_name'] = media_spend_df['channel_name'].str.lower().replace({'affiliate': 'affiliates'})
        direct_media_spend_df = media_spend_df[~media_spend_df['channel_name'].str.contains("agency", na=False, case=False)].copy()
        direct_media_spend_df['mapping_key'] = direct_media_spend_df['channel_name'].str.replace(" media", "", regex=True, case=False).str.lower().str.strip()
        monthly_spend = pd.merge(direct_media_spend_df, agency_fees_df[['date', 'mapping_key', 'value']], on=['date', 'mapping_key'], how='left', suffixes=('_media', '_agency'))
        monthly_spend['value_agency'] = monthly_spend['value_agency'].fillna(0)
        monthly_spend['total_spend'] = monthly_spend['value_media'] + monthly_spend['value_agency']
        
        monthly_revenue = topsheet_df[topsheet_df['metric'].str.contains("NET SALES -", na=False)].copy()
        monthly_revenue['mapping_key'] = monthly_revenue['metric'].str.replace("NET SALES - ", "", regex=False).str.strip().str.lower()
        
        monthly_performance = pd.merge(monthly_spend[['date', 'mapping_key', 'total_spend']], monthly_revenue[['date', 'mapping_key', 'value']], on=['date', 'mapping_key'], how='left')
        monthly_performance.rename(columns={'value': 'net_revenue'}, inplace=True)
        
        # --- 6. APPLY IMPUTATION (Task 8.2) ---
        # Impute missing values for net_revenue before calculating ROAS
        monthly_performance = apply_iterative_imputation(monthly_performance, ['net_revenue', 'total_spend'])
        
        monthly_performance['monthly_roas'] = monthly_performance.apply(lambda row: row['net_revenue'] / row['total_spend'] if row['total_spend'] > 0 else 0, axis=1)
        
        new_cust_df['mapping_key'] = new_cust_df['channel_name'].str.lower().replace({'affiliate': 'affiliates'})
        monthly_cac_df = pd.merge(monthly_spend[['date', 'mapping_key', 'total_spend']], new_cust_df[['date', 'mapping_key', 'value']], on=['date', 'mapping_key'], how='left')
        monthly_cac_df.rename(columns={'value': 'new_customers'}, inplace=True)
        monthly_cac_df = apply_iterative_imputation(monthly_cac_df, ['new_customers']) # Impute missing customer counts
        monthly_cac_df['monthly_cac'] = monthly_cac_df.apply(lambda row: row['total_spend'] / row['new_customers'] if row['new_customers'] > 0 else 0, axis=1)
        
        monthly_trends_df = pd.merge(monthly_performance, monthly_cac_df[['date', 'mapping_key', 'monthly_cac']], on=['date', 'mapping_key'], how='left')
        
        # --- 7. APPLY SCHEMA VALIDATION (Task 8.1) ---
        logging.info("Validating final dataframes with Pandera schemas...")
        try:
            roas_schema.validate(roas_df)
            logging.info("ROAS dataframe validation successful.")
            monthly_trends_schema.validate(monthly_trends_df[monthly_trends_df['mapping_key'].isin(['paid search', 'paid social', 'affiliates'])])
            logging.info("Monthly trends dataframe validation successful.")
        except SchemaError as e:
            logging.error(f"Final dataframe validation failed: {e}")
            # In a real pipeline, you might raise the error or handle it differently
            raise

        # --- 8. SAVE ANALYSIS-READY DATA ---
        logging.info(f"Saving analysis-ready files to {OUTPUT_DIR}...")
        roas_df.to_csv(OUTPUT_DIR / "final_roas.csv", index=False)
        monthly_trends_df.to_csv(OUTPUT_DIR / "final_monthly_trends.csv", index=False)
        # (Save other final dataframes as needed)

        logging.info("--- Data Preparation Pipeline Finished Successfully ---")

    except FileNotFoundError as e:
        logging.error(f"Error: A required input file was not found. Please check file paths. Details: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred in the pipeline: {e}")


if __name__ == '__main__':
    prepare_final_data()
