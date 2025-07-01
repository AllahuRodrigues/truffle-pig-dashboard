# dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Load Data
df = pd.read_csv("preprocessed_data_clean.csv")
df.columns = df.columns.str.lower().str.strip()
df['month'] = pd.to_datetime(df['month'])

# Create metrics
df['ltv'] = df['total_revenue'] / df['new_customers'].replace(0, pd.NA)
df['cac'] = df['total_spend'] / df['new_customers'].replace(0, pd.NA)
df['roas'] = df['total_revenue'] / df['total_spend'].replace(0, pd.NA)
df['net_revenue'] = df['total_revenue'] - df['returns_value_dist'] - df['technology_spend']
df['return_rate'] = df['returns_value_dist'] / df['total_revenue'].replace(0, pd.NA)

# Sidebar filters
st.sidebar.title("🔍 Filters")
channel_filter = st.sidebar.multiselect("Select Channels", options=df['channel'].unique(), default=list(df['channel'].unique()))
date_range = st.sidebar.slider("Select Date Range", min_value=df['month'].min().date(), max_value=df['month'].max().date(), value=(df['month'].min().date(), df['month'].max().date()))

# Filter Data
df = df[(df['channel'].isin(channel_filter)) & (df['month'].dt.date.between(*date_range))]

# -------------------------
# 1. Overview Page
# -------------------------
st.title("📊 Full-Cycle Marketing Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${df['total_revenue'].sum():,.0f}")
col2.metric("Total Spend", f"${df['total_spend'].sum():,.0f}")
col3.metric("Total Orders", f"{df['total_orders'].sum():,.0f}")

st.subheader("📈 Revenue vs Spend Over Time")
monthly = df.groupby('month')[['total_revenue', 'total_spend']].sum().reset_index()
fig1 = px.line(monthly, x='month', y=['total_revenue', 'total_spend'], title="Revenue vs Spend Over Time")
st.plotly_chart(fig1)

# -------------------------
# 2. LTV, CAC, Repeat Orders
# -------------------------
st.subheader("🧠 Who Is Driving Growth?")
ltv = df.groupby('channel')['ltv'].mean().reset_index()
fig2 = px.bar(ltv, x='channel', y='ltv', title="Avg LTV by Channel")
st.plotly_chart(fig2)

cac = df.groupby('channel')['cac'].mean().reset_index()
fig3 = px.bar(cac, x='channel', y='cac', title="Avg CAC by Channel")
st.plotly_chart(fig3)

repeat = df.groupby('channel')['existing_customer_orders'].sum().reset_index()
fig4 = px.bar(repeat, x='channel', y='existing_customer_orders', title="Repeat Orders by Channel")
st.plotly_chart(fig4)

# -------------------------
# 3. Channel Efficiency
# -------------------------
st.subheader("💸 Channel Efficiency")
agg = df.groupby('channel')[['ltv', 'cac', 'roas', 'total_spend']].mean().reset_index()
fig5 = px.scatter(agg, x='cac', y='roas', size='total_spend', color='channel',
                  hover_name='channel', title="ROAS vs CAC by Channel (Bubble Size = Spend)")
st.plotly_chart(fig5)

st.dataframe(agg.style.format({"ltv": "${:.2f}", "cac": "${:.2f}", "roas": "{:.2f}", "total_spend": "${:.0f}"}))

# -------------------------
# 4. Profitability & Returns
# -------------------------
st.subheader("📦 What’s Working?")
net_rev = df.groupby('channel')['net_revenue'].sum().reset_index()
fig6 = px.bar(net_rev, x='channel', y='net_revenue', title="Net Revenue by Channel")
st.plotly_chart(fig6)

returns = df.groupby('channel')['return_rate'].mean().reset_index()
fig7 = px.bar(returns, x='channel', y='return_rate', title="Return Rate by Channel")
st.plotly_chart(fig7)
