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


def display_summary_statistics(dataset_path):
    """
    Display comprehensive dataset summary statistics including shape, memory usage,
    data types distribution, column details, and descriptive statistics.
    
    Args:
        dataset_path (str): Path to the Excel dataset file
        
    Returns:
        None
        
    Features:
        - Dataset shape and memory usage metrics
        - Data types distribution with visualization
        - Detailed column information
        - Descriptive statistics for numeric columns
        - CSV download option for statistics
    """
    st.subheader("Dataset Summary Statistics")
    
    try:
        with st.spinner("📊 Loading summary statistics..."):
            # Load dataset
            df = pd.read_excel(dataset_path)
            
            # Basic info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Shape", f"{df.shape[0]} × {df.shape[1]}")
            
            with col2:
                memory_mb = df.memory_usage(deep=True).sum() / 1024**2
                st.metric("Memory Usage", f"{memory_mb:.2f} MB")
            
            with col3:
                st.metric("Data Types", len(df.dtypes.unique()))
            
            st.divider()
            
            # Column types breakdown
            st.write("**Column Data Types Distribution:**")
            dtype_counts = df.dtypes.value_counts()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart of data types
                import plotly.express as px
                fig = px.bar(
                    x=dtype_counts.index.astype(str),
                    y=dtype_counts.values,
                    labels={'x': 'Data Type', 'y': 'Count'},
                    title='Data Types Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Show counts
                st.dataframe(
                    pd.DataFrame({
                        'Type': dtype_counts.index.astype(str),
                        'Count': dtype_counts.values
                    }),
                    hide_index=True,
                    use_container_width=True
                )
            
            st.divider()
            
            # Detailed column info
            st.write("**Column Details:**")
            dtype_df = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.values.astype(str),
                "Non-Null Count": df.count().values,
                "Null Count": df.isnull().sum().values
            })
            
            st.dataframe(dtype_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Numeric statistics
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(numeric_cols) > 0:
                st.write("**Descriptive Statistics (Numeric Columns):**")
                
                # Transpose for better readability
                desc_stats = df[numeric_cols].describe().T
                st.dataframe(desc_stats, use_container_width=True)
                
                # Download button
                csv = desc_stats.to_csv()
                st.download_button(
                    label="📥 Download Statistics as CSV",
                    data=csv,
                    file_name=f"statistics_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )
            else:
                st.info("ℹ️ No numeric columns found in the dataset.")
            
        logger.info("Dataset summary statistics loaded")
    
    except FileNotFoundError:
        st.error(f"❌ Dataset file not found: {dataset_path}")
        st.info("Please check the dataset path in your configuration.")

    except CustomException as ce:
        logger.error(f"CustomException in Complaint Info: {ce}")
        st.error("❌ A custom error occurred while loading dataset info.")
        with st.expander("Show error details"):
            st.code(str(ce))
    
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        with st.expander("Show error details"):
            st.code(str(e))
        logger.info("Dataset loaded")