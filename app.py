import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from src.utils.streamlit_helper import sales_distribution_plots, display_sales_summary, fetch_all_data

API_URL = "http://localhost:8000"

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better sidebar styling
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR CONFIGURATION
# ============================================

with st.sidebar:
    st.title("📊 Dashboard Control Panel")
    st.markdown("---")
    
    # ========== MAIN NAVIGATION ==========
    st.header("🧭 Navigation")
    dashboard_type = st.radio(
        "Select Dashboard",
        ["📈 Analysis Dashboard", "📊 Statistical Dashboard", "🔮 Prediction Dashboard"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    
    # ========== DATA SOURCE CONFIGURATION ==========
    st.header("📁 Data Source")
    data_source = st.selectbox(
        "Data Source Type",
        ["Upload File", "Database Connection", "API Endpoint", "Sample Data"]
    )
    
    if data_source == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload your data",
            type=['csv', 'xlsx', 'json'],
            help="Supported formats: CSV, Excel, JSON"
        )
    elif data_source == "Database Connection":
        db_type = st.selectbox("Database Type", ["PostgreSQL", "MySQL", "MongoDB", "SQLite"])
        st.text_input("Connection String", type="password")
    elif data_source == "API Endpoint":
        st.text_input("API URL")
        st.text_input("API Key", type="password")
    
    st.markdown("---")
    
    # ========== DATE RANGE FILTER ==========
    st.header("📅 Date Range")
    date_filter_type = st.radio(
        "Filter Type",
        ["Preset Range", "Custom Range"],
        horizontal=True
    )
    
    if date_filter_type == "Preset Range":
        preset = st.selectbox(
            "Select Period",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"]
        )
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("To", datetime.now())
    
    st.markdown("---")
    
    # ========== DASHBOARD-SPECIFIC FEATURES ==========
    if "Analysis" in dashboard_type:
        st.header("🔍 Analysis Options")
        analysis_type = st.multiselect(
            "Select Analysis Types",
            ["Trend Analysis", "Comparative Analysis", "Cohort Analysis", "Funnel Analysis", "Segmentation"],
            default=["Trend Analysis"]
        )
        
        metrics = st.multiselect(
            "Key Metrics",
            ["Revenue", "Users", "Conversions", "Engagement", "Retention", "Churn"],
            default=["Revenue", "Users"]
        )
        
        grouping = st.selectbox(
            "Group By",
            ["Day", "Week", "Month", "Quarter", "Year"]
        )
    
    elif "Statistical" in dashboard_type:
        st.header("📐 Statistical Options")
        stat_methods = st.multiselect(
            "Statistical Methods",
            ["Descriptive Statistics", "Correlation Analysis", "Hypothesis Testing", 
             "Distribution Analysis", "Outlier Detection", "Time Series Decomposition"],
            default=["Descriptive Statistics"]
        )
        
        confidence_level = st.slider(
            "Confidence Level (%)",
            min_value=90,
            max_value=99,
            value=95,
            step=1
        )
        
        visualization = st.selectbox(
            "Primary Visualization",
            ["Box Plot", "Histogram", "Scatter Plot", "Heatmap", "QQ Plot"]
        )
    
    elif "Prediction" in dashboard_type:
        st.header("🔮 Prediction Options")
        model_type = st.selectbox(
            "Model Type",
            ["Linear Regression", "Time Series (ARIMA)", "Random Forest", 
             "XGBoost", "Neural Network", "Ensemble"]
        )
        
        forecast_horizon = st.slider(
            "Forecast Horizon (days)",
            min_value=1,
            max_value=365,
            value=30,
            step=1
        )
        
        features = st.multiselect(
            "Feature Selection",
            ["Historical Data", "Seasonality", "External Factors", "Trends", "Cyclical Patterns"],
            default=["Historical Data", "Seasonality"]
        )
        
        st.checkbox("Enable Auto-tuning", value=True)
        st.checkbox("Show Confidence Intervals", value=True)
    
    st.markdown("---")
    
    # ========== FILTERS ==========
    st.header("🔧 Filters")
    with st.expander("Advanced Filters", expanded=False):
        category_filter = st.multiselect(
            "Categories",
            ["Category A", "Category B", "Category C", "Category D"]
        )
        
        region_filter = st.multiselect(
            "Regions",
            ["North America", "Europe", "Asia", "South America", "Africa"]
        )
        
        value_range = st.slider(
            "Value Range",
            min_value=0,
            max_value=1000,
            value=(0, 1000)
        )
    
    st.markdown("---")
    
    # ========== VISUALIZATION SETTINGS ==========
    st.header("🎨 Visualization")
    chart_theme = st.selectbox(
        "Theme",
        ["Default", "Dark", "Light", "Colorblind-Friendly"]
    )
    
    chart_types = st.multiselect(
        "Chart Types",
        ["Line Chart", "Bar Chart", "Area Chart", "Pie Chart", "Scatter Plot", "Heatmap"],
        default=["Line Chart", "Bar Chart"]
    )
    
    show_legend = st.checkbox("Show Legend", value=True)
    show_grid = st.checkbox("Show Grid", value=True)
    
    st.markdown("---")
    
    # ========== EXPORT OPTIONS ==========
    st.header("💾 Export")
    export_format = st.selectbox(
        "Export Format",
        ["PDF Report", "Excel Workbook", "CSV Data", "JSON", "PowerPoint"]
    )
    
    if st.button("📥 Export Dashboard", use_container_width=True):
        st.success("Export initiated! Download will start shortly.")
    
    st.markdown("---")
    
    # ========== SETTINGS & INFO ==========
    with st.expander("⚙️ Settings"):
        st.checkbox("Auto-refresh Data", value=False)
        refresh_interval = st.number_input("Refresh Interval (seconds)", min_value=10, max_value=3600, value=60)
        st.checkbox("Enable Notifications", value=True)
        st.checkbox("Dark Mode", value=False)
    
    with st.expander("ℹ️ Info"):
        st.info("""
        **Dashboard Version:** 2.0
        
        **Last Updated:** {}
        
        **Data Points:** -
        
        **Status:** ✅ Connected
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    
    st.markdown("---")
    st.caption("© 2024 Analytics Dashboard | v2.0")

# ============================================
# MAIN CONTENT AREA
# ============================================

st.title(dashboard_type.split(" ")[1] + " " + dashboard_type.split(" ")[2])

# Display selected configuration
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Data Source", data_source)
with col2:
    st.metric("Active Filters", "0")
with col3:
    st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))

st.info("👈 Use the sidebar to configure your dashboard settings and filters")

# Placeholder for dashboard content
st.markdown("### Dashboard Content")
st.write("Your visualizations and analysis will appear here based on sidebar configurations.")

# Sample visualization placeholder
tab1, tab2, tab3 = st.tabs(["📈 Visualizations", "📋 Data Table", "📊 Summary"])

with tab1:
    st.write("Charts and graphs will be displayed here")

with tab2:
    st.write("Raw data table will be displayed here")

with tab3:
    st.write("Summary statistics will be displayed here")