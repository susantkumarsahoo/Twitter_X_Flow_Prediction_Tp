import streamlit as st
import pandas as pd
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
from src.api.url_api import fastapi_api_request_url, flask_api_request_url

logger = get_logger(__name__)


def display_complaint_information():
    """
    Display complaint information by fetching data from Flask and FastAPI endpoints.
    
    This function:
    - Fetches complaint report from Flask API endpoint (/complaint_report)
    - Fetches pivot data from FastAPI endpoint (/apply_pivot_data)
    - Displays both dataframes with visualizations
    - Handles errors gracefully with detailed messages
    
    Returns:
        None
    """
    st.subheader("📊 Complaint Information")
    
    try:
        with st.spinner("🔄 Fetching complaint data from APIs..."):
            # Fetch data from both APIs
            flask_response = flask_api_request_url("/complaint_report", timeout=30)
            fastapi_response = fastapi_api_request_url("/apply_pivot_data", timeout=30)
            
            # Parse JSON responses
            flask_data = flask_response.json()
            fastapi_data = fastapi_response.json()
            
            # Convert to DataFrames
            df_complaint_report = pd.DataFrame(flask_data)
            df_pivot_data = pd.DataFrame(fastapi_data)
            
        # Display success message
        st.success("✅ Data loaded successfully!")
        
        # Display Complaint Report
        st.markdown("### 📋 Complaint Report")
        st.dataframe(
            df_complaint_report,
            use_container_width=True,
            height=400
        )
        
        # Display metrics if dataframe has data
        if not df_complaint_report.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df_complaint_report))
            with col2:
                st.metric("Total Columns", len(df_complaint_report.columns))
            with col3:
                if 'Status' in df_complaint_report.columns:
                    st.metric("Unique Statuses", df_complaint_report['Status'].nunique())
        
        st.divider()
        
        # Display Pivot Data
        st.markdown("### 📊 Pivot Analysis")
        st.dataframe(
            df_pivot_data,
            use_container_width=True,
            height=400
        )
        
        # Display pivot metrics
        if not df_pivot_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Pivot Rows", len(df_pivot_data))
            with col2:
                st.metric("Pivot Columns", len(df_pivot_data.columns))
        
        # Download buttons
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            csv_complaint = df_complaint_report.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Complaint Report (CSV)",
                data=csv_complaint,
                file_name="complaint_report.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            csv_pivot = df_pivot_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Pivot Data (CSV)",
                data=csv_pivot,
                file_name="pivot_data.csv",
                mime="text/csv",
                use_container_width=True
            )
                
    except CustomException as ce:
        logger.error(f"CustomException in Complaint Info: {ce}")
        st.error("❌ Failed to load complaint information")
        with st.expander("🔍 Show error details"):
            st.code(str(ce))
            st.info("💡 **Troubleshooting:**\n"
                   "- Check if Flask API is running on http://localhost:5000\n"
                   "- Check if FastAPI is running on http://localhost:8000\n"
                   "- Verify the endpoints /complaint_report and /apply_pivot_data exist")
            
    except ValueError as ve:
        logger.error(f"ValueError in parsing response: {ve}")
        st.error("❌ Invalid data format received from API")
        with st.expander("🔍 Show error details"):
            st.code(str(ve))
            
    except Exception as e:
        logger.exception("Unexpected error in display_complaint_information")
        st.error("❌ An unexpected error occurred while loading complaint information")
        with st.expander("🔍 Show error details"):
            st.code(str(e))