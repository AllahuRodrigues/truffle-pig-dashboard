import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.dates as mdates
import numpy as np
import io

# --- App Configuration ---
st.set_page_config(
    page_title="Business Growth & Profitability Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Data Processing Logic from Analysis Scripts ---
@st.cache_data
def load_and_process_data(marketing_file, media_spend_file, topsheet_file, new_cust_file, ext_cust_file):
    """
    Loads and processes all uploaded CSV files to generate the dataframes needed for the dashboard plots.
    This function encapsulates the logic from all the user's analysis scripts.
    """
    try:
        # --- Load Data from uploaded files ---
        marketing_df = pd.read_csv(marketing_file)
        media_spend_df = pd.read_csv(media_spend_file)
        topsheet_df = pd.read_csv(topsheet_file)
        new_cust_df = pd.read_csv(new_cust_file)
        ext_cust_df = pd.read_csv(ext_cust_file)

        # --- 1. Corrected ROAS Calculation ---
        agency_fees_df = media_spend_df[media_spend_df['channel_name'].str.contains("Agency", na=False)].copy()
        agency_fees_df['mapping_key'] = agency_fees_df['channel_name'].str.replace(" Agency", "", regex=False).str.lower()
        agency_fees_df['mapping_key'] = agency_fees_df['mapping_key'].replace({'affiliate': 'affiliates'})
        total_agency_fees_agg = agency_fees_df.groupby('mapping_key')['value'].sum().reset_index()
        total_agency_fees_agg.rename(columns={'value': 'agency_fees'}, inplace=True)

        channel_summary = marketing_df.groupby('marketing_channel').agg(
            total_ad_spend=('ad_spend', 'sum'),
            total_revenue=('gross_discount_(shopify)', 'sum')
        ).reset_index()

        channel_summary = pd.merge(channel_summary, total_agency_fees_agg, left_on='marketing_channel', right_on='mapping_key', how='left')
        channel_summary['agency_fees'] = channel_summary['agency_fees'].fillna(0)
        channel_summary['true_total_ad_spend'] = channel_summary['total_ad_spend'] + channel_summary['agency_fees']
        channel_summary['corrected_roas'] = channel_summary.apply(
            lambda row: row['total_revenue'] / row['true_total_ad_spend'] if row['true_total_ad_spend'] > 0 else 0, axis=1
        )
        roas_df = channel_summary.sort_values('corrected_roas', ascending=False).reset_index(drop=True)

        # --- 2. Monthly Trends (ROAS & CAC) ---
        media_spend_df['date'] = pd.to_datetime(media_spend_df['date'])
        topsheet_df['date'] = pd.to_datetime(topsheet_df['date'])
        new_cust_df['date'] = pd.to_datetime(new_cust_df['date'])
        ext_cust_df['date'] = pd.to_datetime(ext_cust_df['date'])

        # Monthly Spend
        agency_fees_df['date'] = pd.to_datetime(agency_fees_df['date'])
        direct_media_spend_df = media_spend_df[~media_spend_df['channel_name'].str.contains("Agency", na=False)].copy()
        direct_media_spend_df['mapping_key'] = direct_media_spend_df['channel_name'].str.replace(" Media", "", regex=False).str.lower()
        monthly_spend = pd.merge(direct_media_spend_df, agency_fees_df[['date', 'mapping_key', 'value']], on=['date', 'mapping_key'], how='left', suffixes=('_media', '_agency'))
        monthly_spend['value_agency'] = monthly_spend['value_agency'].fillna(0)
        monthly_spend['total_spend'] = monthly_spend['value_media'] + monthly_spend['value_agency']
        
        # --- PATCH SPEND GAP (Task 4) ---
        try:
            overrides_df = pd.read_csv("spend_overrides.csv")
            overrides_df['month'] = pd.to_datetime(overrides_df['month'])
            # Standardize channel names to match 'mapping_key'
            overrides_df['channel'] = overrides_df['channel'].str.lower().str.replace(" agency", "").str.strip()
            
            monthly_spend['month'] = monthly_spend['date'].dt.to_period('M').dt.to_timestamp()

            monthly_spend = pd.merge(
                monthly_spend,
                overrides_df,
                left_on=['month', 'mapping_key'],
                right_on=['month', 'channel'],
                how='left'
            )
            
            monthly_spend['total_spend'] = np.where(monthly_spend['total_spend'] == 0, monthly_spend['spend_override'], monthly_spend['total_spend'])
            monthly_spend.drop(columns=['month', 'channel', 'spend_override'], inplace=True)
            monthly_spend['total_spend'].fillna(0, inplace=True)

        except FileNotFoundError:
            st.sidebar.warning("`spend_overrides.csv` not found. Spend gap not patched.")
        # --- END OF PATCH ---

        # Monthly Revenue
        monthly_revenue = topsheet_df[topsheet_df['metric'].str.contains("NET SALES -", na=False)].copy()
        monthly_revenue['mapping_key'] = monthly_revenue['metric'].str.replace("NET SALES - ", "", regex=False).str.strip().str.lower()
        
        # Monthly Performance
        monthly_performance = pd.merge(monthly_spend[['date', 'mapping_key', 'total_spend']], monthly_revenue[['date', 'mapping_key', 'value']], on=['date', 'mapping_key'], how='left')
        monthly_performance.rename(columns={'value': 'net_revenue'}, inplace=True)
        monthly_performance['net_revenue'] = monthly_performance['net_revenue'].fillna(0)
        monthly_performance['monthly_roas'] = monthly_performance.apply(lambda row: row['net_revenue'] / row['total_spend'] if row['total_spend'] > 0 else 0, axis=1)

        # Monthly CAC
        new_cust_df['mapping_key'] = new_cust_df['channel_name'].str.lower().replace({'affiliate': 'affiliates'})
        monthly_cac_df = pd.merge(monthly_spend[['date', 'mapping_key', 'total_spend']], new_cust_df[['date', 'mapping_key', 'value']], on=['date', 'mapping_key'], how='left')
        monthly_cac_df.rename(columns={'value': 'new_customers'}, inplace=True)
        monthly_cac_df['new_customers'] = monthly_cac_df['new_customers'].fillna(0)
        monthly_cac_df['monthly_cac'] = monthly_cac_df.apply(lambda row: row['total_spend'] / row['new_customers'] if row['new_customers'] > 0 else 0, axis=1)
        
        # --- FIX for KeyError ---
        # Combine monthly trends by merging the calculated CAC into the performance dataframe
        monthly_trends_df = pd.merge(
            monthly_performance,
            monthly_cac_df[['date', 'mapping_key', 'monthly_cac']],
            on=['date', 'mapping_key'],
            how='left'
        )
        
        channels_to_plot = ['paid search', 'paid social', 'affiliates']
        monthly_trends_df = monthly_trends_df[monthly_trends_df['mapping_key'].isin(channels_to_plot)]


        # --- 3. Overall CAC Calculation ---
        analysis_end_date = pd.to_datetime('2025-05-01')
        media_spend_capped = media_spend_df[media_spend_df['date'] < analysis_end_date].copy()
        new_cust_capped = new_cust_df[new_cust_df['date'] < analysis_end_date].copy()
        
        agency_fees_capped = media_spend_capped[media_spend_capped['channel_name'].str.contains("Agency", na=False)].copy()
        agency_fees_capped['mapping_key'] = agency_fees_capped['channel_name'].str.replace(" Agency", "", regex=False).str.lower().replace({'affiliate': 'affiliates'})
        total_agency_fees = agency_fees_capped.groupby('mapping_key')['value'].sum()

        direct_media_spend_capped = media_spend_capped[~media_spend_capped['channel_name'].str.contains("Agency", na=False)].copy()
        direct_media_spend_capped['mapping_key'] = direct_media_spend_capped['channel_name'].str.replace(" Media", "", regex=False).str.lower().replace({'affiliate': 'affiliates'})
        total_media_spend = direct_media_spend_capped.groupby('mapping_key')['value'].sum()
        
        total_spend_agg = total_media_spend.add(total_agency_fees, fill_value=0)
        total_new_customers = new_cust_capped.groupby('mapping_key')['value'].sum()
        
        cac_df = pd.DataFrame({'total_spend': total_spend_agg, 'total_new_customers': total_new_customers})
        cac_df['cac'] = cac_df.apply(lambda r: r['total_spend'] / r['total_new_customers'] if r['total_new_customers'] > 0 else 0, axis=1)
        cac_df = cac_df[cac_df['cac'] > 0].reset_index().rename(columns={'mapping_key': 'channel'})


        # --- 4. Customer Composition ---
        new_cust_df['customer_type'] = 'New'
        ext_cust_df['customer_type'] = 'Existing'
        all_cust_df = pd.concat([new_cust_df, ext_cust_df])
        all_cust_df['date'] = pd.to_datetime(all_cust_df['date'])
        all_cust_capped = all_cust_df[all_cust_df['date'] < analysis_end_date]
        cust_composition_df = all_cust_capped.groupby(['date', 'customer_type'])['value'].sum().unstack().fillna(0)
        
        # --- 5. New Customer Acquisition by Channel ---
        new_cust_acq_df = new_cust_capped.groupby('channel_name')['value'].sum().sort_values(ascending=False).reset_index()

        return roas_df, monthly_trends_df, cac_df, cust_composition_df, new_cust_acq_df

    except Exception as e:
        st.error(f"An error occurred during data processing: {e}")
        st.warning("Please ensure all uploaded files are correct and in the expected CSV format.")
        return None, None, None, None, None

# --- Plotting Functions ---

def plot_corrected_roas(df):
    roas_chart_data = df[df['true_total_ad_spend'] > 0].sort_values('corrected_roas', ascending=True)
    fig = px.bar(
        roas_chart_data, x='corrected_roas', y='marketing_channel', orientation='h',
        title='Corrected Return on Ad Spend (ROAS) by Channel',
        labels={'corrected_roas': 'Corrected ROAS', 'marketing_channel': 'Marketing Channel'},
        text='corrected_roas', color='corrected_roas', color_continuous_scale=px.colors.sequential.Viridis
    )
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
    return fig

def plot_monthly_roas_trends(df):
    fig = px.line(
        df, x='date', y='monthly_roas', color='mapping_key', markers=True,
        title='Monthly ROAS Trend for Key Paid Channels',
        labels={'date': 'Month', 'monthly_roas': 'Monthly ROAS', 'mapping_key': 'Channel'}
    )
    fig.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="Breakeven (ROAS = 1)")
    return fig

def plot_overall_cac(df):
    df_sorted = df.sort_values('cac', ascending=True)
    fig = px.bar(
        df_sorted, x='cac', y='channel', orientation='h',
        title='Overall Customer Acquisition Cost (CAC) by Channel',
        labels={'cac': 'Overall CAC ($)', 'channel': 'Channel'},
        text='cac', color='cac', color_continuous_scale=px.colors.sequential.Magma
    )
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
    return fig

def plot_monthly_cac_trends(df):
    fig = px.line(
        df, x='date', y='monthly_cac', color='mapping_key', markers=True,
        title='Monthly Customer Acquisition Cost (CAC) Trend',
        labels={'date': 'Month', 'monthly_cac': 'Monthly CAC ($)', 'mapping_key': 'Channel'}
    )
    return fig

def plot_customer_composition(df):
    fig = px.area(
        df, x=df.index, y=['New', 'Existing'],
        title='Monthly Active Customers: New vs. Existing',
        labels={'date': 'Month', 'value': 'Number of Customers', 'variable': 'Customer Type'}
    )
    return fig

def plot_new_customer_acquisition(df):
    df_sorted = df.sort_values('value', ascending=True)
    fig = px.bar(
        df_sorted, x='value', y='channel_name', orientation='h',
        title='Top Channels for New Customer Acquisition (All Time)',
        labels={'value': 'Total New Customers Acquired', 'channel_name': 'Channel'},
        text='value', color='value', color_continuous_scale='tealgrn'
    )
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
    return fig

# --- NEW WHOLESALE FUNCTIONS (Task 7) ---
def create_wholesale_dummy_data():
    """Generates a dummy DataFrame for the wholesale module with calculated KPIs."""
    np.random.seed(42)
    num_rows = 30
    retailers = ['Big Box Store', 'Boutique XYZ', 'Online Marketplace', 'Dept Store']
    data = {
        'retailer': np.random.choice(retailers, num_rows),
        'sku': [f'SKU{100+i}' for i in range(num_rows)],
        'units_ordered': np.random.randint(100, 500, size=num_rows),
        'units_sold': np.random.randint(50, 400, size=num_rows),
        'on_hand': np.random.randint(20, 200, size=num_rows),
        'wholesale_dollars': np.random.randint(5000, 20000, size=num_rows)
    }
    df = pd.DataFrame(data)
    df['units_shipped'] = df['units_ordered'] - np.random.randint(0, 50, size=num_rows)
    df['units_shipped'] = df['units_shipped'].clip(lower=0)
    df['discounts'] = df['wholesale_dollars'] * np.random.uniform(0.05, 0.15, size=num_rows)
    df['returns_dollars'] = df['wholesale_dollars'] * np.random.uniform(0.02, 0.1, size=num_rows)
    df['markdowns_dollars'] = df['wholesale_dollars'] * np.random.uniform(0.01, 0.05, size=num_rows)
    df['sell_through_pct'] = df['units_sold'] / (df['units_sold'] + df['on_hand'])
    avg_weekly_units_sold = df['units_sold'] / 4
    df['weeks_of_supply'] = df['on_hand'] / avg_weekly_units_sold.replace(0, np.nan)
    df['fill_rate_pct'] = df['units_shipped'] / df['units_ordered']
    net_revenue = df['wholesale_dollars'] - df['discounts'] - df['returns_dollars'] - df['markdowns_dollars']
    df['net_margin_pct'] = net_revenue / df['wholesale_dollars']
    df.fillna(0, inplace=True)
    return df

def plot_wholesale_performance(df):
    """Creates the Plotly scatter plot for wholesale performance."""
    fig = px.scatter(
        df,
        x="sell_through_pct",
        y="net_margin_pct",
        size="wholesale_dollars",
        color="retailer",
        hover_name="sku",
        title="Wholesale Performance: Sell-Through vs. Net Margin",
        labels={
            "sell_through_pct": "Sell-Through %",
            "net_margin_pct": "Net Margin %",
            "wholesale_dollars": "Wholesale Revenue ($)"
        },
        template="plotly_white"
    )
    fig.update_layout(xaxis_tickformat='.0%', yaxis_tickformat='.0%')
    return fig


# --- Dashboard UI ---

st.title("📈 Business Growth & Profitability Dashboard")
st.markdown("An interactive dashboard to analyze customer behavior, channel efficiency, and product strategy from your data.")

# --- Sidebar for File Uploads and Navigation ---
st.sidebar.header("Data Upload")
st.sidebar.info("Please upload your 5 cleaned CSV files to populate the dashboard.")

marketing_file = st.sidebar.file_uploader("1. Marketing Channel Breakdown CSV", type="csv")
media_spend_file = st.sidebar.file_uploader("2. Media Spend by Channel CSV", type="csv")
topsheet_file = st.sidebar.file_uploader("3. TOPSHEET CSV", type="csv")
new_cust_file = st.sidebar.file_uploader("4. Customers by Channel (New) CSV", type="csv")
ext_cust_file = st.sidebar.file_uploader("5. Customers by Channel (Existing) CSV", type="csv")

st.sidebar.header("Dashboard Navigation")
page = st.sidebar.radio(
    "Select a Question to Answer:",
    [
        "❓ Executive Summary",
        "👥 Who is driving my growth?",
        "🌍 Where is that growth coming from?",
        "🛍️ Wholesale Shell", # New page
        "📦 What should I be selling?"
    ]
)

# --- Main Content ---

# First, handle the pages that have specific data requirements
if page in ["❓ Executive Summary", "👥 Who is driving my growth?", "🌍 Where is that growth coming from?"]:
    
    # Check if all files are uploaded before proceeding
    if all([marketing_file, media_spend_file, topsheet_file, new_cust_file, ext_cust_file]):
        roas_df, monthly_trends_df, cac_df, cust_composition_df, new_cust_acq_df = load_and_process_data(
            marketing_file, media_spend_file, topsheet_file, new_cust_file, ext_cust_file
        )

        if roas_df is not None: # Check if data processing was successful
            if page == "❓ Executive Summary":
                st.header("Executive Summary: Key Findings & Strategic Recommendations")
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ Top Performers")
                    st.success("""
                    **Organic Search, Email, and SMS are hyper-efficient profit engines.**
                    - **ROAS:** Generating **$25 - $47** for every dollar invested.
                    - **Action:** Protect, optimize, and scale investment in SEO, email content, and SMS list growth.
                    """)
                    st.info("""
                    **Paid Search is a solid, profitable workhorse.**
                    - **ROAS:** **~$5.18**, aligning with business-wide averages.
                    - **CAC:** **~$39**, making it the most efficient paid channel for scalable acquisition.
                    - **Action:** Maintain or moderately increase investment, focusing on strategies that preserve ROAS.
                    """)

                with col2:
                    st.subheader("❌ Underperformers & Drains")
                    st.error("""
                    **Paid Social is the primary drain on marketing profitability.**
                    - **ROAS:** **$0.73** (losing $0.27 per $1 spent).
                    - **CAC:** **~$139** (3.5x more expensive than Paid Search).
                    - **Rank:** 5th for new customer acquisition despite the highest spend.
                    - **Action:** **Immediately freeze or significantly reduce budget.** Conduct a comprehensive audit of campaigns, creative, and targeting.
                    """)
                    st.warning("""
                    **Affiliates are unprofitable and inefficient.**
                    - **ROAS:** **~$1.78** (not profitable after COGS).
                    - **CAC:** **~$114**, the second most expensive channel.
                    - **Action:** Reassess the program structure and fee model. The current setup is unsustainable.
                    """)
                
                st.markdown("---")
                st.header("The 'Leaky Bucket' Problem")
                st.write("The analysis reveals a pattern of high new customer acquisition but poor retention. The business is constantly pouring new users in, but not enough are being retained to drive sustainable, long-term growth. A strategic shift towards improving customer retention is critical.")
                st.plotly_chart(plot_customer_composition(cust_composition_df), use_container_width=True)


            elif page == "👥 Who is driving my growth?":
                st.header("👥 Customer Analysis: Personas & Segments")
                st.markdown("Understanding who your most valuable customers are and how they behave.")
                
                st.subheader("Monthly Active Customers: New vs. Existing")
                st.plotly_chart(plot_customer_composition(cust_composition_df), use_container_width=True)
                with st.expander("Key Observations & Strategic Insights"):
                    st.markdown("""
                    - **Stagnant Growth & High Volatility:** The total number of active customers isn't showing consistent growth, indicating a reliance on promotions rather than steady, organic acquisition.
                    - **The "Leaky Bucket":** A large portion of customers each month are new. This reveals a pattern of frequent acquisition but poor retention. A healthy business would show the 'Existing' customer base growing steadily.
                    - **Strong Seasonality:** Consistent peaks appear during the holiday season (Nov/Dec), which should be factored into forecasting.
                    """)

                st.subheader("Top Channels for New Customer Acquisition")
                st.plotly_chart(plot_new_customer_acquisition(new_cust_acq_df), use_container_width=True)
                with st.expander("Key Observations & Strategic Insights"):
                    st.markdown("""
                    - **Search is King:** Paid Search and Organic Search are the top two channels for acquiring new customers by a significant margin, aligning with their strong ROAS.
                    - **Paid Social Underperforms:** Despite having the largest ad spend, Paid Social ranks only 5th in new customer acquisition, revealing a major misalignment between spending and performance.
                    - **The Dilemma:** Paid Social is both unprofitable (bad ROAS) and inefficient at acquiring new customers relative to its cost.
                    """)

            elif page == "🌍 Where is that growth coming from?":
                st.header("🌍 Channel Analysis: Performance & Tactics")
                st.markdown("Evaluating which marketing channels deliver the best return on investment.")

                tab1, tab2 = st.tabs(["Return on Ad Spend (ROAS)", "Customer Acquisition Cost (CAC)"])

                with tab1:
                    # --- ADD DATA GAP FLAG (Task 4) ---
                    if (monthly_trends_df['total_spend'] <= 0).any():
                        st.error("🚨 Data Gap: One or more channels has $0 spend in a recent month after patching. Please review the data sources.")
                    
                    st.subheader("Corrected Return on Ad Spend (ROAS) by Channel")
                    st.plotly_chart(plot_corrected_roas(roas_df), use_container_width=True)
                    st.dataframe(roas_df.sort_values('corrected_roas', ascending=False).reset_index(drop=True))
                    
                    st.subheader("Monthly ROAS Trend for Key Paid Channels")
                    st.plotly_chart(plot_monthly_roas_trends(monthly_trends_df), use_container_width=True)
                    with st.expander("Key Observations & Strategic Insights on ROAS"):
                        st.markdown("""
                        - **Elite Channels:** Organic Search, Email, and SMS are hyper-efficient, acting as primary profit engines.
                        - **Paid Search:** A solid, profitable workhorse, validating its role as a reliable, scalable channel.
                        - **Chronically Unprofitable:** Paid Social and Affiliates have a history of being unprofitable. This is a long-term strategic issue, not a recent decline. The fundamental approach for these channels is not working.
                        """)

                with tab2:
                    st.subheader("Overall Customer Acquisition Cost (CAC) by Channel")
                    st.plotly_chart(plot_overall_cac(cac_df), use_container_width=True)
                    st.dataframe(cac_df.sort_values('cac', ascending=True).reset_index(drop=True))

                    st.subheader("Monthly CAC Trend for Key Paid Channels")
                    st.plotly_chart(plot_monthly_cac_trends(monthly_trends_df), use_container_width=True)
                    with st.expander("Key Observations & Strategic Insights on CAC"):
                        st.markdown("""
                        - **Extreme Inefficiency:** Paid Social is the most critical finding, costing **$129.6765** to acquire a customer—3.5x more than Paid Search.
                        - **Expensive Alternatives:** The Affiliate channel is also very expensive at **$111.7699** per new customer.
                        - **The Clear Winner:** Paid Search is the most efficient and scalable acquisition engine at **$37.5405** per new customer.
                        - **Strategic Insight:** Prioritize and scale Paid Search. Re-evaluate or pause Paid Social and Affiliate spending immediately.
                        """)
    else:
        # Show this message if files for the data-dependent pages have not been uploaded
        st.info("Please upload all 5 required CSV files using the sidebar to begin the analysis.")
        st.image("https://i.imgur.com/3_3.png", caption="Upload files to start", use_column_width=True)

# Now, handle the pages that do NOT require the main data files to be loaded
elif page == "🛍️ Wholesale Shell":
    st.header("🛍️ Wholesale Shell: Framework Demo")
    st.markdown("This module demonstrates the KPI and visualization framework for wholesale data.")
    
    # Generate the dummy data and plot
    wholesale_df = create_wholesale_dummy_data()
    st.plotly_chart(plot_wholesale_performance(wholesale_df), use_container_width=True)
    
    with st.expander("Why is this dummy data?"):
        st.info("""
        The client hasn’t provided retailer feeds yet; this proves the framework is ready the moment they do. 
        [cite: client said] This section shows stakeholders the framework before we have retailer feeds.
        """)

elif page == "📦 What should I be selling?":
    st.header("📦 Product & Pricing Strategy Analysis")
    st.warning("Analysis for this section is pending.", icon="⚠️")
    st.markdown("""
    This section of the dashboard is designed to answer critical questions about your product strategy. However, the necessary data and analysis have not yet been provided.
    
    **To complete this view, we need data cuts that can help us understand:**
    - **Product-level LTV:** Which SKUs bring back high-value buyers?
    - **Attachment Rate / Bundle Behavior:** What else are customers buying with top sellers?
    - **Product Performance by Acquisition Channel:** Do some products attract better personas via specific channels?
    - **Discount Reliance:** Which SKUs can carry full price versus those that rely on promotions?

    Once this data is available, we can build out the following analyses:
    - **Product Strategy Dashboard:** Classifying products into `Core Drivers`, `Test & Learn`, `Sunset Candidates`, and `Gateway SKUs`.
    - **Cross-Sell & Bundle Opportunities.**
    - **Pricing & Promotion Strategy Recommendations.**
    """)
    st.info("Please provide the relevant data exports (e.g., sales by SKU, order line items) to populate this section.", icon="ℹ️")
