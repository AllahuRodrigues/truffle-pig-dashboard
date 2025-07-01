import pandas as pd
import os
import re
import sys

# This final script is specifically designed to parse the complex, multi-column
# layout of your Email.csv report file by reading it line-by-line.

print("--- Starting Final Email Data Cleaning Script (v4) ---")

# --- 1. Setup Paths ---
raw_data_path = 'raw_data'
email_raw_filename = 'Email.csv'
output_path_email = 'email_data_clean.csv'

email_raw_path = os.path.join(raw_data_path, email_raw_filename)

if not os.path.exists(email_raw_path):
    print(f"\nERROR: The file '{email_raw_filename}' was not found in the 'raw_data' folder.")
    sys.exit()

# --- 2. Parse the Complex Report Format Line by Line ---
try:
    print(f"Reading and parsing '{email_raw_filename}' line by line...")
    
    with open(email_raw_path, 'r', encoding='latin1') as f:
        lines = f.readlines()

    all_data = []

    for line in lines:
        # Split the line by any whitespace
        parts = line.split()
        
        # A valid data line will contain 'Campaign' and 'Flow' and be long enough
        if 'Campaign' in parts and 'Flow' in parts and len(parts) > 10:
            try:
                # Find indices of the keywords
                campaign_idx = parts.index('Campaign')
                flow_idx = parts.index('Flow')

                # Extract Campaign data based on position relative to the keyword
                campaign_year = parts[campaign_idx - 2]
                campaign_month = parts[campaign_idx - 1]
                campaign_sends = parts[campaign_idx + 1]
                campaign_clicks = parts[campaign_idx + 2]
                all_data.append(['Campaigns', campaign_year, campaign_month, campaign_sends, campaign_clicks])

                # Extract Flow data based on position relative to the keyword
                flow_year = parts[flow_idx - 2]
                flow_month = parts[flow_idx - 1]
                flow_sends = parts[flow_idx + 1]
                flow_clicks = parts[flow_idx + 2]
                all_data.append(['Flows', flow_year, flow_month, flow_sends, flow_clicks])

            except (ValueError, IndexError):
                # Skip lines that look like data lines but are malformed
                continue

    # Create a DataFrame from all the extracted data
    df_email_processed = pd.DataFrame(all_data, columns=['type', 'year', 'month', 'sends', 'clicks'])

    # --- 3. Clean and Aggregate ---
    # Clean numeric columns
    for col in ['sends', 'clicks']:
        df_email_processed[col] = df_email_processed[col].astype(str).str.replace(',', '', regex=False)
        df_email_processed[col] = pd.to_numeric(df_email_processed[col], errors='coerce').fillna(0)
    
    # NOTE: Revenue and Conversions are not in the source file, so they will be 0.
    df_email_processed['revenue'] = 0
    df_email_processed['conversions'] = 0
    
    numeric_cols = ['sends', 'clicks', 'conversions', 'revenue']
    df_email_agg = df_email_processed.groupby('type')[numeric_cols].sum().reset_index()

    # Calculate final KPIs
    df_email_agg['ctr'] = (df_email_agg['clicks'] / df_email_agg['sends'].replace(0,1)) * 100
    df_email_agg['cvr_from_clicks'] = (df_email_agg['conversions'] / df_email_agg['clicks'].replace(0,1)) * 100
    df_email_agg['revenue_per_send'] = df_email_agg['revenue'] / df_email_agg['sends'].replace(0,1)

    df_email_agg.to_csv(output_path_email, index=False)
    print(f"\n✅ SUCCESS: Email data processing complete. Saved '{output_path_email}'.")

except Exception as e:
    print(f"\nERROR processing email data: {e}")
