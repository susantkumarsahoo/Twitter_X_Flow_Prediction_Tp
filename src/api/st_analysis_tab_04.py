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


def display_dataset_info():
    """
    Display dataset information by fetching data from the FastAPI endpoint.
    
    This function:
    - Fetches dataset info from /read_dataset_info endpoint
    - Displays the information in JSON format
    - Handles errors with detailed error messages
    
    Returns:
        None
    """
    st.subheader("Dataset Information")
    
    try:
        with st.spinner("📊 Loading dataset info..."):     
            response = fastapi_api_request_url("/read_dataset_info", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                st.json(data)
            else:
                st.error(f"❌ Error loading dataset info: {response.text}")
            
        logger.info("Dataset info loaded")

    except CustomException as ce:
        logger.error(f"CustomException in Complaint Info: {ce}")
        st.error("❌ A custom error occurred while loading dataset info.")
        with st.expander("Show error details"):
            st.code(str(ce))                        
                
    except Exception as e:
        st.error(f"❌ Error loading dataset info: {e}")
        with st.expander("Show error details"):
            st.code(str(e))
        logger.info("Dataset info loaded")