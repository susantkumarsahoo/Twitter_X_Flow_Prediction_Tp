import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from typing import Optional
import time

from src.logging.logger import get_logger
from src.exceptions.exception import CustomException

logger = get_logger(__name__)

FASTAPI_URL = "http://localhost:8000"
FLASK_URL = "http://localhost:5000"

def fastapi_api_request_url(endpoint: str, timeout: int = 30, max_retries: int = 3):
    """
    Make API request with retry logic
    
    Parameters:
        endpoint: API endpoint to call
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    
    Returns:
        Response object or None if failed
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{FASTAPI_URL}{endpoint}", timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏱️ Request timeout. Retrying... (Attempt {attempt + 2}/{max_retries})")
                time.sleep(2)
            else:
                st.error(f"⏱️ Request timed out after {max_retries} attempts.")
                return None
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Please ensure the FastAPI server is running.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request error: {e}")
            return None
    
    return None

def flask_api_request_url(endpoint: str, timeout: int = 30, max_retries: int = 3):
    """
    Make API request with retry logic
    
    Parameters:
        endpoint: API endpoint to call
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    
    Returns:
        Response object or None if failed
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{FLASK_URL}{endpoint}", timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏱️ Request timeout. Retrying... (Attempt {attempt + 2}/{max_retries})")
                time.sleep(2)
            else:
                st.error(f"⏱️ Request timed out after {max_retries} attempts.")
                return None
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Please ensure the FastAPI server is running.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request error: {e}")
            return None
    
    return None



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
        
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Complaint Info", "📋 Data Table", "📊 Summary", "🔍 Dataset Info"])
        
        # ============================================
        # TAB 1: VISUALIZATION
        # ============================================
                # ============================================
        with tab1:
            st.subheader("Complaint Information")

            try:
                with st.spinner("📊 Loading dataset info..."):
                    response = flask_api_request_url("/complaint_report", timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        st.json(data)   # <-- renders dict nicely
                    else:
                        st.error(f"❌ Error loading dataset info: {response.text}")

            except Exception as e:
                st.error(f"❌ Error loading dataset info: {e}")
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
                                    return 'background-color: #ffcccc'  # Red
                                elif val >= 25:
                                    return 'background-color: #ffffcc'  # Yellow
                                else:
                                    return 'background-color: #ccffcc'  # Green
                            
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
                    
                    except Exception as e:
                        st.error(f"❌ Error processing data: {e}")
                        with st.expander("Show error details"):
                            st.code(str(e))
        
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
            
            except FileNotFoundError:
                st.error(f"❌ Dataset file not found: {dataset_path}")
                st.info("Please check the dataset path in your configuration.")
            
            except Exception as e:
                st.error(f"❌ Error loading dataset: {e}")
                with st.expander("Show error details"):
                    st.code(str(e))
        # ============================================
        # DATASET INFO
        # ============================================ 
        with tab4:
            st.subheader("Dataset Information")
            
            try:
                with st.spinner("📊 Loading dataset info..."):     
                    response = fastapi_api_request_url("/read_dataset_info", timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.json(data)   # <-- renders dict nicely
                    else:
                        st.error(f"❌ Error loading dataset info: {response.text}")
                        
            except Exception as e:
                st.error(f"❌ Error loading dataset info: {e}")
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