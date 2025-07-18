import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import xgboost as xgb
import joblib
from pathlib import Path

# --- App Configuration ---
st.set_page_config(
    page_title="ExcelDemocracy | Creative Performance Dashboard",
    page_icon="💡",
    layout="wide"
)

# --- Caching Functions for Performance ---
@st.cache_data
def load_data():
    """Loads and preprocesses the mock data files from the local directory."""
    try:
        sessions_df = pd.read_csv('sessions.csv')
        campaigns_df = pd.read_csv('campaigns.csv')
        orders_df = pd.read_csv('orders.csv')

        # Convert date columns
        sessions_df['session_start'] = pd.to_datetime(sessions_df['session_start'])
        campaigns_df['start_date'] = pd.to_datetime(campaigns_df['start_date'])
        orders_df['order_datetime'] = pd.to_datetime(orders_df['order_datetime'])

        # Merge campaign info into sessions
        data_df = pd.merge(sessions_df, campaigns_df, on='campaign_id', how='left')

        # Attribute revenue to the specific session that converted
        # This is a simplified last-touch attribution model
        order_attribution = pd.merge(orders_df, sessions_df[['session_id', 'user_id', 'session_start']], on='user_id')
        order_attribution = order_attribution[order_attribution['order_datetime'] >= order_attribution['session_start']]
        
        order_attribution['time_diff'] = order_attribution['order_datetime'] - order_attribution['session_start']
        # Get the session that occurred most recently before the order
        order_attribution = order_attribution.loc[order_attribution.groupby(['user_id', 'order_id'])['time_diff'].idxmin()]
        
        session_revenue = order_attribution.groupby('session_id')['gross_revenue'].sum().reset_index()

        # Merge revenue back to the main dataframe
        data_df = pd.merge(data_df, session_revenue, on='session_id', how='left')
        data_df['gross_revenue'].fillna(0, inplace=True)
        
        return data_df, campaigns_df, orders_df
        
    except FileNotFoundError as e:
        st.error(f"❌ **Error:** A required data file was not found: `{e.filename}`. Please run the `mockdata2.py` script first, then the Jupyter Notebook.")
        return None, None, None
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return None, None, None

@st.cache_resource
def load_model_and_features():
    """
    Loads the pre-trained XGBoost model and feature list from disk.
    These files are created by the Jupyter Notebook.
    """
    model_path = Path("conversion_model.joblib")
    features_path = Path("model_features.joblib")

    if not model_path.exists() or not features_path.exists():
        st.error(f"❌ **Error:** Model files (`{model_path}`, `{features_path}`) not found. Please run the `jupyterfile.ipynb` notebook to train and save the model first.")
        return None, None

    model = joblib.load(model_path)
    features = joblib.load(features_path)
    return model, features

# --- Main Dashboard UI ---
st.title("💡 ExcelDemocracy | Creative Performance Dashboard")
st.markdown("A proof-of-concept dashboard analyzing the impact of creative assets on marketing KPIs.")

data_df, campaigns_df, orders_df = load_data()

if data_df is not None:
    # --- Sidebar Filters ---
    with st.sidebar:
        st.header("Filters")
        
        # Ensure date inputs are valid
        min_date = data_df['session_start'].min().date()
        max_date = data_df['session_start'].max().date()
        
        date_range = st.date_input(
            "Select Date Range", 
            (min_date, max_date), 
            min_value=min_date, 
            max_value=max_date
        )

        ad_formats = ['All'] + campaigns_df['creative_format'].dropna().unique().tolist()
        selected_formats = st.multiselect("Ad Format", ad_formats, default=['All'])

        themes = ['All'] + campaigns_df['creative_theme'].dropna().unique().tolist()
        selected_themes = st.multiselect("Creative Theme", themes, default=['All'])

    # Filter data based on sidebar selections
    start_date, end_date = date_range
    filtered_df = data_df[
        (data_df['session_start'].dt.date >= start_date) &
        (data_df['session_start'].dt.date <= end_date)
    ]
    if 'All' not in selected_formats:
        filtered_df = filtered_df[filtered_df['creative_format'].isin(selected_formats)]
    if 'All' not in selected_themes:
        filtered_df = filtered_df[filtered_df['creative_theme'].isin(selected_themes)]


    # --- Main Content Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 ROAS & CAC Analysis", "📈 Payback Curve", "🚀 Lift Forecast", "🧠 Model Insights"])

    with tab1:
        st.header("ROAS & CAC per Creative Tag")
        
        if not filtered_df.empty:
            # Correctly get unique campaign spend from the filtered data to avoid double-counting
            relevant_campaigns = filtered_df[['campaign_id', 'spend', 'creative_format', 'creative_theme']].drop_duplicates()
            
            # Aggregate revenue and conversions from the filtered sessions
            session_summary = filtered_df.groupby('campaign_id').agg(
                total_revenue=('gross_revenue', 'sum'),
                total_conversions=('converted', 'sum')
            ).reset_index()
            
            campaign_summary = pd.merge(relevant_campaigns, session_summary, on='campaign_id')

            # Aggregate by creative tags
            creative_summary = campaign_summary.groupby(['creative_format', 'creative_theme']).agg(
                total_spend=('spend', 'sum'),
                total_revenue=('total_revenue', 'sum'),
                total_conversions=('total_conversions', 'sum')
            ).reset_index()

            creative_summary['roas'] = creative_summary.apply(lambda r: r['total_revenue'] / r['total_spend'] if r['total_spend'] > 0 else 0, axis=1)
            creative_summary['cac'] = creative_summary.apply(lambda r: r['total_spend'] / r['total_conversions'] if r['total_conversions'] > 0 else 0, axis=1)

            # --- NEW: Add a more detailed treemap visualization ---
            st.subheader("Detailed Performance Breakdown")
            st.markdown("Use this treemap to explore performance. The **size** of each rectangle represents total revenue, and the **color** represents ROAS.")
            
            # Ensure no zero or negative values for the color scale
            creative_summary['roas_display'] = creative_summary['roas'].clip(lower=0.01)

            fig_treemap = px.treemap(
                creative_summary,
                path=[px.Constant("All Creatives"), 'creative_theme', 'creative_format'],
                values='total_revenue',
                color='roas_display',
                color_continuous_scale='RdYlGn',
                # FIX: Use customdata and a hovertemplate for cleaner tooltips that avoid showing NaN for parent nodes.
                custom_data=['roas', 'cac', 'total_spend'],
                title='Revenue and ROAS by Creative Theme & Format'
            )
            # This template shows ROAS, CAC etc. only for the lowest-level items (leaves)
            fig_treemap.update_traces(
                textinfo="label+value+percent parent",
                hovertemplate='<b>%{label}</b><br><br>Total Revenue: %{value:$,.0f}<br>ROAS: %{customdata[0]:.2f}<br>CAC: %{customdata[1]:$,.2f}<br>Spend: %{customdata[2]:$,.0f}<extra></extra>'
            )
            st.plotly_chart(fig_treemap, use_container_width=True)


            st.subheader("Summary by Creative Format")
            col1, col2 = st.columns(2)
            with col1:
                fig_format = px.bar(creative_summary, x='creative_format', y='roas', color='creative_format', title="ROAS by Creative Format", labels={'roas': 'Return on Ad Spend'})
                st.plotly_chart(fig_format, use_container_width=True)
            with col2:
                fig_cac_format = px.bar(creative_summary, x='creative_format', y='cac', color='creative_format', title="CAC by Creative Format", labels={'cac': 'Customer Acquisition Cost ($)'})
                st.plotly_chart(fig_cac_format, use_container_width=True)

            st.dataframe(creative_summary.sort_values('roas', ascending=False))
        else:
            st.warning("No data available for the selected filters.")

    with tab2:
        st.header("Payback Curve per Campaign")
        
        selected_campaign = st.selectbox("Select a Campaign to Analyze", campaigns_df['campaign_name'].unique())
        
        campaign_info = campaigns_df[campaigns_df['campaign_name'] == selected_campaign]
        if not campaign_info.empty:
            campaign_spend = campaign_info['spend'].iloc[0]
            campaign_start_date = campaign_info['start_date'].iloc[0]
            campaign_id = campaign_info['campaign_id'].iloc[0]
            
            # Filter sessions to the specific campaign, after its launch date
            campaign_sessions = filtered_df[
                (filtered_df['campaign_id'] == campaign_id) & 
                (filtered_df['session_start'] >= campaign_start_date)
            ].sort_values('session_start')
            
            if not campaign_sessions.empty and campaign_sessions['gross_revenue'].sum() > 0:
                campaign_sessions['cumulative_revenue'] = campaign_sessions['gross_revenue'].cumsum()
                campaign_sessions['days_since_launch'] = (campaign_sessions['session_start'] - campaign_start_date).dt.days

                fig_payback = px.line(campaign_sessions, x='days_since_launch', y='cumulative_revenue', title=f"Payback Curve for {selected_campaign}", labels={'cumulative_revenue': 'Cumulative Revenue ($)'})
                fig_payback.add_hline(y=campaign_spend, line_dash="dash", line_color="red", annotation_text="Total Spend")
                st.plotly_chart(fig_payback, use_container_width=True)
            else:
                st.warning("No revenue data available for this campaign in the selected date range.")
        else:
            st.error("Selected campaign not found.")

    with tab3:
        st.header("Lift Forecast")
        st.markdown("Use our conversion model to predict the incremental lift from a budget increase.")

        model, features = load_model_and_features()
        
        if model and features:
            # Use a representative sample from the filtered data for forecasting
            if not filtered_df.empty:
                forecast_sample = filtered_df.sample(min(len(filtered_df), 10000), random_state=1)
                
                # Feature Engineering on the sample
                forecast_sample['hour_of_day'] = forecast_sample['session_start'].dt.hour
                forecast_sample['day_of_week'] = forecast_sample['session_start'].dt.dayofweek
                forecast_sample['month'] = forecast_sample['session_start'].dt.month
                
                # One-hot encode and align columns with the model's features
                forecast_sample_encoded = pd.get_dummies(forecast_sample, columns=['utm_source', 'utm_medium', 'creative_format', 'creative_theme', 'effectiveness_tier'], dummy_na=True)
                forecast_sample_encoded = forecast_sample_encoded.reindex(columns=features, fill_value=0)

                # Baseline prediction
                baseline_pred_proba = model.predict_proba(forecast_sample_encoded[features])[:, 1]
                
                budget_increase = st.select_slider("Select Budget Increase %", options=[10, 25, 50, 75, 100])
                
                # Create a new dataframe for the lift scenario
                forecast_sample_lift = forecast_sample_encoded.copy()
                forecast_sample_lift['spend'] *= (1 + budget_increase / 100)
                
                # Prediction with increased spend
                new_pred_proba = model.predict_proba(forecast_sample_lift[features])[:, 1]
                
                # Calculate lift
                lift_conversions = (new_pred_proba - baseline_pred_proba).sum()
                
                avg_order_value = orders_df['gross_revenue'].mean()
                lift_revenue = lift_conversions * avg_order_value
                
                col1, col2 = st.columns(2)
                col1.metric("Predicted Incremental Conversions", f"{lift_conversions:,.1f}", help="The number of additional conversions predicted if spend were increased for sessions like these.")
                col2.metric("Predicted Incremental Revenue", f"${lift_revenue:,.2f}", help="Based on the average order value.")
            else:
                st.warning("No data in the selected filter range to create a forecast.")

    with tab4:
        st.header("Model Insights: What Drives Conversion?")
        st.markdown("This chart shows the features the model found most predictive. This helps answer *how* we are winning or losing.")
        
        model, features = load_model_and_features()
        if model and features:
            feature_importances = pd.DataFrame({
                'feature': features,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)

            fig_imp = px.bar(
                feature_importances.head(15), 
                x='importance', 
                y='feature', 
                orientation='h',
                title='Top 15 Feature Importances for Conversion'
            )
            fig_imp.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_imp, use_container_width=True)

