import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px



# streamlit run app.py
# API_URL = "http://localhost:8000"

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
    st.markdown(
        """
        <div style="border: 2px solid blue; padding: 10px; border-radius: 8px; text-align: center;">
            <h2 style="color: #1E90FF;">📊 Twitter X Control Panel</h2>
        </div>
        <hr>
        """,
        unsafe_allow_html=True
    )    
 
    # ========== MAIN NAVIGATION ==========
    st.header("🧭 CRM Navigation")

    dashboard_type = st.radio(
        "Select Dashboard",
        [
            "📈 Analysis Dashboard",
            "📊 Statistical Dashboard",
            "🔮 Twitter Flow Prediction Dashboard",
            "🤖 AI Chatbot"
        ],
        label_visibility="collapsed"
    )
    # ========== DATA SOURCE CONFIGURATION ==========
    st.header("📁 Data Source")

    # Only manual file upload
    uploaded_file = st.file_uploader(
        "Upload your data manually",
        type=['csv', 'xlsx', 'json'],
        help="Supported formats: CSV, Excel, JSON"
    )

    # Optional: show confirmation if file uploaded
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
with st.sidebar:
    
    # ========== SETTINGS & INFO ==========
    
    with st.expander("ℹ️ Info"):
        st.info("""
        **Dashboard Version:** 2.0
        
        **Last Updated:** {}
        
        **Data Points:** -
        
        **Status:** ✅ Connected
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    
    st.caption("© 2024 Analytics Dashboard | v2.0")

# ============================================
# MAIN CONTENT AREA
# ============================================

# ============================================
# MAIN CONTENT AREA
# ============================================

# Show the dashboard title directly
st.title(dashboard_type)

# ---------------- Analysis Dashboard ----------------
if dashboard_type == "📈 Analysis Dashboard":
    st.markdown("### Dashboard Content")
    tab1, tab2, tab3 = st.tabs(["📈 Visualizations", "📋 Data Table", "📊 Summary"])

    with tab1:
        st.write("Charts and graphs will be displayed here")

    with tab2:
        st.write("Raw data table will be displayed here")

    with tab3:
        st.write("Summary statistics will be displayed here")

# ---------------- Statistical Dashboard ----------------
elif dashboard_type == "📊 Statistical Dashboard":
    st.markdown("### Statistical Insights")
    tab1, tab2 = st.tabs(["📊 Descriptive Stats", "📉 Advanced Models"])

    with tab1:
        st.write("Descriptive statistics and distributions will be displayed here")

    with tab2:
        st.write("Advanced statistical models and tests will be displayed here")

# ---------------- Twitter Flow Prediction Dashboard ----------------
elif dashboard_type == "🔮 Twitter Flow Prediction Dashboard":
    st.markdown("### Twitter Flow Predictions")
    tab1, tab2 = st.tabs(["🔮 Predictions", "📊 Trend Analysis"])

    with tab1:
        st.write("Prediction results will be displayed here")

    with tab2:
        st.write("Trend analysis and sentiment graphs will be displayed here")

# ---------------- AI Chatbot ----------------
elif dashboard_type == "🤖 AI Chatbot":
    st.markdown("### Chatbot Interface")
    st.chat_input("Ask me anything...")
    st.write("Chat responses will appear here")
  