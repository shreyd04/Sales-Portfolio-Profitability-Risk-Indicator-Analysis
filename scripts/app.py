import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Jio Institute: Digital Ecosystem Risk Tracker", layout="wide")
st.title("🛡️ Portfolio Profitability & Behavioral Risk Indicator")

# --- DATA LOADING WITH DYNAMIC PATHING ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Points to processed_sales_risk.csv in the root directory
data_path = os.path.join(current_dir, '..', 'processed_sales_risk.csv')

@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"❌ Data file not found. Please run 'python scripts/data_pipeline.py' first.")
        st.stop()
    return pd.read_csv(path)

df = load_data(data_path)

# --- SIDEBAR: CONSUMER SEGMENTATION ---
st.sidebar.header("Target Ecosystem Filters")
available_segments = df['segment'].unique()
segment = st.sidebar.multiselect("Select Consumer Segment", available_segments, default=["Home Office"])
filtered_df = df[df['segment'].isin(segment)]

# --- EXECUTIVE KPIS ---
col1, col2, col3 = st.columns(3)
with col1:
    avg_margin = filtered_df['margin_pct'].mean()
    st.metric(label="Systemic Margin %", value=f"{avg_margin:.2f}%", delta="-15% Erosion Detected")

with col2:
    high_risk_revenue = filtered_df[filtered_df['leakage_flag'] == 1]['sales'].sum()
    st.metric(label="Revenue at Risk (INR/USD)", value=f"${high_risk_revenue:,.2f}")

with col3:
    elasticity_score = filtered_df['discount'].corr(filtered_df['quantity'])
    st.metric(label="Discount Elasticity", value=f"{elasticity_score:.3f}")

# --- AI INSIGHT SECTION (Jio Institute Specific) ---
st.info(f"**Behavioral Insight:** The selected segments show an Elasticity Score of **{elasticity_score:.3f}**. "
        "A score near zero indicates that discounts are failing to drive volume, leading to the observed margin leakage.")

# --- VISUALIZATION ---
st.subheader("Financial Leakage Map: Discount vs. Profitability")
fig = px.scatter(filtered_df, x="discount", y="profit", color="category", 
                 size="sales", hover_data=['sub_category'],
                 color_discrete_sequence=px.colors.qualitative.Bold)

fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Breakeven Point")
st.plotly_chart(fig, use_container_width=True)