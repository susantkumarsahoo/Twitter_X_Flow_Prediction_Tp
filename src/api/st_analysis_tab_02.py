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

from src.api.st_analysis_tab_02 import display_missing_values_report



logger = get_logger(__name__)

FASTAPI_URL = "http://localhost:8000"
FLASK_URL = "http://localhost:5000"



def display_missing_values_report():
    """
    Display a comprehensive missing values report with metrics and visualizations.
    
    This function fetches missing value data from the API and displays:
    - Summary metrics (total rows, columns, missing counts)
    - Overall missing percentage progress bar
    - Detailed table with color-coded severity
    - CSV download option
    
    Returns:
        None
    """
    st.subheader("Missing Values Report")
    
    with st.spinner("🔄 Loading data..."):
        response = fastapi_api_request_url("/report_missing_values", timeout=30)
        
        if response is not None:
            try:
                report = response.json()
                
                # Display summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Total Rows", 
                        f"{report.get('total_rows', 0):,}",
                        help="Total number of rows in dataset"
                    )
                
                with col2:
                    st.metric(
                        "Total Columns", 
                        report.get('total_columns', 0),
                        help="Total number of columns in dataset"
                    )
                
                with col3:
                    cols_with_missing = report.get('columns_with_missing_values', 0)
                    st.metric(
                        "Columns with Missing", 
                        cols_with_missing,
                        help="Number of columns containing missing values"
                    )
                
                with col4:
                    total_missing = report.get('total_missing_values', 0)
                    st.metric(
                        "Total Missing", 
                        f"{total_missing:,}",
                        help="Total count of missing values"
                    )
                
                # Overall missing percentage
                overall_pct = report.get('overall_missing_percentage', 0)
                st.progress(overall_pct / 100, text=f"Overall Missing Data: {overall_pct}%")
                
                st.divider()
                
                # Display detailed table
                missing_summary = report.get("missing_values_summary", [])
                
                if missing_summary:
                    df = pd.DataFrame(missing_summary)
                    
                    # Format the dataframe
                    df = df.rename(columns={
                        "column": "Column Name",
                        "missing_count": "Missing Count",
                        "missing_percentage": "Missing %"
                    })
                    
                    # Add color-coded severity
                    def color_severity(val):
                        if val >= 50:
                            return 'background-color: #ffcccc'
                        elif val >= 25:
                            return 'background-color: #ffffcc'
                        else:
                            return 'background-color: #ccffcc'
                    
                    # Display with styling
                    st.dataframe(
                        df.style.applymap(color_severity, subset=['Missing %']),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Missing %": st.column_config.NumberColumn(
                                "Missing %",
                                format="%.2f%%"
                            ),
                            "Missing Count": st.column_config.NumberColumn(
                                "Missing Count",
                                format="%d"
                            )
                        }
                    )
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Report as CSV",
                        data=csv,
                        file_name=f"missing_values_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                    )
                else:
                    st.success("✅ No missing values found in the dataset!")
                    st.balloons()
                logger.info("missing values found in the dataset")
            except CustomException as ce:
                logger.error(f"CustomException in Complaint Info: {ce}")
                st.error("❌ A custom error occurred while loading dataset info.")
                with st.expander("Show error details"):
                    st.code(str(ce))                            
            
            except Exception as e:
                st.error(f"❌ Error processing data: {e}")
                with st.expander("Show error details"):
                    st.code(str(e))
                    logger.info("Complaint Info loaded")