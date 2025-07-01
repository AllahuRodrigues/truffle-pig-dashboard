import pandas as pd
import os
import glob
import re
import sys

def clean_col_names(df):
    """Standardizes column names to snake_case."""
    # Cleans column names to make them valid Python identifiers.
    df.columns = [re.sub(r'[\s\.\-\$]+', '_', str(col).lower()).strip('_') for col in df.columns]
    return df

def parse_currency(series):
    """Converts a currency string series to a float series, handling $, commas, and parentheses."""
    series = series.astype(str).str.replace(r'[$,()]', '', regex=True)
    return pd.to_numeric(series, errors='coerce').fillna(0)

def melt_channel_df(df, value_name):
    """
    Reshapes data from wide (channels as columns) to long format.
    This handles files like 'Cust By Channel'.
    """
    df = clean_col_names(df)
    # The first column is always the date column, whatever its original name.
    df = df.rename(columns={df.columns[0]: 'month'})
    
    # This handles non-date text like summary rows in the date column.
    df['month'] = pd.to_datetime(df['month'], errors='coerce')
    df.dropna(subset=['month'], inplace=True)
    
    id_vars = ['month']
    value_vars = [col for col in df.columns if col not in id_vars and 'total' not in col]
    
    df_melted = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='channel', value_name=value_name)
    return df_melted.dropna(subset=['month'])

print("--- Starting Final Data Preprocessing Script ---")

# --- 1. Load All Raw CSV Files ---
raw_data_path = 'raw_data'
output_path = 'preprocessed_data.csv'

if not os.path.exists(raw_data_path) or not os.listdir(raw_data_path):
    print(f"\nERROR: The 'raw_data' folder is missing or empty.")
    sys.exit()

all_files = glob.glob(os.path.join(raw_data_path, "*.csv"))
print(f"Found {len(all_files)} CSV files in 'raw_data' folder.")

dfs = {}
try:
    for f in all_files:
        key = os.path.basename(f).lower().replace('.csv', '')
        # FIX: Use 'latin1' encoding to prevent UnicodeDecodeError, common with Excel exports.
        dfs[key] = pd.read_csv(f, thousands=',', encoding='latin1')
except Exception as e:
    print(f"\nERROR during file loading: {e}")
    sys.exit()

# --- 2. Clean and Reshape Each File Individually ---
try:
    print("Cleaning and reshaping each data file...")
    # Find dataframes by keywords in their filenames for robustness
    df_mcb = next(df.copy() for key, df in dfs.items() if 'marketing channel breakdown' in key)
    df_ms = next(df.copy() for key, df in dfs.items() if 'media spend' in key and 'by channel' not in key)
    df_cust_new = next(df.copy() for key, df in dfs.items() if 'cust by channel-new' in key)
    df_cust_ext = next(df.copy() for key, df in dfs.items() if 'cust by channel-ext' in key)
    df_orders_new = next(df.copy() for key, df in dfs.items() if 'orders by channel-new' in key)
    df_orders_ext = next(df.copy() for key, df in dfs.items() if 'orders by channel-ext' in key)
    df_returns = next(df.copy() for key, df in dfs.items() if 'returns' in key)
    df_tech = next(df.copy() for key, df in dfs.items() if 'technology spend' in key)
    df_web = next(df.copy() for key, df in dfs.items() if 'web analytics' in key and '2' not in key)

    # Process all dataframes with error handling for dates and names
    for df in [df_mcb, df_ms, df_returns, df_tech, df_web]:
        df = clean_col_names(df)
        df.rename(columns={df.columns[0]: 'month'}, inplace=True)
        df['month'] = pd.to_datetime(df['month'], errors='coerce')
        df.dropna(subset=['month'], inplace=True)

    # Melt channel-based files
    df_cust_new_melted = melt_channel_df(df_cust_new, 'new_customers')
    df_cust_ext_melted = melt_channel_df(df_cust_ext, 'existing_customers')
    df_orders_new_melted = melt_channel_df(df_orders_new, 'new_customer_orders')
    df_orders_ext_melted = melt_channel_df(df_orders_ext, 'existing_customer_orders')
    
    # Specific cleaning for Web Analytics
    df_web.rename(columns={'source_medium': 'source'}, inplace=True)
    channel_map = {'google / cpc': 'Paid Search', 'facebook / cpc': 'Paid Social', 'klaviyo / email': 'Email', '(direct) / (none)': 'Direct', 'tiktok / cpc': 'TikTok', 'shareasale / affiliate': 'Affiliate', 'organic': 'Organic Social'}
    df_web['channel'] = df_web['source'].apply(lambda x: next((v for k, v in channel_map.items() if k in str(x).lower()), 'Other'))
    
    # --- 3. Aggregate Data to Prevent Duplicate Keys ---
    print("Aggregating data to ensure unique keys...")
    
    # FIX: Aggregate data *before* merging to resolve "duplicate keys" error.
    df_mcb_agg = df_mcb.groupby(['month', 'channel']).sum().reset_index()
    df_ms_agg = df_ms.groupby(['month', 'channel']).sum().reset_index()
    df_web_agg = df_web.groupby(['month', 'channel'])[['sessions', 'users']].sum().reset_index()
    
    df_tech_monthly = df_tech.groupby('month')[df_tech.columns[1]].sum().reset_index().rename(columns={df_tech.columns[1]: 'technology_spend'})
    df_returns_monthly = df_returns.groupby('month')[df_returns.columns[2]].sum().reset_index().rename(columns={df_returns.columns[2]: 'returned_value'})

    # --- 4. Merge All DataFrames ---
    print("Merging all data sources into a single master file...")
    master_df = df_mcb_agg.copy()
    data_to_merge = [
        df_cust_new_melted, df_cust_ext_melted, df_orders_new_melted, 
        df_orders_ext_melted, df_web_agg, df_ms_agg
    ]

    for df in data_to_merge:
        if df is not None:
            group_cols = ['month', 'channel']
            agg_cols = {col: 'sum' for col in df.columns if col not in group_cols}
            df_agg = df.groupby(group_cols).agg(agg_cols).reset_index()
            master_df = pd.merge(master_df, df_agg, on=['month', 'channel'], how='left')

    master_df = pd.merge(master_df, df_returns_monthly, on='month', how='left')
    master_df = pd.merge(master_df, df_tech_monthly, on='month', how='left')
    
    # --- 5. Final Calculations and Cleanup ---
    print("Performing final calculations...")
    master_df.fillna(0, inplace=True)
    
    # Convert appropriate columns to integer
    int_cols = ['new_customers', 'existing_customers', 'new_customer_orders', 'existing_customer_orders', 'sessions', 'users', 'impressions', 'clicks']
    for col in int_cols:
        if col in master_df.columns:
            master_df[col] = master_df[col].astype(int)

    master_df['revenue_share'] = master_df.groupby('month')['total_revenue'].transform(lambda x: x / (x.sum() if x.sum() != 0 else 1))
    master_df['returns_value_dist'] = master_df['returned_value'] * master_df['revenue_share']
    master_df['net_revenue'] = master_df['total_revenue'] - master_df['returns_value_dist']

    print("Saving final preprocessed file...")
    master_df.to_csv(output_path, index=False)
    
    print(f"\n--- SUCCESS! ---")
    print(f"Preprocessing is complete. The final file 'preprocessed_data.csv' has been created.")

except Exception as e:
    print(f"\nERROR during processing: {e}")
    print("Please ensure your 13 CSV files are in the 'raw_data' folder.")
    sys.exit()