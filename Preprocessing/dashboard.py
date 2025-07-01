import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="DTC Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

# --- Data Loading ---
@st.cache_data
def load_data():
    """Loads the main preprocessed data."""
    main_data_filename = 'preprocessed_data_clean.csv'
    try:
        df = pd.read_csv(main_data_filename)
        df['month'] = pd.to_datetime(df['month'])
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{main_data_filename}' was not found. Please ensure your clean data file is in the same folder as this script.")
        return None

df = load_data()

# --- Dashboard Title ---
st.title("📈 Rodrigues Consultores DTC - Performance Dashboard")

if df is not None:
    # --- Prepare Data for Views ---
    df_monthly = df.groupby('month').agg({'total_revenue': 'sum', 'total_spend': 'sum'}).reset_index()
    df_channel = df.groupby('channel').agg({'total_revenue': 'sum', 'total_spend': 'sum', 'new_customers': 'sum'}).reset_index()
    # Calculate channel-level LTV and CAC for visualization
    df_channel['6-Month LTV'] = (df_channel['total_revenue'] / df_channel['new_customers'].replace(0, 1)) * 2.5 
    df_channel['CAC'] = df_channel['total_spend'] / df_channel['new_customers'].replace(0, 1)
    df_channel['LTV-to-CAC Ratio'] = df_channel['6-Month LTV'] / df_channel['CAC'].replace(0, 1)
    df_channel.replace([np.inf, -np.inf], 0, inplace=True)

    # --- Tabs for Different Views ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Overview", "👥 Persona Economics", "📦 Product Strategy", "📧 Email Performance"])

    with tab1:
        st.header("Revenue vs. Marketing Spend")
        st.markdown("This view tracks how marketing investment translates into top-line revenue each month.")
        fig_rev_spend = px.line(df_monthly, x='month', y=['total_revenue', 'total_spend'], title='Monthly Revenue vs. Media Spend', labels={'value':'Amount (USD)'})
        st.plotly_chart(fig_rev_spend, use_container_width=True)

        st.header("Channel Efficiency: LTV vs. CAC")
        st.markdown("This chart positions each channel by its cost vs. the long-term value that customer brings.")
        fig_channel_bubble = px.scatter(df_channel, x='CAC', y='6-Month LTV', size='total_revenue', color='LTV-to-CAC Ratio', text='channel', title='Channel LTV vs. CAC Bubble Chart', color_continuous_scale=px.colors.sequential.Greens)
        st.plotly_chart(fig_channel_bubble, use_container_width=True)

    with tab2:
        st.header("Persona & Economics Matrix")
        st.markdown("This matrix defines personas by their acquisition channel to identify profit engines and money drains.")
        persona_df = df_channel[['6-Month LTV', 'CAC', 'LTV-to-CAC Ratio']].set_index(df_channel['channel'])
        st.dataframe(persona_df.style.background_gradient(cmap='Greens', subset=['6-Month LTV', 'LTV-to-CAC Ratio']).background_gradient(cmap='Reds', subset=['CAC']), use_container_width=True)
    
    with tab3:
        st.header("Product Strategy Quadrant")
        st.warning("This view is a functional sample. Product-level analysis requires SKU-level transactional data, which was not available in the provided aggregated files.")
        sku_data = {'SKU': ['Leakproof Panty', 'Flora Lace Bra', '3-for-$48 Pack', 'Basic Tee'],'Category': ['Core', 'New', 'Value Pack', 'Basics'],'Total Orders': [15000, 2500, 25000, 8000],'Profit Margin': [0.45, 0.65, 0.25, 0.15]}
        df_sku = pd.DataFrame(sku_data)
        avg_orders = df_sku['Total Orders'].mean()
        avg_margin = df_sku['Profit Margin'].mean()
        fig_product_quad = px.scatter(df_sku, x='Total Orders', y='Profit Margin', text='SKU', color='Category', title='Product Performance Quadrant')
        fig_product_quad.add_vline(x=avg_orders, line_width=1, line_dash="dash", line_color="grey")
        fig_product_quad.add_hline(y=avg_margin, line_width=1, line_dash="dash", line_color="grey")
        st.plotly_chart(fig_product_quad, use_container_width=True)

    with tab4:
        st.header("Email Performance: Automated Flows vs. Batch Campaigns")
        st.warning("This view is a functional sample. The raw 'Email.csv' file contained formatting issues that prevented automated processing.")
        email_data = {
            'Type': ['Flows', 'Campaigns'],
            'Total Revenue': [750000, 562500],
            'Revenue per Send': [1.50, 0.22],
            'CTR (%)': [10.0, 3.0],
            'CVR (% from Clicks)': [10.0, 5.0]
        }
        df_email_sample = pd.DataFrame(email_data).set_index('Type')
        st.dataframe(df_email_sample, use_container_width=True)
else:
    st.info("Awaiting 'preprocessed_data_clean.csv' to generate the dashboard.")
