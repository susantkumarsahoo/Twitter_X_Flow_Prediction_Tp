import os
import sys
import time
import requests
import pandas as pd
from typing import Optional
import streamlit as st
import plotly.graph_objects as go
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
from src.constants.paths import dataset_path
from plotly.subplots import make_subplots
from src.api.url_api import fastapi_api_request_url, flask_api_request_url
from src.visualization.st_plt import (create_complaints_visualization, process_complaints_data,create_missing_values_chart,
                                    complaints_status_stacked_bar,complaints_trend_line,unique_value_bar_chart)



logger = get_logger(__name__)

FASTAPI_URL = "http://localhost:8000"
FLASK_URL = "http://localhost:5000"


def analysis_dashboard(dashboard_type: str, dataset_path: str, uploaded_file: Optional[object] = None) -> None:
    """
    Render the selected dashboard.
    
    Parameters:
        dashboard_type: The selected dashboard option
        dataset_path: Path to the default dataset
        uploaded_file: Optional uploaded file from user
    """
    
    st.title(dashboard_type)
    
    # ============================================
    # ANALYSIS DASHBOARD
    # ============================================
    if dashboard_type == "📈 Analysis Dashboard":
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Complaint Info", "📋 Data Table", "📊 Summary", "🔍 Dataset Info",'Visualizations'])
        
        # ============================================
        # TAB 1: COMPLAINT INFORMATION
        # ============================================
        with tab1:
            st.subheader("Complaint Information")
            
            try:
                with st.spinner("📊 Loading dataset info..."):
                    response = flask_api_request_url("/complaint_report", timeout=30)
                    response_01 = fastapi_api_request_url("/apply_pivot_data", timeout=30)
                    
                    if response.status_code == 200 and response_01.status_code == 200:
                        df_main = pd.DataFrame(response)
                        df_pivot = pd.DataFrame(response_01)
                        st.dataframe(df_main)
                        st.divider()
                        st.dataframe(df_pivot)
                    else:
                        error_msg = f"Error loading dataset: {response.text}"
                        logger.error(error_msg)
                        st.error(f"❌ {error_msg}")
                        
            except CustomException as ce:
                logger.error(f"CustomException in Complaint Info: {ce}")
                st.error("❌ A custom error occurred while loading dataset info.")
                with st.expander("Show error details"):
                    st.code(str(ce))
                    
            except Exception as e:
                logger.exception("Unexpected error in Complaint Info")
                st.error("❌ An unexpected error occurred.")
                with st.expander("Show error details"):
                    st.code(str(e))