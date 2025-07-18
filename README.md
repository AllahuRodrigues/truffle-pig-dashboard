# 📊 ExcelDemocracy: Creative Performance Dashboard

**ExcelDemocracy** is a proof-of-concept project showcasing how creative performance data can be transformed into **clear, actionable KPIs** using mock data, machine learning, and interactive visualizations.

This project includes:
- 📦 A mock data generator  
- 🤖 A machine learning model for conversion prediction  
- 📈 An interactive **Streamlit dashboard** to visualize results like ROAS, CAC, Payback Period, and Lift Forecasts  

---

## 🔧 Key Components

| File/Script | Description |
|-------------|-------------|
| `mockdata2.py` | A **data factory** script that generates synthetic campaign, session, and order data (`CSV` format). |
| `jupyterfile.ipynb` | A **Jupyter Notebook** covering the entire ML workflow: data loading, feature engineering, Optuna hyperparameter tuning, and XGBoost model training. |
| `dashboards.py` | A **Streamlit app** offering an interactive dashboard for data exploration and predictive analytics. |
| `requirements.txt` | A list of all required **Python dependencies**. |
| `conversion_model.joblib` | The **trained XGBoost model**, ready for inference in the dashboard. |
| `model_features.joblib` | A saved list of **model features** used during training, ensuring consistency. |

---

## 🚀 How to Run the Project

Follow these steps to get the project running locally:

### 1. Install Dependencies  
Use pip to install all required libraries:

```bash
pip install -r requirements.txt
```

### 2. Generate Mock Data  
Run the mock data generator to create the required CSV files:

```bash
python mockdata2.py
```

This will create:
- `campaigns.csv`
- `sessions.csv`
- `orders.csv`

### 3. Train the Machine Learning Model  
Open the notebook and run all cells:

```bash
jupyter notebook jupyterfile.ipynb
```

This will:
- Train the conversion prediction model
- Save `conversion_model.joblib` and `model_features.joblib` for dashboard use

### 4. Launch the Dashboard  
Start the Streamlit app:

```bash
streamlit run dashboards.py
```

Your browser will automatically open the interactive dashboard 🎯

---

## 🗂 Project Structure

```
.
├── mockdata2.py               # Synthetic data generator
├── jupyterfile.ipynb          # ML workflow notebook
├── dashboards.py              # Streamlit dashboard
├── requirements.txt           # Python package list
├── campaigns.csv              # Generated mock data
├── sessions.csv               # Generated mock data
├── orders.csv                 # Generated mock data
├── conversion_model.joblib    # Trained XGBoost model
└── model_features.joblib      # Feature list used in training
```

---

## 📌 Features & KPIs Visualized
- ROAS (Return on Ad Spend)
- CAC (Customer Acquisition Cost)
- Payback Period
- Predictive Lift Forecast

---

## 📬 Feedback & Contributions  
This is a prototype project—feedback and contributions are welcome! If you’d like to suggest improvements or report bugs, feel free to open an issue or fork the repo.