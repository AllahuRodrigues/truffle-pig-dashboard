import pandas as pd
import numpy as np
import optuna
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score

def create_sample_data():
    """Creates a sample time-series DataFrame for the demonstration."""
    dates = pd.to_datetime(pd.date_range(start='2024-01-01', periods=200, freq='D'))
    data = {
        'activity_date': dates,
        'days_since_last_purchase': np.random.randint(1, 90, size=200),
        'total_spent': np.random.uniform(50, 1000, size=200),
        'session_count': np.random.randint(1, 50, size=200),
        'churned': np.random.randint(0, 2, size=200)
    }
    df = pd.DataFrame(data).sort_values('activity_date')
    return df

def objective(trial, X, y):
    """
    The objective function for Optuna to optimize.
    It trains an XGBoost model using parameters suggested by the 'trial' object
    and returns the average cross-validated AUC score.
    """
    # --- 1. Define the hyperparameter search space ---
    # Optuna will suggest values from these ranges for each trial.
    param = {
        'objective': 'binary:logistic',
        'eval_metric': 'auc',
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 9),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'gamma': trial.suggest_float('gamma', 0, 5),
        'random_state': 42
    }
    
    # --- 2. Use TimeSeriesSplit for robust cross-validation ---
    n_splits = 5
    tscv = TimeSeriesSplit(n_splits=n_splits)
    
    scores = []
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        model = xgb.XGBClassifier(**param)
        model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        
        preds = model.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, preds)
        scores.append(auc_score)
        
    # Optuna will try to maximize this value
    return np.mean(scores)


if __name__ == "__main__":
    print("--- Running Hyperparameter Tuning with Optuna and TimeSeriesSplit ---")
    
    # Create sample data
    df = create_sample_data()
    X = df[['days_since_last_purchase', 'total_spent', 'session_count']]
    y = df['churned']
    
    # --- 3. Create and run the Optuna study ---
    # We want to 'maximize' the AUC score.
    study = optuna.create_study(direction='maximize')
    
    # Run the optimization process. n_trials determines how many different
    # hyperparameter combinations to test.
    study.optimize(lambda trial: objective(trial, X, y), n_trials=50)
    
    # --- 4. Print the results ---
    print("\n--- Tuning Complete ---")
    print(f"Number of finished trials: {len(study.trials)}")
    print("\nBest trial:")
    trial = study.best_trial
    
    print(f"  Value (Best CV AUC): {trial.value:.4f}")
    
    print("  Best Parameters: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")

