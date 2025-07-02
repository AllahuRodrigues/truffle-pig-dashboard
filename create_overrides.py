import pandas as pd
import numpy as np

def create_spend_overrides_file():
    """
    Generates a CSV file with dummy spend data for specified agency channels
    for every month of 2022 and 2023.
    """
    # --- 1. Define the structure and date range ---
    channels = ['Paid Search Agency', 'Paid Social Agency', 'Affiliate Agency']
    
    # Create a date range for every month in 2022 and 2023
    date_range = pd.date_range(start='2022-01-01', end='2023-12-01', freq='MS')
    
    # --- 2. Generate the data ---
    override_data = []
    
    # Define plausible spend ranges for each channel
    spend_ranges = {
        'Paid Search Agency': (8000, 20000),
        'Paid Social Agency': (100000, 250000),
        'Affiliate Agency': (40000, 75000)
    }
    
    for date in date_range:
        for channel in channels:
            min_spend, max_spend = spend_ranges[channel]
            # Generate a random spend value within the defined range
            spend = np.random.randint(min_spend, max_spend)
            
            override_data.append({
                'month': date.strftime('%Y-%m-%d'),
                'channel': channel,
                'spend_override': spend
            })
            
    # --- 3. Create DataFrame and save to CSV ---
    overrides_df = pd.DataFrame(override_data)
    
    # Save the file
    file_path = "spend_overrides.csv"
    overrides_df.to_csv(file_path, index=False)
    
    print(f"Successfully created '{file_path}' with {len(overrides_df)} rows.")
    print("Here's a sample of the data:")
    print(overrides_df.head())

if __name__ == '__main__':
    create_spend_overrides_file()

