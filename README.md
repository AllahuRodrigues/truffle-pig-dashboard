# DTC Analytics & Profitability Dashboard

This project provides an interactive **Streamlit dashboard** for analyzing marketing channel performance, customer behavior, and profitability for a direct-to-consumer business. It includes a robust data pipeline for ingesting and validating new data, as well as advanced model training and evaluation features.

---

## 📁 Project Structure

```
/data
    /new                # Staging area for new, unprocessed CSV files (e.g., order_lines_..., session_level_...)
    /processed          # Archive for files that have been successfully ingested by the pipeline
    /analysis_ready     # Final, cleaned, and validated data tables ready for dashboard and notebooks
    /logs               # Log files for pipeline actions (pipeline.log) and data quality errors (data_errors.log)
    /exports            # (Optional) Automated exports of KPIs and charts
ingestion_pipeline.py   # Watches /data/new to process and validate new raw data feeds
data_preparation_pipeline.py # Loads, validates, and prepares analysis-ready data
Analysis Phase.ipynb    # Jupyter Notebook for advanced model training (Churn/LTV)
dashboard.py            # Main Streamlit app for interactive data visualization
requirements.txt        # Python dependencies
spend_overrides.csv     # Patch historical spend data gaps
customer_personas.csv   # Map customers to personas
email_flow_performance.csv # Analyze email campaign performance
```

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.8+ installed on your system.

### 1. Create a Virtual Environment (Recommended)

```bash
# Create the virtual environment
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Project

### Step 1: Prepare the Data

Run the data preparation pipeline to clean, validate, and prepare the data:

```bash
python data_preparation_pipeline.py
```

This will generate the final data tables in the `/data/analysis_ready/` directory.

---

### Step 2: Run the Interactive Dashboard

Launch the Streamlit dashboard:

```bash
streamlit run dashboard.py
```

The application will open in your default web browser.  
**Use the sidebar to upload the required `cleaned_*.csv` files to populate the charts.**

---

### (Optional) Step 3: Process New Raw Data

When you receive new raw data files (e.g., from client partners):

1. Place the new Order-line or Session-level CSV files into the `/data/new/` directory.
2. Run the ingestion pipeline script:

    ```bash
    python ingestion_pipeline.py
    ```

3. After the script runs, **re-run** `data_preparation_pipeline.py` (Step 1) to incorporate the new data into your main analysis.

---

Enjoy analyzing your DTC business with actionable insights!