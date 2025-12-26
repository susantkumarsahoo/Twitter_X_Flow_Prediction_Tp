import streamlit as st
import pandas as pd
import plotly.express as px
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
from src.api.url_api import fastapi_api_request_url, flask_api_request_url
from src.visualization.st_plt import plot_complaint_pie_chart, visualize_report
from src.constants.paths import dataset_path

logger = get_logger(__name__)


def display_complaint_information():
    st.subheader("📊 Complaint Information")
    
    try:
        with st.spinner("🔄 Fetching complaint data from FastAPI..."):
            # Fetch data from FastAPI
            response = fastapi_api_request_url("/read_complaint_counts", timeout=30)
            response_01 = flask_api_request_url("/all_data_report", timeout=30)
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            with col1:
                st.metric(label="Total Complaints", value=0)

            with col2:
                st.metric(label="Open Complaints", value=0)

            with col3:
                st.metric(label="Closed Complaints", value=0)

            with col4:
                st.metric(label="In Progress", value=0)

            with col5:
                st.metric(label="Avg Resolution Time", value=0)

            with col6:
                st.metric(label="High Priority", value=0)            
            
            if response.status_code == 200:
                # Convert JSON dictionary back to Series → DataFrame
                data_dict = response.json()
                complaint_counts = pd.Series(data_dict).sort_values(ascending=False)
                complaint_df = complaint_counts.reset_index()
                complaint_df.columns = ["Complaint Type", "Count"]
                
                st.success("✅ Data loaded successfully from FastAPI!")
                
                # Display as table and chart
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Raw Counts")
                    st.dataframe(complaint_df, use_container_width=True)
                with col2:
                    st.write("Visual Report")
                    fig = px.bar(
                        complaint_df,
                        x="Complaint Type",
                        y="Count",
                        title="Complaint Counts",
                        text_auto=True,
                        color="Count",
                        color_continuous_scale="Blues"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                            
            else:
                raise CustomException(f"Failed to fetch data. Status code: {response.status_code}")            

            st.divider()

            # Pie chart visualization
            pie_chart = plot_complaint_pie_chart(dataset_path, column_name='COMPLAINT TYPE')
            st.plotly_chart(pie_chart, use_container_width=True)

            st.divider()

            # ===============================
            # All Data Report
            # ===============================
            st.write("## 📊 All Data Report")

            # Convert API JSON response to DataFrame
            all_data_report = pd.DataFrame(response_01.json())

            st.dataframe(
                all_data_report,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "DIVISION": st.column_config.SelectboxColumn("Division Filter"),
                    "CLOSED/OPEN": st.column_config.SelectboxColumn("Status Filter"),
                }
            )


            st.divider()

            # ===============================
            # All Data Visualization
            # ===============================
            st.write("## 📊 All Data Visualization")

            fig = visualize_report(
                report_df=all_data_report,
                category="DEPT",
                top_n=12
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                theme="streamlit"
            )

            st.divider()

            st.info(
                "⚠️ This module is under active development. Enhanced analytics and "
                "additional visualizations will be available in the next release."
            )

    except CustomException as ce:
        logger.error(str(ce))
        st.error(f"❌ {str(ce)}")
    except Exception as e:
        logger.exception("Unexpected error in display_complaint_information")
        st.error("❌ An unexpected error occurred while loading complaint information")
        with st.expander("🔍 Show error details"):
            st.code(str(e))