import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="DTC Growth Cockpit",
    page_icon="🚀",
    layout="wide",
)

# --- Data Loading ---
@st.cache_data
def load_data():
    """Loads all necessary clean data files."""
    data_files = {
        'channel_perf': 'channel_performance_monthly.csv',
        'cohorts': 'customer_cohorts.csv',
        'web_funnel': 'web_funnel_monthly.csv',
        'email': 'email_performance_clean.csv'
    }
    
    loaded_data = {}
    for key, filename in data_files.items():
        try:
            df = pd.read_csv(filename)
            # Safely convert month columns to datetime
            for col in df.columns:
                if 'month' in col:
                    df[col] = pd.to_datetime(df[col])
            loaded_data[key] = df
        except FileNotFoundError:
            st.warning(f"Warning: The data file '{filename}' was not found. Some dashboard features may be unavailable.")
            loaded_data[key] = None
            
    return loaded_data

data = load_data()
df_channel_perf = data.get('channel_perf')
df_cohorts = data.get('cohorts')

# --- Dashboard Title ---
st.title("🚀 Rodrigues Consultores - Growth Cockpit")

# --- Create Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Overview", "📈 LTV & Retention", "🌐 Website Funnel", "📧 Email Performance"])

# --- Tab 1: Performance Overview ---
with tab1:
    st.header("Where is growth coming from?")
    
    if df_channel_perf is not None:
        # --- Revenue vs. Spend ---
        st.subheader("Revenue vs. Marketing Spend")
        df_monthly = df_channel_perf.groupby('month').agg({
            'gross_revenue': 'sum',
            'media_spend': 'sum'
        }).reset_index()
        fig_rev_spend = px.line(df_monthly, x='month', y=['gross_revenue', 'media_spend'], title='Monthly Revenue vs. Media Spend', labels={'value':'Amount (USD)'})
        st.plotly_chart(fig_rev_spend, use_container_width=True)

        # --- Channel Efficiency ---
        st.subheader("Channel Efficiency: LTV vs. CAC")
        st.info("Note: LTV is estimated based on historical cohort data. Awaiting user-level data for a more precise model.")
        
        df_channel_agg = df_channel_perf[df_channel_perf['month'].dt.year >= 2024].groupby('channel').agg({
            'gross_revenue': 'sum', 'media_spend': 'sum', 'new_customers_monthly': 'sum'
        }).reset_index()
        
        df_channel_agg['LTV_estimate'] = (df_channel_agg['gross_revenue'] / df_channel_agg['new_customers_monthly'].replace(0, 1)) * 2.5 
        df_channel_agg['CAC'] = df_channel_agg['media_spend'] / df_channel_agg['new_customers_monthly'].replace(0, 1)
        df_channel_agg.replace([np.inf, -np.inf], 0, inplace=True)

        fig_channel_bubble = px.scatter(
            df_channel_agg, x='CAC', y='LTV_estimate', size='gross_revenue', color='channel',
            text='channel', title='Channel LTV vs. CAC Bubble Chart (2024-2025 Data)',
            labels={'CAC': 'Customer Acquisition Cost ($)', 'LTV_estimate': 'Estimated Lifetime Value ($)'}
        )
        st.plotly_chart(fig_channel_bubble, use_container_width=True)

    else:
        st.warning("Could not load 'channel_performance_monthly.csv'. This view is unavailable.")

# --- Tab 2: LTV & Retention ---
with tab2:
    st.header("Who drives profit and who buys repeatedly?")

    if df_cohorts is not None:
        st.subheader("Customer Retention by Acquisition Cohort")
        
        # Calculate retention rates
        cohort_data = df_cohorts.set_index(['acquisition_month', 'channel'])
        cohort_sizes = cohort_data['new_customers']
        retention_matrix = cohort_data.drop(columns=['new_customers', 'orders_month_0']).divide(cohort_sizes, axis=0)
        
        # For simplicity, we'll average retention across all channels for the heatmap
        avg_retention_matrix = retention_matrix.groupby('acquisition_month').mean().mul(100)

        fig_heatmap = px.imshow(
            avg_retention_matrix,
            labels=dict(x="Months Since Acquisition", y="Acquisition Cohort", color="Retention Rate (%)"),
            title="Monthly Customer Retention Heatmap (All Channels)"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.warning("Could not load 'customer_cohorts.csv'. This view is unavailable.")

# --- Placeholder Tabs for Future Phases ---
with tab3:
    st.header("Website Funnel Analysis")
    st.info("This view will be populated using the 'web_funnel_monthly.csv' data.")

with tab4:
    st.header("Email Performance")
    st.info("This view will be populated using the 'email_performance_clean.csv' data.")
    st.markdown("**Accuracy Artefact Placeholder:** t-test or uplift chart: [to be generated]")

