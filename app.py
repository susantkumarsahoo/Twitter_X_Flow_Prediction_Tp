import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
from src.streamlit.st_analyst import analysis_dashboard
from src.constants.paths import dataset_path
from datetime import datetime, timedelta

# app.py

API_URL = "http://localhost:8000"

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
            "📊 Mathematics & Statistical Analysis",
            "🔮 Twitter Flow Prediction",
            "🕒 Time Series Analysis",
            "📝 Sentiment Analysis",
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
#Analysis Dashboard
analysis_dashboard(dashboard_type, dataset_path)




