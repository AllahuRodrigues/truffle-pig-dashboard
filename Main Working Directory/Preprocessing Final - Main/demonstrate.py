import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def demonstrate_timeseries_cv():
    """
    Demonstrates the use of TimeSeriesSplit for cross-validation to avoid
    look-ahead bias in time-dependent data, as per Task 8.3.
    """
    print("--- Demonstrating TimeSeriesSplit for Cross-Validation ---")

    # --- 1. Create Sample Time-Series Data ---
    # Imagine we have customer data over 12 months.
    # We want to predict if a customer will churn in the next month.
    dates = pd.to_datetime(pd.date_range(start='2024-01-01', periods=100, freq='D'))
    data = {
        'activity_date': dates,
        'customer_id': [f'C{i}' for i in range(100)],
        'days_since_last_purchase': np.random.randint(1, 90, size=100),
        'total_spent': np.random.uniform(50, 1000, size=100),
        'churned': np.random.randint(0, 2, size=100) # Target variable
    }
    df = pd.DataFrame(data).sort_values('activity_date')
    
    print(f"\nSample DataFrame created with {len(df)} records.")
    
    X = df[['days_since_last_purchase', 'total_spent']]
    y = df['churned']

    # --- 2. Set up TimeSeriesSplit ---
    # We'll create 5 splits. Each split uses more training data than the last.
    n_splits = 5
    tscv = TimeSeriesSplit(n_splits=n_splits)
    
    print(f"\nInitialized TimeSeriesSplit with {n_splits} splits.")
    print("Each 'fold' trains on past data and tests on future data.\n")

    # --- 3. Loop Through Splits and Train a Model ---
    fold_number = 1
    accuracies = []

    for train_index, test_index in tscv.split(X):
        # Get the training and testing sets for this fold
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        print(f"--- Fold {fold_number} ---")
        print(f"Train data size: {len(X_train)} records (from index {train_index[0]} to {train_index[-1]})")
        print(f"Test data size:  {len(X_test)} records (from index {test_index[0]} to {test_index[-1]})")
        
        # Train a simple model
        model = LogisticRegression()
        model.fit(X_train, y_train)
        
        # Make predictions and evaluate
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        accuracies.append(accuracy)
        
        print(f"Fold {fold_number} Accuracy: {accuracy:.2f}\n")
        fold_number += 1
        
    print("--- Cross-Validation Complete ---")
    print(f"Average Accuracy across all folds: {np.mean(accuracies):.2f}")

if __name__ == '__main__':
    demonstrate_timeseries_cv()
