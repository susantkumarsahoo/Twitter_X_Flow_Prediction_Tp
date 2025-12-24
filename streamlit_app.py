import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
from src.constants.paths import dataset_path
from src.api.url_api import fastapi_api_request_url, flask_api_request_url, check_api_status

# streamlit_app.py

# -----------------------------------------------------------------------------
# Logger
# -----------------------------------------------------------------------------
logger = get_logger(__name__)

# -----------------------------------------------------------------------------
# Try importing custom modules
# -----------------------------------------------------------------------------
try:
    from src.backend_api.streamlit_helper import analysis_dashboard
    from src.constants.paths import dataset_path
except ImportError as e:
    logger.exception("Failed to import Streamlit helper modules")
    st.error("⚠️ Unable to import custom modules. Please check your project structure.")
    dataset_path = "data/dataset.xlsx"
    analysis_dashboard = None

# -----------------------------------------------------------------------------
# API Configuration
# -----------------------------------------------------------------------------
# API_URL = "http://localhost:8000"

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Twitter Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("🧭 Navigation")

    dashboard_type = st.radio(
        "Select Dashboard",
        [
            "📈 Analysis Dashboard",
            "📊 Mathematics & Statistical Analysis",
            "🔮 Twitter Flow Prediction",
            "🕒 Time Series Analysis",
            "📝 Sentiment Analysis",
            "🗂️ CRM Database",
            "🤖 AI Chatbot"
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.header("📁 Data Source")
    uploaded_file = st.file_uploader(
        "Upload your data",
        type=["csv", "xlsx", "json"],
    )
 
    if uploaded_file:
        logger.info("File uploaded | name=%s", uploaded_file.name)
        st.success(f"✅ '{uploaded_file.name}' uploaded!")
 
    st.divider()
 
    st.header("🔌 API Status")
    is_connected, api_data = check_api_status()
    
    if is_connected:
        st.success("✅ API Connected")
        if api_data.get("dataset_available"):
            st.info("📂 Dataset available")
        else:
            st.warning("⚠️ Dataset not found")
    else:
        st.error("❌ API Disconnected")
        with st.expander("Show error details"):
            st.code(api_data.get("message", "Unknown error"))
 
    if st.button("🔄 Refresh API Status", use_container_width=True):
        logger.info("API status refresh triggered")
        st.rerun()
 
    st.divider()
 
    with st.expander("ℹ️ Dashboard Info"):
        st.info(
            f"""
            **Version:** 2.0  
            **Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
            **Status:** {"Connected" if is_connected else "Disconnected"}  
            **Dataset:** {dataset_path}
            """
        )

# -----------------------------------------------------------------------------
# MAIN CONTENT
# -----------------------------------------------------------------------------
if not is_connected:
    st.title("⚠️ API Connection Required")
    st.error("Cannot connect to FastAPI backend. Please ensure the server is running.")
    st.info("""
    **Troubleshooting Steps:**
    1. Ensure FastAPI server is running on http://localhost:8000
    2. Check if the port 8000 is not blocked
    3. Verify API endpoint: /healthcheck
    """)
    logger.warning("Streamlit blocked due to API unavailability")
 
else:
    try:
        logger.info("Rendering dashboard | type=%s", dashboard_type)
        
        if analysis_dashboard is None:
            st.error("⚠️ Dashboard module not found. Please check import configuration.")
        else:
            analysis_dashboard(dashboard_type, dataset_path, uploaded_file)
 
    except Exception as e:
        logger.exception("Unhandled error in Streamlit dashboard")
        st.error("❌ An unexpected error occurred while loading the dashboard.")
        with st.expander("Show error details"):
            st.code(str(e))