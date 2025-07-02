import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def demonstrate_iterative_imputation():
    """
    Demonstrates how to use IterativeImputer to fill missing numeric values
    and flag the imputed rows, as per Task 8.2.
    """
    print("--- Demonstrating Iterative Imputation ---")
    
    # --- 1. Create Sample Data with Missing Values ---
    # We'll create a sample dataframe with some correlated columns and missing data.
    data = {
        'total_spend': [100, 150, np.nan, 200, 250, 300],
        'revenue': [500, 750, 800, 1000, np.nan, 1500],
        'new_customers': [10, 15, 16, 20, 25, np.nan],
        'channel': ['A', 'B', 'A', 'B', 'A', 'B'] # Non-numeric column
    }
    df = pd.DataFrame(data)
    print("\nOriginal DataFrame with missing values:")
    print(df)
    
    # --- 2. Apply IterativeImputer ---
    
    # Separate numeric columns for imputation
    numeric_cols = df.select_dtypes(include=np.number).columns
    df_numeric = df[numeric_cols]
    
    # Initialize the imputer
    # It will use a BayesianRidge model by default to predict missing values
    imputer = IterativeImputer(max_iter=10, random_state=0)
    
    # Fit and transform the data
    imputed_numeric_data = imputer.fit_transform(df_numeric)
    
    # Convert the result back to a DataFrame
    df_imputed_numeric = pd.DataFrame(imputed_numeric_data, columns=numeric_cols)
    
    # --- 3. Flag Imputed Rows and Combine Data ---
    
    # Create the 'imputed_bool' flag [cite: client said]
    # This flag is True for any row where a value was originally missing.
    df['imputed_bool'] = df.isnull().any(axis=1)
    
    # Combine the imputed numeric data with the original non-numeric data
    # and the new flag.
    df_final = df[['channel', 'imputed_bool']].copy()
    df_final[numeric_cols] = df_imputed_numeric
    
    print("\nDataFrame after Iterative Imputation:")
    print(df_final)
    
    print("\nNote the new 'imputed_bool' column and the filled NaN values.")
    

if __name__ == '__main__':
    demonstrate_iterative_imputation()
