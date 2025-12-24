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



def display_visualizations(dataset_path):
    """
    Display comprehensive data visualizations including complaints data, missing values,
    time series trends, and unique values analysis.
    
    Args:
        dataset_path (str): Path to the dataset file
        
    Returns:
        None
        
    Features:
        - Static complaints data visualization
        - Interactive Plotly visualization
        - Missing values chart
        - Time series trend analysis
        - Complaints status stacked bar chart
        - Unique values bar chart
    """
    st.subheader("Visualization")

    try:
        with st.spinner("📊 Loading Visualization..."):
            # Static visualization
            fig_01 = process_complaints_data(dataset_path)
            st.plotly_chart(fig_01, use_container_width=True)
            logger.info("Static visualization loaded")

            st.divider()

            # Interactive Plotly visualization
            fig_02 = create_complaints_visualization(dataset_path)
            st.plotly_chart(fig_02, use_container_width=True)
            logger.info("Interactive visualization loaded")

            st.divider()
            
            # Missing values visualization
            fig_03 = create_missing_values_chart(dataset_path)
            if fig_03 is not None:
                st.plotly_chart(fig_03, use_container_width=True)
                logger.info("Missing values visualization loaded")
            else:
                st.info("ℹ️ No missing values found in the dataset.")
                logger.info("No missing values to visualize")

            st.divider()

            # Time series visualization
            fig_04 = complaints_trend_line(dataset_path)
            fig_05 = complaints_status_stacked_bar(dataset_path)
            if fig_04 is not None and fig_05 is not None:
                st.plotly_chart(fig_04, use_container_width=True)
                st.plotly_chart(fig_05, use_container_width=True)
                logger.info("Time series visualization loaded")
            else:
                st.info("ℹ️ No time series data found in the dataset.")
                logger.info("No time series data to visualize")

            st.divider()

            # Unique values visualization
            fig_06 = unique_value_bar_chart(dataset_path)
            if fig_06 is not None:
                st.plotly_chart(fig_06, use_container_width=True)
                logger.info("Unique values visualization loaded")
            else:
                st.info("ℹ️ No unique values found in the dataset.")
                logger.info("No unique values to visualize")

            logger.info("Visualization loaded")

    except CustomException as ce:
        logger.error("CustomException in Visualization", exc_info=True)
        st.error("❌ A custom error occurred while loading visualization.")
        with st.expander("Show error details"):
            st.code(str(ce))

    except Exception as e:
        logger.exception("Unhandled error in visualization")
        st.error("❌ Error loading visualization.")
        with st.expander("Show error details"):
            st.code(str(e))