import pandas as pd
import numpy as np
import logging
from pathlib import Path

# --- 1. CONFIGURATION ---
# Configure logging to append to the main pipeline log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler() # Also print to console
    ]
)

# Define the output file for model metrics
METRICS_FILE = Path("model_metrics.txt")


def demonstrate_ltv_bootstrapping():
    """
    Demonstrates bootstrapping to create 95% confidence interval error bands
    for a Customer Lifetime Value (LTV) prediction, as per Task 8.5.
    """
    logging.info("--- Starting LTV Bootstrapping Demonstration ---")

    # --- 2. Create Sample LTV Data ---
    # In a real scenario, this DataFrame would be the output of your LTV model.
    # It contains the predicted LTV for each customer.
    np.random.seed(42)
    data = {
        'customer_id': [f'C{i}' for i in range(500)],
        'predicted_ltv': np.random.gamma(shape=2, scale=80, size=500) + 20
    }
    ltv_df = pd.DataFrame(data)
    
    logging.info(f"Created sample LTV data for {len(ltv_df)} customers.")

    # --- 3. Perform Bootstrapping ---
    n_iterations = 1000  # Number of bootstrap samples to create
    n_size = int(len(ltv_df)) # Size of each sample
    
    logging.info(f"Performing {n_iterations} bootstrap iterations...")
    
    # This list will store the mean LTV from each bootstrap sample
    bootstrapped_means = []
    
    for i in range(n_iterations):
        # Create a bootstrap sample by sampling with replacement
        sample = ltv_df['predicted_ltv'].sample(n=n_size, replace=True)
        
        # Calculate the mean LTV for this sample and store it
        bootstrapped_means.append(sample.mean())

    # Convert to a pandas Series for easy calculation
    bootstrapped_means = pd.Series(bootstrapped_means)

    # --- 4. Calculate Confidence Interval ---
    # The 95% confidence interval is found by taking the 2.5th and 97.5th percentiles
    # of the bootstrapped means distribution.
    confidence_level = 0.95
    lower_bound = bootstrapped_means.quantile( (1 - confidence_level) / 2 )
    upper_bound = bootstrapped_means.quantile( 1 - ( (1 - confidence_level) / 2 ) )
    
    # Calculate the point estimate (the mean of the original data)
    point_estimate_ltv = ltv_df['predicted_ltv'].mean()

    # --- 5. Log Results to File and Console ---
    logging.info("--- Bootstrapping Complete ---")
    
    result_text = (
        f"\n--- LTV Model Performance ---\n"
        f"Point Estimate (Average LTV): ${point_estimate_ltv:.2f}\n"
        f"95% Confidence Interval (Error Band): ${lower_bound:.2f} - ${upper_bound:.2f}\n"
    )
    
    print(result_text)
    
    try:
        with open(METRICS_FILE, "a") as f:
            f.write(result_text)
        logging.info(f"Successfully logged 95% CI to {METRICS_FILE}")
    except Exception as e:
        logging.error(f"Could not write to {METRICS_FILE}: {e}")


if __name__ == '__main__':
    demonstrate_ltv_bootstrapping()
