import os
import sys
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
from src.constants.paths import dataset_path
from plotly.subplots import make_subplots
from src.api.url_api import fastapi_api_request_url, flask_api_request_url
from src.api.st_analysis_tab_01 import display_complaint_information
from src.api.st_helper import complaint_overview_dashboard

logger = get_logger(__name__)


# streamlit_app.py

def analysis_dashboard(
    dashboard_type: str,
    dataset_path: str,
    uploaded_file: Optional[object] = None,
) -> None:
    """
    Render the selected dashboard.

    Parameters:
        dashboard_type (str): Selected dashboard option
        dataset_path (str): Path to the default dataset
        uploaded_file (Optional[object]): Optional user-uploaded file
    """

    # Page Title
    st.title(dashboard_type)

    # ==================================================
    # ANALYSIS DASHBOARD
    # ==================================================
    if dashboard_type == "📈 Analysis Dashboard":
        
        df = None
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_excel(dataset_path)
        
        if df is None:
            st.warning("⚠️ No data available. Please upload a file or check the default dataset path.")
            return

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "📈 Complaint Overview",
                "📋 Data Table",
                "📊 Summary",
                "🔍 Dataset Information",
                "📊 Visualizations",
            ]
        )

        # ----------------------------------------------
        # TAB 1: COMPLAINT OVERVIEW
        # ----------------------------------------------

        with tab1:
            st.subheader("Complaint Overview")

            # Under development notice
            st.warning("🚧 Complaint Overview dashboard is under development.")

            st.divider()

            display_complaint_information()

            st.divider()

            # Complaint overview dashboard
            logger.info("Complaint overview dashboard rendered.")

            # --------------------------------------------------
            # Quick Links Section
            # --------------------------------------------------
            st.warning("🚧 Visualizations dashboard is under development.")

            st.markdown("### 🔗 Quick Links")

            quick_option = st.selectbox(
                "Choose a feature to explore:",
                [
                    "Select an option",
                    "Consumer History",
                    "Consumer Ledger",
                    "Consumer Bill Wise Balances",
                    "Bill Calculator",
                    "Adhoc Reports",
                ],
            )

            if quick_option != "Select an option":
                st.info(f"📄 **{quick_option}** feature is under development.")
            


        # ----------------------------------------------
        # TAB 5: VISUALIZATIONS
        # ----------------------------------------------
        with tab5:
            st.subheader("Data Visualizations")
            # under development
            st.warning("🚧 Data Visualizations dashboard is under development.")


        # ----------------------------------------------
        # WEB APP: UNDER DEVELOPMENT
        # ----------------------------------------------

    else:
        st.info(f"🚧 {dashboard_type} is under development. Coming soon!")
        
        # Placeholder content
        with st.expander("📋 Planned Features"):
            st.markdown(f"""
            ### {dashboard_type}
            
            This dashboard will include:
            - Advanced analytics features
            - Interactive visualizations
            - Real-time data processing
            - Machine learning models
            - Export capabilities
            
            **Status:** In Development
            **Expected Release:** Q1 2025
            """)

            



 