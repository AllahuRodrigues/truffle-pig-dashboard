import pandas as pd
import os
import re
import sys

# --- CONFIGURATION: UPDATE THESE FILENAMES ---
# IMPORTANT: Replace these with the exact names of your two Excel files.
FILE1_NAME = "Hp_data.xlsx"
FILE2_NAME = "Digital_duo.xlsx"
# --------------------------------------------

def clean_col_names(df):
    """Standardizes column names to snake_case."""
    df.columns = [re.sub(r'[\s\.\-\$]+', '_', str(col).lower()).strip('_') for col in df.columns]
    return df

def parse_currency(series):
    """Converts a currency string series to a float series."""
    series = series.astype(str).str.replace(r'[$,()]', '', regex=True)
    return pd.to_numeric(series, errors='coerce').fillna(0)

def melt_channel_df(df, value_name):
    """Melts a dataframe where columns are channels and rows are dates."""
    df = clean_col_names(df)
    if 'month' not in df.columns:
        date_col = next((col for col in df.columns if 'unnamed' in col), None)
        if date_col:
            df = df.rename(columns={date_col: 'month'})
        else: return None
            
    id_vars = ['month']
    value_vars = [col for col in df.columns if col not in id_vars and 'total' not in col]
    
    df_melted = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='channel', value_name=value_name)
    df_melted['month'] = pd.to_datetime(df_melted['month'], errors='coerce')
    return df_melted.dropna(subset=['month'])

print("--- Starting Data Preprocessing from Excel Files (v2) ---")

# Define paths
raw_data_path = 'raw_data'
output_path = 'preprocessed_data.csv'
file1_path = os.path.join(raw_data_path, FILE1_NAME)
file2_path = os.path.join(raw_data_path, FILE2_NAME)

# --- Load All Sheets from Both Excel Files ---
all_sheets = {}
try:
    print(f"Reading all tabs from '{FILE1_NAME}'...")
    all_sheets.update(pd.read_excel(file1_path, sheet_name=None, header=None))
    print(f"Reading all tabs from '{FILE2_NAME}'...")
    all_sheets.update(pd.read_excel(file2_path, sheet_name=None, header=None))
    print(f"Successfully loaded {len(all_sheets)} tabs in total.")
except FileNotFoundError as e:
    print(f"\nERROR: File not found - {e}.")
    sys.exit()
except Exception as e:
    print(f"\nAn error occurred: {e}. Please ensure 'openpyxl' is installed (`pip install openpyxl`).")
    sys.exit()

def get_df_by_keyword(keyword, header_keywords):
    """Finds a sheet by keyword, detects its header, and returns a clean DataFrame."""
    sheet_name = next((s for s in all_sheets if keyword.lower() in s.lower()), None)
    if not sheet_name:
        raise ValueError(f"Sheet containing '{keyword}' not found.")
    
    df_raw = all_sheets[sheet_name]
    header_row_index = -1
    for i, row in df_raw.iterrows():
        row_str = ' '.join(str(x) for x in row.values)
        if all(h.lower() in row_str.lower() for h in header_keywords):
            header_row_index = i
            break
            
    if header_row_index == -1:
        raise ValueError(f"Header for '{keyword}' sheet not found. Looked for: {header_keywords}")
    
    df = df_raw.iloc[header_row_index+1:].copy()
    df.columns = df_raw.iloc[header_row_index].values
    df.reset_index(drop=True, inplace=True)
    return df

try:
    print("Cleaning and reshaping data from each tab...")
    # Dynamically find and load each required sheet
    df_mcb = get_df_by_keyword('Marketing Channel Breakdown', ['Month', 'Orders', 'AOV'])
    df_ms = get_df_by_keyword('Media Spend', ['Spend', 'Impressions', 'Clicks'])
    df_cust_new = get_df_by_keyword('Cust By Channel-New', ['Paid Search', 'Paid Social'])
    df_cust_ext = get_df_by_keyword('Cust By Channel-Ext', ['Paid Search', 'Paid Social'])
    df_orders_new = get_df_by_keyword('Orders By Channel-New', ['Paid Search', 'Paid Social'])
    df_orders_ext = get_df_by_keyword('Orders By Channel-Ext', ['Paid Search', 'Paid Social'])
    df_returns = get_df_by_keyword('Returns', ['Returned $'])
    df_tech = get_df_by_keyword('Technology Spend', ['Technology', 'Spend'])
    df_web = get_df_by_keyword('Web Analytics', ['Source / Medium', 'Sessions'])

    # Clean and process as before
    df_mcb = clean_col_names(df_mcb).rename(columns={'marketing_channel': 'channel', 'revenue': 'total_revenue', 'orders': 'total_orders', 'spend': 'total_spend'})
    df_mcb['month'] = pd.to_datetime(df_mcb['month'])
    # ... continue with the rest of the script ...

    # The rest of the cleaning and merging logic remains the same
    df_ms = clean_col_names(df_ms).rename(columns={'spend_':'spend'})
    df_ms['month'] = pd.to_datetime(df_ms['month'])
    df_ms['spend'] = parse_currency(df_ms['spend'])
    
    df_returns = clean_col_names(df_returns)
    df_returns['month'] = pd.to_datetime(df_returns['month'])
    df_returns['returned'] = parse_currency(df_returns['returned'])
    
    df_tech = clean_col_names(df_tech)
    df_tech['month'] = pd.to_datetime(df_tech['month'])
    df_tech['spend'] = parse_currency(df_tech['spend'])
    df_tech_monthly = df_tech.groupby('month')['spend'].sum().reset_index().rename(columns={'spend': 'technology_spend'})
    
    df_web = clean_col_names(df_web).rename(columns={'source_medium': 'source'})
    df_web['month'] = pd.to_datetime(df_web['month'])
    channel_map = {'google / cpc': 'Paid Search', 'facebook / cpc': 'Paid Social', 'klaviyo / email': 'Email', '(direct) / (none)': 'Direct', 'tiktok / cpc': 'TikTok'}
    df_web['channel'] = df_web['source'].apply(lambda x: next((v for k, v in channel_map.items() if k in str(x).lower()), 'Other'))
    df_web_agg = df_web.groupby(['month', 'channel'])[['sessions', 'users']].sum().reset_index()

    # Melt data
    df_cust_new_melted = melt_channel_df(df_cust_new, 'new_customers')
    df_cust_ext_melted = melt_channel_df(df_cust_ext, 'existing_customers')
    df_orders_new_melted = melt_channel_df(df_orders_new, 'new_customer_orders')
    df_orders_ext_melted = melt_channel_df(df_orders_ext, 'existing_customer_orders')

    print("Merging into a single master file...")
    master_df = df_mcb.copy()
    data_to_merge = [df_cust_new_melted, df_cust_ext_melted, df_orders_new_melted, df_orders_ext_melted, df_web_agg, df_ms]

    for df in data_to_merge:
        if df is not None:
            master_df = pd.merge(master_df, df, on=['month', 'channel'], how='left')

    master_df = pd.merge(master_df, df_returns[['month', 'returned']], on='month', how='left')
    master_df = pd.merge(master_df, df_tech_monthly, on='month', how='left')
    
    numeric_cols = ['new_customers', 'existing_customers', 'new_customer_orders', 'existing_customer_orders', 'sessions', 'users', 'spend', 'impressions', 'clicks']
    for col in numeric_cols:
        if col in master_df.columns:
            master_df[col] = master_df[col].fillna(0)
            if master_df[col].dtype == 'object':
                 master_df[col] = parse_currency(master_df[col])
            master_df[col] = master_df[col].astype(int)

    master_df['revenue_share'] = master_df.groupby('month')['total_revenue'].transform(lambda x: x / x.sum())
    master_df['returns_value_dist'] = master_df['returned'] * master_df['revenue_share']
    master_df['technology_spend_dist'] = master_df['technology_spend'] * master_df['revenue_share']
    master_df['net_revenue'] = master_df['total_revenue'] - master_df['returns_value_dist']
    
    print("Finalizing columns and saving...")
    master_df.to_csv(output_path, index=False)
    print(f"\n--- SUCCESS! ---")
    print(f"Final preprocessed file has been saved to '{output_path}'.")

except (ValueError, KeyError, IndexError) as e:
    print(f"\nERROR during processing: {e}")
    print("This might be due to an unexpected sheet name or column structure. Please check your Excel files.")
    sys.exit()