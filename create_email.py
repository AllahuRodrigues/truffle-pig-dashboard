import pandas as pd
import numpy as np

def create_email_flow_performance_file():
    """
    Generates a dummy email_flow_performance.csv file with realistic data
    for different email campaigns over a period of time.
    """
    # --- 1. Define the structure and data parameters ---
    flow_names = ['Welcome Series', 'Abandoned Cart', 'Post-Purchase Follow-up', 'Win-back Campaign', 'Weekly Newsletter']
    
    # --- FIX: Corrected the function call ---
    # pd.date_range() already returns a datetime-like object, so no conversion is needed.
    # The original pd.to_date was also a typo for pd.to_datetime.
    date_range = pd.date_range(start='2024-01-01', end='2025-06-01', freq='W') # Weekly sends
    
    email_data = []

    # --- 2. Generate the data ---
    for date in date_range:
        for flow in flow_names:
            sends = np.random.randint(5000, 25000)
            
            # Simulate different performance levels for each flow type
            if 'Welcome' in flow:
                open_rate = np.random.uniform(0.30, 0.50)
                click_rate = np.random.uniform(0.05, 0.10) # Clicks on opens
                conversion_rate = np.random.uniform(0.03, 0.08) # Conversions on clicks
            elif 'Abandoned Cart' in flow:
                open_rate = np.random.uniform(0.40, 0.60)
                click_rate = np.random.uniform(0.10, 0.20)
                conversion_rate = np.random.uniform(0.08, 0.15)
            else: # Other campaigns
                open_rate = np.random.uniform(0.15, 0.25)
                click_rate = np.random.uniform(0.01, 0.04)
                conversion_rate = np.random.uniform(0.005, 0.02)
            
            opens = int(sends * open_rate)
            clicks = int(opens * click_rate)
            conversions = int(clicks * conversion_rate)
            
            # Assume an average order value between $50 and $80
            revenue = conversions * np.random.uniform(50, 80)
            
            email_data.append({
                'flow_name': flow,
                'send_date': date.strftime('%Y-%m-%d'),
                'sends': sends,
                'opens': opens,
                'clicks': clicks,
                'revenue': round(revenue, 2)
            })

    # --- 3. Create DataFrame and save to CSV ---
    email_df = pd.DataFrame(email_data)
    
    file_path = "email_flow_performance.csv"
    email_df.to_csv(file_path, index=False)
    
    print(f"Successfully created '{file_path}' with {len(email_df)} rows.")
    print("Here's a sample of the data:")
    print(email_df.head())

if __name__ == '__main__':
    create_email_flow_performance_file()
