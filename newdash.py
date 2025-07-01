import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64

# --- Page Configuration ---
st.set_page_config(
    page_title="DTC Analytics Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for a professional, elegant, and aesthetic UI ---
st.markdown("""
<style>
    /* Import Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* CSS Variables for Theming */
    :root {
        --dark-bg: #030712; /* Gray 950 */
        --sidebar-bg: #111827; /* Gray 900 */
        --card-bg: #1F2937; /* Gray 800 */
        --text-light: #F9FAFB; /* Gray 50 */
        --text-muted: #9CA3AF; /* Gray 400 */
        --border-color: #374155; /* Gray 700 */
        --primary-accent: #3B82F6; /* Blue 500 */
    }

    /* General Body and Font Styling */
    html, body, [class*="st-"], [class*="css-"] {
        font-family: 'Inter', sans-serif;
    }
    .main {
        background-color: var(--dark-bg);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p {
        color: var(--text-light);
    }
    [data-testid="stSidebar"] .st-emotion-cache-1629p8f span {
        color: var(--text-muted);
        font-weight: 500;
        padding: 0.5rem 0;
    }
    [data-testid="stSidebar"] .st-emotion-cache-1629p8f:has([aria-checked="true"]) span {
        color: var(--text-light);
        font-weight: 600;
    }
     [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-muted) !important;
     }

    /* KPI Metric Cards Styling */
    div[data-testid="stMetric"] {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: var(--primary-accent);
    }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--text-light) !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: clamp(2rem, 4vw, 2.75rem); /* Responsive font size */
    }

    /* Headings in Main Area */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-light) !important;
    }
    
</style>
""", unsafe_allow_html=True)


# --- Load Data ---
@st.cache_data
def load_data():
    """Loads and preprocesses data from the verified CSV file."""
    file_path = 'monthly_summary_v5_final_non_redundant.csv'
    try:
        df = pd.read_csv(file_path)
        month_map = {'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4, 'MAY': 5, 'JUNE': 6,
                     'JULY': 7, 'AUGUST': 8, 'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12}
        df['MONTH_NUM'] = df['MONTH'].map(month_map)
        df['Date'] = pd.to_datetime(dict(year=df.YEAR, month=df.MONTH_NUM, day=1))
        df['Total_Orders'] = df['Orders_New'] + df['Orders_Existing']
        df['Total_Customers'] = df['Customers_New'] + df['Customers_Existing']
        return df
    except FileNotFoundError:
        st.error(f"Error: Data file '{file_path}' not found.")
        return None

df = load_data()

# --- Reusable Components & Helper Functions ---
def get_svg_logo():
    """Returns a base64 encoded SVG logo for the sidebar."""
    svg = """
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 4H8V8H4V4Z" fill="#3B82F6"/>
        <path d="M4 10H8V20H4V10Z" fill="#3B82F6" fill-opacity="0.6"/>
        <path d="M10 4H20V8H10V4Z" fill="#10B981"/>
        <path d="M10 10H14V14H10V10Z" fill="#10B981" fill-opacity="0.6"/>
        <path d="M16 10H20V20H16V10Z" fill="#3B82F6"/>
        <path d="M10 16H14V20H10V16Z" fill="#10B981"/>
    </svg>
    """
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

def display_kpi_cards(kpis):
    """Displays a list of KPIs in styled columns."""
    cols = st.columns(len(kpis))
    for i, (label, value) in enumerate(kpis.items()):
        with cols[i]:
            st.metric(label=label, value=value)

# --- App Sidebar ---
with st.sidebar:
    st.image(get_svg_logo(), width=40)
    st.title("DTC Analytics")
    st.markdown("---")
    page = st.radio("Select a View", ["📊 Executive Summary", "🎯 Channel Efficiency", "💰 Profitability Analysis", "🔍 Data Explorer"])
    st.markdown("---")
    st.info("A strategic overview of business performance based on the unified dataset.")

# --- Main App Body ---
if df is not None:
    if page == "📊 Executive Summary":
        st.title("📊 Executive Summary")
        
        year = st.selectbox("Select Year for Analysis:", sorted(df['YEAR'].unique(), reverse=True), key="year_select")
        df_year = df[df['YEAR'] == year].copy()

        if not df_year.empty:
            total_revenue = df_year.groupby('MONTH')['Total_Revenue'].first().sum()
            total_spend = df_year['Spend'].sum()
            total_customers = df_year['Total_Customers'].sum()
            blended_cac = total_spend / total_customers if total_customers > 0 else 0
            blended_roas = total_revenue / total_spend if total_spend > 0 else float('inf')

            kpis = {
                "Total Revenue": f"${total_revenue:,.0f}",
                "Total Media Spend": f"${total_spend:,.0f}",
                "Overall Blended ROAS": f"{blended_roas:.2f}x" if np.isfinite(blended_roas) else "N/A",
                "Overall Blended CAC": f"${blended_cac:.2f}"
            }
            display_kpi_cards(kpis)

            st.markdown("---")
            st.header(f"{year} Monthly Performance Trends")
            monthly_trends = df_year.groupby('Date').agg(Total_Revenue=('Total_Revenue', 'first'), Spend=('Spend', 'sum')).reset_index()

            fig = go.Figure()
            fig.add_trace(go.Bar(x=monthly_trends['Date'], y=monthly_trends['Total_Revenue'], name='Total Revenue', marker_color='rgba(59, 130, 246, 0.7)'))
            fig.add_trace(go.Scatter(x=monthly_trends['Date'], y=monthly_trends['Spend'], name='Media Spend', mode='lines+markers', line=dict(color='#F59E0B', width=3), yaxis='y2'))
            fig.update_layout(
                title_text="Monthly Revenue vs. Media Spend", title_font_size=22,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F9FAFB'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(title='Total Revenue ($)', gridcolor='rgba(255,255,255,0.1)'),
                yaxis2=dict(title='Media Spend ($)', overlaying='y', side='right', showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)

    elif page == "🎯 Channel Efficiency":
        st.title("🎯 Channel Efficiency Analysis")
        st.markdown("Identifying the most efficient marketing channels for 2024.")
        
        df_2024 = df[df['YEAR'] == 2024].copy()
        kpi = df_2024.groupby('CHANNEL').agg(
            Spend=('Spend', 'sum'), Total_Customers=('Total_Customers', 'sum'),
            Total_Orders=('Total_Orders', 'sum'), Sessions=('Sessions', 'sum')
        ).reset_index()

        kpi['CVR'] = kpi.apply(lambda r: r['Total_Orders'] / r['Sessions'] if r['Sessions'] > 0 else 0, axis=1)
        kpi['CAC'] = kpi.apply(lambda r: r['Spend'] / r['Total_Customers'] if r['Total_Customers'] > 0 else 0, axis=1)
        kpi_chartable = kpi[(kpi['Total_Customers'] > 0) & (kpi['Spend'] > 0)]

        st.header("2024 Channel Efficiency: CAC vs. CVR")
        if not kpi_chartable.empty:
            fig = px.scatter(
                kpi_chartable, x="CAC", y="CVR", size="Total_Customers", color="CHANNEL", hover_name="CHANNEL",
                size_max=60, color_discrete_sequence=px.colors.qualitative.Plotly,
                labels={"CAC": "Customer Acquisition Cost ($)", "CVR": "Conversion Rate (%)"}
            )
            fig.update_layout(
                yaxis_tickformat='.2%', xaxis_tickprefix='$', legend_title_text='Channel', title_font_size=22,
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#F9FAFB'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            fig.update_traces(marker=dict(line=dict(width=1, color='#F9FAFB')))
            st.plotly_chart(fig, use_container_width=True)
            st.info("Ideal channels are in the top-left (Low CAC, High CVR). Bubble size indicates customer volume.")
        else:
            st.warning("No channels with both spend and customers in 2024 to display.")

    elif page == "💰 Profitability Analysis":
        st.title("💰 Profitability Analysis")
        st.markdown("Analyzing core profitability metrics over time.")
        
        year = st.selectbox("Select Year:", sorted(df['YEAR'].unique(), reverse=True), key="profit_year")
        df_year = df[df['YEAR'] == year].copy()

        if not df_year.empty:
            profit_data = df_year.groupby('Date').agg(
                Total_Revenue=('Total_Revenue', 'first'), Total_Returns=('Total_Returns', 'first'),
                Spend=('Spend', 'sum'), Technology_Spend=('Technology_Spend', 'first')
            ).reset_index()
            
            profit_data['Net_Revenue'] = profit_data['Total_Revenue'] - profit_data['Total_Returns']
            profit_data['Contribution_Margin'] = profit_data['Net_Revenue'] - profit_data['Spend']
            
            kpis = {
                "Total Net Revenue": f"${profit_data['Net_Revenue'].sum():,.0f}",
                "Total Contribution Margin": f"${profit_data['Contribution_Margin'].sum():,.0f}"
            }
            display_kpi_cards(kpis)

            st.markdown("---")
            st.header(f"{year} Monthly Profitability Trends")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=profit_data['Date'], y=profit_data['Net_Revenue'], name='Net Revenue', marker_color='#10B981'))
            fig.add_trace(go.Scatter(x=profit_data['Date'], y=profit_data['Contribution_Margin'], name='Contribution Margin', mode='lines+markers', line=dict(color='#F59E0B', width=3)))
            fig.update_layout(
                title_text="Net Revenue vs. Contribution Margin", title_font_size=22, 
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F9FAFB'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)

    elif page == "🔍 Data Explorer":
        st.title("🔍 Data Explorer")
        st.markdown("View and filter the complete, unified dataset.")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            label="Download Data as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='unified_monthly_performance.csv',
            mime='text/csv',
        )
else:
    st.warning("Data could not be loaded. Please check the file path and format.")
