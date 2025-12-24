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
        # ============================================
        # TAB 2: DATA TABLE
        # ============================================
        with tab2:
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
        
        # ============================================
        # TAB 3: SUMMARY STATISTICS
        # ============================================
        with tab3:
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
        # ============================================
        # TAB 4: DATASET INFO        
        # ============================================ 
        with tab4:
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

    # ============================================
    # TAB 5: VISUALIZATION
    # ============================================

        with tab5:
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
                    fig_05 =complaints_status_stacked_bar(dataset_path)
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

    # ============================================
    # OTHER DASHBOARDS
    # ============================================
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