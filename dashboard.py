import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io
import re
import base64

# --- App Configuration ---
st.set_page_config(
    page_title="Business Growth & Profitability Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Helper: Load Banner Image as Base64 ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{encoded}"

banner_image_base64 = get_base64_image("data/img/img.jpg")

# --- Enhanced Aesthetic CSS ---
st.markdown("""
<style>
body, .main, .block-container {
    background: linear-gradient(135deg, #181c24 0%, #232b39 100%);
    color: #f5f6fa;
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}
section[data-testid="stSidebar"] {
    background: #202736;
    color: #fff;
    border-right: 1px solid #2e3a4e;
    padding-top: 24px;
}
section[data-testid="stSidebar"] .stRadio > div {
    gap: 0.5rem;
}
section[data-testid="stSidebar"] .stFileUploader {
    background: #232b39;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
}
section[data-testid="stSidebar"] .stFileUploader label {
    color: #bfc9da;
    font-weight: 500;
}
div[data-testid="metric-container"] {
    background: linear-gradient(120deg, #232b39 60%, #2e3a4e 100%);
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid #2e3a4e;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-2px) scale(1.025);
    box-shadow: 0 8px 32px rgba(80,120,255,0.10);
    border-color: #4b6cb7;
}
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-weight: 700;
    letter-spacing: 0.01em;
    color: #e6e9f0;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    animation: fadeSlideIn 0.9s cubic-bezier(.77,0,.18,1);
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(24px);}
    to { opacity: 1; transform: translateY(0);}
}
.element-container:has([data-testid="stPlotlyChart"]) {
    animation: fadeUp 0.7s cubic-bezier(.77,0,.18,1);
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(30px);}
    to { opacity: 1; transform: translateY(0);}
}
button[kind="primary"], .stButton>button {
    background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%) !important;
    color: #fff !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: 600;
    transition: background 0.2s;
}
button[kind="primary"]:hover, .stButton>button:hover {
    background: linear-gradient(90deg, #182848 0%, #4b6cb7 100%) !important;
}
.stExpander {
    background: #232b39 !important;
    border-radius: 10px !important;
    border: 1px solid #2e3a4e !important;
}
.stExpanderHeader {
    color: #bfc9da !important;
    font-weight: 600 !important;
}
.stDataFrame {
    background: #232b39 !important;
    border-radius: 10px !important;
    border: 1px solid #2e3a4e !important;
}
::-webkit-scrollbar { width: 8px;}
::-webkit-scrollbar-thumb { background: #444d5c; border-radius: 10px;}
::-webkit-scrollbar-thumb:hover { background: #4b6cb7;}
.section-divider {
    background: linear-gradient(90deg, #4b6cb7, #182848);
    height: 4px;
    border-radius: 2px;
    margin: 32px 0 36px 0;
    box-shadow: 0 2px 8px rgba(75,108,183,0.15);
}
</style>
""", unsafe_allow_html=True)

# --- Modern Banner with Overlay ---
st.markdown(f"""
<div style="
    position: relative;
    background-image: url('{banner_image_base64}');
    height: 340px;
    background-attachment: fixed;
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    overflow: hidden;
    border-radius: 18px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(75,108,183,0.18);
">
    <div style="
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(120deg, rgba(24,28,36,0.82) 60%, rgba(75,108,183,0.45) 100%);
        z-index: 1;
    "></div>
    <div style="
        position: relative;
        z-index: 2;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #fff;
        text-align: center;
        padding: 0 24px;
    ">
        <span style="font-size: 2.5rem; font-weight: 800; letter-spacing: 0.01em; text-shadow: 2px 2px 8px rgba(0,0,0,0.25);">
            📈 Business Growth & Profitability Dashboard
        </span>
        <span style='font-size: 1.15rem; font-weight: 400; margin-top: 16px; color: #e6e9f0; text-shadow: 1px 1px 6px rgba(0,0,0,0.18);'>
            An interactive dashboard to analyze customer behavior, channel efficiency, and product strategy from your data
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# --- Sidebar for File Uploads and Navigation ---
with st.sidebar:
    st.header("Data Upload")

    # Toggle button for showing/hiding file uploaders
    if "show_upload_section" not in st.session_state:
        st.session_state["show_upload_section"] = False

    # --- Persistent file uploaders using session_state for all files ---
    def persistent_file_uploader(label, key, filetype="csv"):
        uploader_key = f"{key}_uploader"
        # Always use the same key for the widget, but store the file in session_state[key]
        file = st.file_uploader(label, type=filetype, key=uploader_key)
        # Only update session_state if a new file is selected
        if file is not None:
            st.session_state[key] = file
        # Always return the file from session_state if it exists
        return st.session_state.get(key, None)

    # Always call the uploader for each file, but only show the widget if toggled on
    def get_file(label, key, filetype="csv"):
        # Always call the uploader so Streamlit keeps the file in session_state
        file = persistent_file_uploader(label, key, filetype)
        # Only show the widget if toggled on, otherwise just return the file from session_state
        if st.session_state["show_upload_section"]:
            return file
        else:
            return st.session_state.get(key, None)

    # Ensure all uploaders are always called, so files persist across tab switches
    marketing_file = get_file("1. Marketing Channel Breakdown CSV", "marketing_file")
    media_spend_file = get_file("2. Media Spend by Channel CSV", "media_spend_file")
    topsheet_file = get_file("3. TOPSHEET CSV", "topsheet_file")
    new_cust_file = get_file("4. Customers by Channel (New) CSV", "new_cust_file")
    ext_cust_file = get_file("5. Customers by Channel (Existing) CSV", "ext_cust_file")
    persona_file = get_file("6. Customer Personas CSV (Optional)", "persona_file")
    email_file = get_file("7. Email Flow Performance CSV (Optional)", "email_file")

    # Only show the widgets if toggled on
    if st.session_state["show_upload_section"]:
        st.info("Please upload your CSV files to populate the dashboard.")

    st.header("Dashboard Navigation")
    page = st.radio(
        "Select a Question to Answer:",
        [
            "❓ Executive Summary",
            "👥 Who is driving my growth?",
            "🌍 Where is that growth coming from?",
            "📧 Email Performance",
            "🛍️ Wholesale Shell",
            "📦 What should I be selling?"
        ]
    )

# --- Data Processing Logic ---
@st.cache_data
def load_and_process_data(marketing_file, media_spend_file, topsheet_file, new_cust_file, ext_cust_file):
    try:
        marketing_df = pd.read_csv(marketing_file)
        media_spend_df = pd.read_csv(media_spend_file)
        topsheet_df = pd.read_csv(topsheet_file)
        new_cust_df = pd.read_csv(new_cust_file)
        ext_cust_df = pd.read_csv(ext_cust_file)

        agency_fees_df = media_spend_df[media_spend_df['channel_name'].str.contains("Agency", na=False, case=False)].copy()
        agency_fees_df['mapping_key'] = agency_fees_df['channel_name'].str.replace(" Agency", "", regex=True, flags=re.IGNORECASE).str.lower().str.strip()
        agency_fees_df['mapping_key'] = agency_fees_df['mapping_key'].replace({'affiliate': 'affiliates'})
        total_agency_fees_agg = agency_fees_df.groupby('mapping_key')['value'].sum().reset_index()
        total_agency_fees_agg.rename(columns={'value': 'agency_fees'}, inplace=True)
        channel_summary = marketing_df.groupby('marketing_channel').agg(total_ad_spend=('ad_spend', 'sum'), total_revenue=('gross_discount_(shopify)', 'sum')).reset_index()
        channel_summary = pd.merge(channel_summary, total_agency_fees_agg, left_on='marketing_channel', right_on='mapping_key', how='left')
        channel_summary['agency_fees'] = channel_summary['agency_fees'].fillna(0)
        channel_summary['true_total_ad_spend'] = channel_summary['total_ad_spend'] + channel_summary['agency_fees']
        channel_summary['corrected_roas'] = channel_summary.apply(lambda row: row['total_revenue'] / row['true_total_ad_spend'] if row['true_total_ad_spend'] > 0 else 0, axis=1)
        roas_df = channel_summary.sort_values('corrected_roas', ascending=False).reset_index(drop=True)

        media_spend_df['date'] = pd.to_datetime(media_spend_df['date'])
        topsheet_df['date'] = pd.to_datetime(topsheet_df['date'])
        new_cust_df['date'] = pd.to_datetime(new_cust_df['date'])
        ext_cust_df['date'] = pd.to_datetime(ext_cust_df['date'])
        media_spend_df['channel_name'] = media_spend_df['channel_name'].str.lower().replace({'affiliate': 'affiliates'})
        agency_fees_df = media_spend_df[media_spend_df['channel_name'].str.contains("agency", na=False, case=False)].copy()
        agency_fees_df['mapping_key'] = agency_fees_df['channel_name'].str.replace(" agency", "", regex=True, flags=re.IGNORECASE).str.lower().str.strip()
        direct_media_spend_df = media_spend_df[~media_spend_df['channel_name'].str.contains("agency", na=False, case=False)].copy()
        direct_media_spend_df['mapping_key'] = direct_media_spend_df['channel_name'].str.replace(" media", "", regex=True, flags=re.IGNORECASE).str.lower().str.strip()
        monthly_spend = pd.merge(direct_media_spend_df, agency_fees_df[['date', 'mapping_key', 'value']], on=['date', 'mapping_key'], how='left', suffixes=('_media', '_agency'))
        monthly_spend['value_agency'] = monthly_spend['value_agency'].fillna(0)
        monthly_spend['total_spend'] = monthly_spend['value_media'] + monthly_spend['value_agency']

        try:
            overrides_df = pd.read_csv("spend_overrides.csv")
            overrides_df['month'] = pd.to_datetime(overrides_df['month'])
            overrides_df['channel'] = overrides_df['channel'].str.replace(" agency", "", regex=True, flags=re.IGNORECASE).str.lower().str.strip()
            monthly_spend['month'] = monthly_spend['date'].dt.to_period('M').dt.to_timestamp()
            monthly_spend = pd.merge(monthly_spend, overrides_df, left_on=['month', 'mapping_key'], right_on=['month', 'channel'], how='left')
            monthly_spend['total_spend'] = np.where(monthly_spend['total_spend'] == 0, monthly_spend['spend_override'], monthly_spend['total_spend'])
            monthly_spend.drop(columns=['month', 'channel', 'spend_override'], inplace=True)
            monthly_spend['total_spend'].fillna(0, inplace=True)
        except FileNotFoundError:
            st.sidebar.warning("`spend_overrides.csv` not found. Spend gap not patched.")

        monthly_revenue = topsheet_df[topsheet_df['metric'].str.contains("NET SALES -", na=False)].copy()
        monthly_revenue['mapping_key'] = monthly_revenue['metric'].str.replace("NET SALES - ", "", regex=False).str.strip().str.lower()
        monthly_performance = pd.merge(monthly_spend[['date', 'mapping_key', 'total_spend']], monthly_revenue[['date', 'mapping_key', 'value']], on=['date', 'mapping_key'], how='left')
        monthly_performance.rename(columns={'value': 'net_revenue'}, inplace=True)
        monthly_performance['net_revenue'] = monthly_performance['net_revenue'].fillna(0)
        monthly_performance['monthly_roas'] = monthly_performance.apply(lambda row: row['net_revenue'] / row['total_spend'] if row['total_spend'] > 0 else 0, axis=1)
        new_cust_df['mapping_key'] = new_cust_df['channel_name'].str.lower().replace({'affiliate': 'affiliates'})
        monthly_cac_df = pd.merge(monthly_spend[['date', 'mapping_key', 'total_spend']], new_cust_df[['date', 'mapping_key', 'value']], on=['date', 'mapping_key'], how='left')
        monthly_cac_df.rename(columns={'value': 'new_customers'}, inplace=True)
        monthly_cac_df['new_customers'] = monthly_cac_df['new_customers'].fillna(0)
        monthly_cac_df['monthly_cac'] = monthly_cac_df.apply(lambda row: row['total_spend'] / row['new_customers'] if row['new_customers'] > 0 else 0, axis=1)
        monthly_trends_df = pd.merge(monthly_performance, monthly_cac_df[['date', 'mapping_key', 'monthly_cac']], on=['date', 'mapping_key'], how='left')
        channels_to_plot = ['paid search', 'paid social', 'affiliates']
        monthly_trends_df = monthly_trends_df[monthly_trends_df['mapping_key'].isin(channels_to_plot)]

        analysis_end_date = pd.to_datetime('2025-05-01')
        media_spend_capped = media_spend_df[media_spend_df['date'] < analysis_end_date].copy()
        new_cust_capped = new_cust_df[new_cust_df['date'] < analysis_end_date].copy()
        agency_fees_capped = media_spend_capped[media_spend_capped['channel_name'].str.contains("Agency", na=False, case=False)].copy()
        agency_fees_capped['mapping_key'] = agency_fees_capped['channel_name'].str.replace(" Agency", "", regex=True, flags=re.IGNORECASE).str.lower().str.strip()
        total_agency_fees = agency_fees_capped.groupby('mapping_key')['value'].sum()
        direct_media_spend_capped = media_spend_capped[~media_spend_capped['channel_name'].str.contains("Agency", na=False, case=False)].copy()
        direct_media_spend_capped['mapping_key'] = direct_media_spend_capped['channel_name'].str.replace(" Media", "", regex=True, flags=re.IGNORECASE).str.lower().str.strip()
        total_media_spend = direct_media_spend_capped.groupby('mapping_key')['value'].sum()
        total_spend_agg = total_media_spend.add(total_agency_fees, fill_value=0)
        total_new_customers = new_cust_capped.groupby('mapping_key')['value'].sum()
        cac_df = pd.DataFrame({'total_spend': total_spend_agg, 'total_new_customers': total_new_customers})
        cac_df['cac'] = cac_df.apply(lambda r: r['total_spend'] / r['total_new_customers'] if r['total_new_customers'] > 0 else 0, axis=1)
        cac_df = cac_df[cac_df['cac'] > 0].reset_index().rename(columns={'mapping_key': 'channel'})

        new_cust_df['customer_type'] = 'New'
        ext_cust_df['customer_type'] = 'Existing'
        all_cust_df = pd.concat([new_cust_df, ext_cust_df])
        all_cust_df['date'] = pd.to_datetime(all_cust_df['date'])
        all_cust_capped = all_cust_df[all_cust_df['date'] < analysis_end_date]
        cust_composition_df = all_cust_capped.groupby(['date', 'customer_type'])['value'].sum().unstack().fillna(0)
        new_cust_acq_df = new_cust_capped.groupby('channel_name')['value'].sum().sort_values(ascending=False).reset_index()

        total_revenue_kpi = roas_df['total_revenue'].sum()
        total_spend_kpi = roas_df[roas_df['true_total_ad_spend'] > 0]['true_total_ad_spend'].sum()
        blended_roas_kpi = total_revenue_kpi / total_spend_kpi if total_spend_kpi > 0 else 0
        total_new_cust_kpi = cac_df['total_new_customers'].sum()
        blended_cac_kpi = cac_df['total_spend'].sum() / total_new_cust_kpi if total_new_cust_kpi > 0 else 0

        kpi_data = {
            "total_revenue": total_revenue_kpi,
            "blended_roas": blended_roas_kpi,
            "blended_cac": blended_cac_kpi,
            "total_new_customers": total_new_cust_kpi
        }

        return roas_df, monthly_trends_df, cac_df, cust_composition_df, new_cust_acq_df, kpi_data

    except Exception as e:
        st.error(f"An error occurred during main data processing: {e}")
        return None, None, None, None, None, None

@st.cache_data
def process_email_data(email_file):
    try:
        email_df = pd.read_csv(email_file)
        email_df['send_date'] = pd.to_datetime(email_df['send_date'])
        email_df['cost'] = email_df['sends'] * 0.005
        flow_summary = email_df.groupby('flow_name').agg(
            total_revenue=('revenue', 'sum'),
            total_cost=('cost', 'sum')
        ).reset_index()
        flow_summary['roas'] = flow_summary.apply(
            lambda row: row['total_revenue'] / row['total_cost'] if row['total_cost'] > 0 else 0,
            axis=1
        )
        return flow_summary
    except Exception as e:
        st.error(f"An error occurred during email data processing: {e}")
        return None

# --- Custom Plotly Theme ---
import plotly.io as pio

CUSTOM_PLOTLY_TEMPLATE = dict(
    layout= dict(
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=16, color="#e6e9f0"),
        paper_bgcolor="#232b39",
        plot_bgcolor="#232b39",
        title=dict(font=dict(size=22, color="#f5f6fa", family="Inter, Segoe UI, Arial, sans-serif")),
        xaxis=dict(
            gridcolor="#2e3a4e",
            zerolinecolor="#4b6cb7",
            linecolor="#4b6cb7",
            tickcolor="#bfc9da",
            title_font=dict(size=16, color="#bfc9da"),
            tickfont=dict(size=14, color="#bfc9da"),
        ),
        yaxis=dict(
            gridcolor="#2e3a4e",
            zerolinecolor="#4b6cb7",
            linecolor="#4b6cb7",
            tickcolor="#bfc9da",
            title_font=dict(size=16, color="#bfc9da"),
            tickfont=dict(size=14, color="#bfc9da"),
        ),
        legend=dict(
            bgcolor="rgba(24,28,36,0.85)",
            bordercolor="#4b6cb7",
            borderwidth=1,
            font=dict(size=14, color="#e6e9f0"),
            orientation="h",
            x=0.5, xanchor="center", y=1.08
        ),
        margin=dict(l=40, r=30, t=60, b=40),
        hoverlabel=dict(
            bgcolor="#232b39",
            bordercolor="#4b6cb7",
            font_size=14,
            font_family="Inter, Segoe UI, Arial, sans-serif"
        ),
        colorway=["#4b6cb7", "#00b894", "#fdcb6e", "#e17055", "#00cec9", "#a29bfe", "#fd79a8"],
        bargap=0.18,
        bargroupgap=0.08,
        shapes=[
            # Rounded rectangle background for charts (visual effect)
            dict(
                type="rect",
                xref="paper", yref="paper",
                x0=0, y0=0, x1=1, y1=1,
                line=dict(width=0),
                fillcolor="#232b39",
                layer="below"
            )
        ]
    )
)
pio.templates["dtc_dark"] = CUSTOM_PLOTLY_TEMPLATE
pio.templates.default = "dtc_dark"

# --- Plotting Functions ---
def plot_corrected_roas(df):
    roas_chart_data = df[df['true_total_ad_spend'] > 0].sort_values('corrected_roas', ascending=True)
    fig = px.bar(
        roas_chart_data, x='corrected_roas', y='marketing_channel', orientation='h',
        title='Corrected ROAS by Channel',
        labels={'corrected_roas': 'Corrected ROAS', 'marketing_channel': 'Marketing Channel'},
        text='corrected_roas', color='corrected_roas',
        color_continuous_scale=px.colors.sequential.Plasma
    )
    fig.update_traces(
        texttemplate='$%{text:.2f}',
        textposition='outside',
        marker=dict(line=dict(width=1.5, color="#181c24"), opacity=0.92),
        hoverlabel=dict(bgcolor="#181c24", font_color="#fff")
    )
    fig.update_layout(
        showlegend=False,
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor="#232b39",
        paper_bgcolor="#232b39",
        bargap=0.18,
        margin=dict(l=60, r=30, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        hovermode="y unified"
    )
    return fig

def plot_monthly_roas_trends(df):
    fig = px.line(
        df, x='date', y='monthly_roas', color='mapping_key', markers=True,
        title='Monthly ROAS Trend for Key Paid Channels',
        labels={'date': 'Month', 'monthly_roas': 'Monthly ROAS', 'mapping_key': 'Channel'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.add_hline(y=1, line_dash="dash", line_color="#fdcb6e", annotation_text="Breakeven (ROAS = 1)", annotation_position="top left")
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=10, line=dict(width=2, color="#232b39")),
        hoverlabel=dict(bgcolor="#181c24", font_color="#fff")
    )
    fig.update_layout(
        plot_bgcolor="#232b39",
        paper_bgcolor="#232b39",
        xaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        yaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        margin=dict(l=60, r=30, t=60, b=40),
        hovermode="x unified"
    )
    return fig

def plot_overall_cac(df):
    df_sorted = df.sort_values('cac', ascending=True)
    fig = px.bar(
        df_sorted, x='cac', y='channel', orientation='h',
        title='Overall CAC by Channel',
        labels={'cac': 'Overall CAC ($)', 'channel': 'Channel'},
        text='cac', color='cac',
        color_continuous_scale=px.colors.sequential.Magma
    )
    fig.update_traces(
        texttemplate='$%{text:.2f}',
        textposition='outside',
        marker=dict(line=dict(width=1.5, color="#181c24"), opacity=0.92),
        hoverlabel=dict(bgcolor="#181c24", font_color="#fff")
    )
    fig.update_layout(
        showlegend=False,
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor="#232b39",
        paper_bgcolor="#232b39",
        bargap=0.18,
        margin=dict(l=60, r=30, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        hovermode="y unified"
    )
    return fig

def plot_monthly_cac_trends(df):
    fig = px.line(
        df, x='date', y='monthly_cac', color='mapping_key', markers=True,
        title='Monthly CAC Trend',
        labels={'date': 'Month', 'monthly_cac': 'Monthly CAC ($)', 'mapping_key': 'Channel'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=10, line=dict(width=2, color="#232b39")),
        hoverlabel=dict(bgcolor="#181c24", font_color="#fff")
    )
    fig.update_layout(
        plot_bgcolor="#232b39",
        paper_bgcolor="#232b39",
        xaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        yaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        margin=dict(l=60, r=30, t=60, b=40),
        hovermode="x unified"
    )
    return fig

def plot_customer_composition(df):
    fig = px.area(
        df, x=df.index, y=['New', 'Existing'],
        title='Monthly Active Customers: New vs. Existing',
        labels={'date': 'Month', 'value': 'Number of Customers', 'variable': 'Customer Type'},
        color_discrete_sequence=["#4b6cb7", "#fdcb6e"]
    )
    fig.update_traces(
        line=dict(width=0.5),
        hoverlabel=dict(bgcolor="#181c24", font_color="#fff"),
        opacity=0.92
    )
    fig.update_layout(
        plot_bgcolor="#232b39",
        paper_bgcolor="#232b39",
        xaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        yaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        margin=dict(l=60, r=30, t=60, b=40),
        hovermode="x unified"
    )
    return fig

def plot_new_customer_acquisition(df):
    df_sorted = df.sort_values('value', ascending=True)
    fig = px.bar(
        df_sorted, x='value', y='channel_name', orientation='h',
        title='Top Channels for New Customer Acquisition',
        labels={'value': 'Total New Customers Acquired', 'channel_name': 'Channel'},
        text='value', color='value',
        color_continuous_scale=px.colors.sequential.Teal
    )
    fig.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        marker=dict(line=dict(width=1.5, color="#181c24"), opacity=0.92),
        hoverlabel=dict(bgcolor="#181c24", font_color="#fff")
    )
    fig.update_layout(
        showlegend=False,
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor="#232b39",
        paper_bgcolor="#232b39",
        bargap=0.18,
        margin=dict(l=60, r=30, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        hovermode="y unified"
    )
    return fig

def create_wholesale_dummy_data():
    np.random.seed(42)
    num_rows = 30
    retailers = ['Big Box Store', 'Boutique XYZ', 'Online Marketplace', 'Dept Store']
    data = {'retailer': np.random.choice(retailers, num_rows), 'sku': [f'SKU{100+i}' for i in range(num_rows)], 'units_ordered': np.random.randint(100, 500, size=num_rows), 'units_sold': np.random.randint(50, 400, size=num_rows), 'on_hand': np.random.randint(20, 200, size=num_rows), 'wholesale_dollars': np.random.randint(5000, 20000, size=num_rows)}
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
    fig = px.scatter(
        df, x="sell_through_pct", y="net_margin_pct", size="wholesale_dollars", color="retailer",
        hover_name="sku", title="Wholesale Performance: Sell-Through vs. Net Margin",
        labels={"sell_through_pct": "Sell-Through %", "net_margin_pct": "Net Margin %", "wholesale_dollars": "Wholesale Revenue ($)"},
        template="dtc_dark", color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(
        marker=dict(line=dict(width=2, color="#181c24"), opacity=0.92),
        hoverlabel=dict(bgcolor="#181c24", font_color="#fff")
    )
    fig.update_layout(
        xaxis_tickformat='.0%',
        yaxis_tickformat='.0%',
        plot_bgcolor="#232b39",
        paper_bgcolor="#232b39",
        margin=dict(l=60, r=30, t=60, b=40),
        hovermode="closest"
    )
    return fig

def plot_persona_distribution(df):
    persona_counts = df['persona'].value_counts().reset_index()
    persona_counts.columns = ['persona', 'count']
    fig = px.bar(
        persona_counts, x='count', y='persona', orientation='h',
        title='Customer Distribution by Persona',
        labels={'count': 'Number of Customers', 'persona': 'Persona'},
        color='count', color_continuous_scale=px.colors.sequential.Plasma
    )
    fig.update_traces(
        marker=dict(line=dict(width=1.5, color="#181c24"), opacity=0.92),
        hoverlabel=dict(bgcolor="#181c24", font_color="#fff"),
        text='count', texttemplate='%{text:,}', textposition='outside'
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="#232b39",
        paper_bgcolor="#232b39",
        bargap=0.18,
        margin=dict(l=60, r=30, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        hovermode="y unified"
    )
    return fig

def plot_email_roas(df):
    df_sorted = df.sort_values('roas', ascending=True)
    fig = px.bar(
        df_sorted, x='roas', y='flow_name', orientation='h',
        title='Email Flow Return on Ad Spend (ROAS)',
        labels={'roas': 'Return on Ad Spend (ROAS)', 'flow_name': 'Email Flow'},
        text='roas', color='roas', color_continuous_scale=px.colors.sequential.Greens
    )
    fig.update_traces(
        texttemplate='$%{text:.2f}',
        textposition='outside',
        marker=dict(line=dict(width=1.5, color="#181c24"), opacity=0.92),
        hoverlabel=dict(bgcolor="#181c24", font_color="#fff")
    )
    fig.update_layout(
        showlegend=False,
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor="#232b39",
        paper_bgcolor="#232b39",
        bargap=0.18,
        margin=dict(l=60, r=30, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor="#2e3a4e"),
        hovermode="y unified"
    )
    return fig

# --- Main Content ---
if page in ["❓ Executive Summary", "👥 Who is driving my growth?", "🌍 Where is that growth coming from?"]:
    if all([marketing_file, media_spend_file, topsheet_file, new_cust_file, ext_cust_file]):
        result = load_and_process_data(
            marketing_file, media_spend_file, topsheet_file, new_cust_file, ext_cust_file
        )
        if result:
            roas_df, monthly_trends_df, cac_df, cust_composition_df, new_cust_acq_df, kpi_data = result

            if page == "❓ Executive Summary":
                st.header("Executive Summary")

                # --- Attractive Overall Summary Card ---
                st.markdown("""
                <div style="
                    background: linear-gradient(120deg, #232b39 60%, #4b6cb7 100%);
                    border-radius: 18px;
                    box-shadow: 0 4px 24px rgba(75,108,183,0.18);
                    padding: 2.2rem 2rem 1.2rem 2rem;
                    margin-bottom: 2.2rem;
                    color: #e6e9f0;
                    font-size: 1.18rem;
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                ">
                    <b>📊 Dashboard At-a-Glance</b><br>
                    <ul style="margin: 1em 0 0 1.2em; padding: 0;">
                        <li><b>Growth Drivers:</b> See which channels and personas are fueling your business growth.</li>
                        <li><b>Channel Efficiency:</b> Instantly compare ROAS and CAC across all paid channels.</li>
                        <li><b>Customer Mix:</b> Track the balance between new and existing customers for sustainable growth.</li>
                        <li><b>Email & Wholesale:</b> Review high-level email flow performance and wholesale readiness.</li>
                        <li><b>Product Strategy:</b> (Coming soon) Get ready for actionable product and pricing insights.</li>
                    </ul>
                    <div style="margin-top:1.2em; color:#bfc9da; font-size:1.05rem;">
                        <i>Use the navigation to explore each area in detail. This summary gives you a quick pulse on your business health and marketing effectiveness.</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- KPIs ---
                st.markdown("""
                <div style="display:flex; flex-wrap:wrap; gap:1.5em; margin-bottom:1.5em;">
                    <div style="flex:1; min-width:180px; background:rgba(75,108,183,0.18); border-radius:14px; padding:1.2em 1em; text-align:center;">
                        <div style="font-size:1.2em; font-weight:700; color:#4b6cb7;">${:,.0f}</div>
                        <div style="color:#bfc9da;">Total Revenue</div>
                    </div>
                    <div style="flex:1; min-width:180px; background:rgba(75,108,183,0.18); border-radius:14px; padding:1.2em 1em; text-align:center;">
                        <div style="font-size:1.2em; font-weight:700; color:#00b894;">{:.2f}x</div>
                        <div style="color:#bfc9da;">Blended ROAS</div>
                    </div>
                    <div style="flex:1; min-width:180px; background:rgba(75,108,183,0.18); border-radius:14px; padding:1.2em 1em; text-align:center;">
                        <div style="font-size:1.2em; font-weight:700; color:#fdcb6e;">${:.2f}</div>
                        <div style="color:#bfc9da;">Blended CAC</div>
                    </div>
                    <div style="flex:1; min-width:180px; background:rgba(75,108,183,0.18); border-radius:14px; padding:1.2em 1em; text-align:center;">
                        <div style="font-size:1.2em; font-weight:700; color:#e17055;">{:,.0f}</div>
                        <div style="color:#bfc9da;">Total New Customers</div>
                    </div>
                </div>
                """.format(
                    kpi_data['total_revenue'],
                    kpi_data['blended_roas'],
                    kpi_data['blended_cac'],
                    kpi_data['total_new_customers']
                ), unsafe_allow_html=True)

                # --- Generalized High-Level Summaries for Each Tab ---
                st.markdown("""
                <div style="margin-top:2.2em; margin-bottom:1.2em;">
                    <div style="display:flex; flex-wrap:wrap; gap:1.2em;">
                        <div style="flex:1; min-width:220px; background:rgba(75,108,183,0.10); border-radius:12px; padding:1.1em;">
                            <b>👥 Who is driving my growth?</b><br>
                            <span style="color:#bfc9da;">Top personas and channels are identified for targeted acquisition and retention.</span>
                        </div>
                        <div style="flex:1; min-width:220px; background:rgba(75,108,183,0.10); border-radius:12px; padding:1.1em;">
                            <b>🌍 Where is that growth coming from?</b><br>
                            <span style="color:#bfc9da;">Compare channel performance and efficiency at a glance.</span>
                        </div>
                        <div style="flex:1; min-width:220px; background:rgba(75,108,183,0.10); border-radius:12px; padding:1.1em;">
                            <b>📧 Email Performance</b><br>
                            <span style="color:#bfc9da;">See which email flows are delivering the best ROI.</span>
                        </div>
                        <div style="flex:1; min-width:220px; background:rgba(75,108,183,0.10); border-radius:12px; padding:1.1em;">
                            <b>🛍️ Wholesale Shell</b><br>
                            <span style="color:#bfc9da;">Wholesale analytics framework is ready for your retailer data.</span>
                        </div>
                        <div style="flex:1; min-width:220px; background:rgba(75,108,183,0.10); border-radius:12px; padding:1.1em;">
                            <b>📦 What should I be selling?</b><br>
                            <span style="color:#bfc9da;">Product and pricing insights will be available once data is provided.</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")

                st.subheader("The 'Leaky Bucket' Problem")
                st.markdown(
                    """
                    <div style="font-size:1.08rem; color:#bfc9da; margin-bottom:1.2em;">
                        <b>What is the 'Leaky Bucket' Problem?</b><br>
                        Imagine your business as a bucket: <b>new customers</b> are water pouring in, while <b>existing customers</b> are water you want to keep. 
                        If you only focus on acquiring new customers but don't retain existing ones, your bucket will always be leaking—making it hard to grow sustainably.<br><br>
                        <b>Why does it matter?</b><br>
                        • <b>High churn</b> means you must spend more to replace lost customers.<br>
                        • <b>Healthy growth</b> comes from both acquiring new customers and keeping existing ones engaged.<br>
                        • <b>Tracking the mix</b> helps you spot if your growth is real or just replacing lost customers.<br><br>
                        <b>How to use this chart:</b><br>
                        • <span style="color:#4b6cb7;">Blue area</span>: New customers acquired each month.<br>
                        • <span style="color:#fdcb6e;">Yellow area</span>: Existing customers returning.<br>
                        • <b>Goal:</b> Grow both areas over time, not just one!
                    </div>
                    """, unsafe_allow_html=True
                )
                st.plotly_chart(plot_customer_composition(cust_composition_df), use_container_width=True)

            elif page == "👥 Who is driving my growth?":
                st.header("👥 Customer Analysis: Personas & Segments")
                st.markdown("""
                <div style="font-size:1.1rem; color:#bfc9da; margin-bottom:1.5em;">
                    <b>Summary:</b> Identify which customer segments and personas are fueling your growth. Analyze acquisition channels and persona distribution to optimize targeting and retention.
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                col1.metric("Total New Customers", f"{kpi_data['total_new_customers']:,.0f}")
                col2.metric("Top Acquisition Channel", f"{new_cust_acq_df.iloc[0]['channel_name']}" if not new_cust_acq_df.empty else "N/A")

                st.subheader("Monthly Active Customers: New vs. Existing")
                st.plotly_chart(plot_customer_composition(cust_composition_df), use_container_width=True)
                st.subheader("Top Channels for New Customer Acquisition")
                st.plotly_chart(plot_new_customer_acquisition(new_cust_acq_df), use_container_width=True)
                st.markdown("---")
                st.header("Persona Analysis")
                if persona_file:
                    personas_df = pd.read_csv(persona_file)
                    persona_list = ['All Personas'] + sorted(personas_df['persona'].unique().tolist())
                    selected_persona = st.selectbox("Filter by Persona:", persona_list)
                    if selected_persona != 'All Personas':
                        display_personas_df = personas_df[personas_df['persona'] == selected_persona]
                    else:
                        display_personas_df = personas_df
                    st.plotly_chart(plot_persona_distribution(display_personas_df), use_container_width=True)
                    st.dataframe(display_personas_df)
                else:
                    st.info("Upload the `customer_personas.csv` file to view persona analysis.")

            elif page == "🌍 Where is that growth coming from?":
                st.header("🌍 Channel Analysis: Performance & Tactics")
                st.markdown("""
                <div style="font-size:1.1rem; color:#bfc9da; margin-bottom:1.5em;">
                    <b>Summary:</b> Evaluate which marketing channels deliver the best return on investment and lowest acquisition costs. Use these insights to optimize your marketing mix.
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                top_roas_channel = roas_df.iloc[0]['marketing_channel'] if not roas_df.empty else "N/A"
                top_roas_value = roas_df.iloc[0]['corrected_roas'] if not roas_df.empty else 0
                col1.metric("Top ROAS Channel", f"{top_roas_channel}", f"{top_roas_value:.2f}x")
                lowest_cac_channel = cac_df.sort_values('cac').iloc[0]['channel'] if not cac_df.empty else "N/A"
                lowest_cac_value = cac_df.sort_values('cac').iloc[0]['cac'] if not cac_df.empty else 0
                col2.metric("Lowest CAC Channel", f"{lowest_cac_channel}", f"${lowest_cac_value:.2f}")

                tab1, tab2 = st.tabs(["Return on Ad Spend (ROAS)", "Customer Acquisition Cost (CAC)"])
                with tab1:
                    spend_gaps = monthly_trends_df[monthly_trends_df['total_spend'] <= 0]
                    if not spend_gaps.empty:
                        st.error("🚨 Data Gap: One or more channels has $0 spend in a recent month after patching.")
                        with st.expander("Show rows with data gaps"):
                            st.dataframe(spend_gaps[['date', 'mapping_key', 'total_spend']])
                    st.subheader("Corrected Return on Ad Spend (ROAS) by Channel")
                    st.plotly_chart(plot_corrected_roas(roas_df), use_container_width=True)
                    st.subheader("Monthly ROAS Trend for Key Paid Channels")
                    st.plotly_chart(plot_monthly_roas_trends(monthly_trends_df), use_container_width=True)
                with tab2:
                    st.subheader("Overall Customer Acquisition Cost (CAC) by Channel")
                    st.plotly_chart(plot_overall_cac(cac_df), use_container_width=True)
                    st.subheader("Monthly CAC Trend for Key Paid Channels")
                    st.plotly_chart(plot_monthly_cac_trends(monthly_trends_df), use_container_width=True)
    else:
        st.info("Please upload all 5 required CSV files using the sidebar to begin the analysis.")
        st.image("https://i.imgur.com/3_3.png", caption="Upload files to start", use_container_width=True)

elif page == "📧 Email Performance":
    st.header("📧 Email-Flow Performance Module")
    st.markdown("""
    <div style="font-size:1.1rem; color:#bfc9da; margin-bottom:1.5em;">
        <b>Summary:</b> Analyze the Return on Ad Spend (ROAS) for each email campaign and identify top-performing flows.
    </div>
    """, unsafe_allow_html=True)
    if email_file:
        email_roas_df = process_email_data(email_file)
        if email_roas_df is not None:
            st.plotly_chart(plot_email_roas(email_roas_df), use_container_width=True)
            with st.expander("View Raw Email Performance Data"):
                email_file.seek(0)  # <-- Add this line
                st.dataframe(pd.read_csv(email_file))
    else:
        st.info("Upload the `email_flow_performance.csv` file to view this analysis.")

elif page == "🛍️ Wholesale Shell":
    st.header("🛍️ Wholesale Shell: Framework Demo")
    st.markdown("""
    <div style="font-size:1.1rem; color:#bfc9da; margin-bottom:1.5em;">
        <b>Summary:</b> This module demonstrates the KPI and visualization framework for wholesale data. Once retailer feeds are available, this section will provide actionable insights for wholesale performance.
    </div>
    """, unsafe_allow_html=True)
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
    <div style="font-size:1.1rem; color:#bfc9da; margin-bottom:1.5em;">
        <b>Summary:</b> This section of the dashboard is designed to answer critical questions about your product strategy. However, the necessary data and analysis have not yet been provided.
    </div>
    **To complete this view, we need data cuts that can help us understand:**
    - **Product-level LTV:** Which SKUs bring back high-value buyers?
    - **Attachment Rate / Bundle Behavior:** What else are customers buying with top sellers?
    - **Product Performance by Acquisition Channel:** Do some products attract better personas via specific channels?
    - **Discount Reliance:** Which SKUs can carry full price versus those that rely on promotions?

    Once this data is available, we can build out the following analyses:
    - **Product Strategy Dashboard:** Classifying products into `Core Drivers`, `Test & Learn`, `Sunset Candidates`, and `Gateway SKUs`.
    - **Cross-Sell & Bundle Opportunities.**
    - **Pricing & Promotion Strategy Recommendations.**
    """, unsafe_allow_html=True)
    st.info("Please provide the relevant data exports (e.g., sales by SKU, order line items) to populate this section.", icon="ℹ️")