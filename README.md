DTC Analytics & Profitability Dashboard
This project provides an interactive Streamlit dashboard for analyzing marketing channel performance, customer behavior, and profitability for a direct-to-consumer business. It includes a robust data pipeline for ingesting and validating new data, as well as advanced model training and evaluation features.

Project Structure
/data: Contains master data tables and staging areas.

/new: Staging area for new, unprocessed CSV files (e.g., order_lines_..., session_level_...).

/processed: Archive for files that have been successfully ingested by the pipeline.

/analysis_ready: Contains the final, cleaned, and validated data tables ready for use by the dashboard and notebooks.

/logs: Contains loge for read pipeline actions (pipeline.log)boar core quality errors (data_errors.log).

/exports: (Optional) Directory for automated exports of KPIs and charts.

ingestion_pipeline.py: A utility script that watchesd it /data/new foldern i.

/Main Dashboard.py: Actual File for dashboard visualization