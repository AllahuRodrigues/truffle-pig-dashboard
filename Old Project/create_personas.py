import pandas as pd
import numpy as np

def create_persona_lookup_file():
    """
    Creates a dummy customer_personas.csv file for the dashboard.
    It uses the total number of new customers to generate realistic customer IDs.
    """
    try:
        # --- FIX: Load from a more appropriate source file ---
        # We'll use the new customer data to generate a realistic number of IDs.
        new_cust_df = pd.read_csv("cleaned_Cust By Channel-New.csv")
        
        # Calculate the total number of new customers to use for generating IDs
        total_new_customers = int(new_cust_df['value'].sum())
        
        if total_new_customers == 0:
            # Fallback if no customers are found
            total_new_customers = 100 # Default to 100 customers
            print("Warning: No new customers found in data. Generating 100 default IDs.")

        # Generate a list of unique customer IDs
        customer_ids = [f'cust_{1000+i}' for i in range(total_new_customers)]

        # We'll assign personas to a random subset of these customers (e.g., 80%)
        sample_size = int(total_new_customers * 0.8)
        sample_ids = np.random.choice(customer_ids, size=min(len(customer_ids), sample_size), replace=False)
        
        personas = ['High-Value VIP', 'Discount Seeker', 'New Shopper', 'Loyal Regular']
        
        persona_data = {
            'customer_id': sample_ids,
            'persona': np.random.choice(personas, size=len(sample_ids))
        }
        
        personas_df = pd.DataFrame(persona_data)
        
        file_path = "customer_personas.csv"
        personas_df.to_csv(file_path, index=False)
        
        print(f"Successfully created '{file_path}' with {len(personas_df)} rows.")
        print("Here's a sample of the data:")
        print(personas_df.head())

    except FileNotFoundError:
        print("Error: 'cleaned_Cust By Channel-New.csv' not found.")
        print("Please ensure the file is in the same directory to generate realistic persona mappings.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    create_persona_lookup_file()
