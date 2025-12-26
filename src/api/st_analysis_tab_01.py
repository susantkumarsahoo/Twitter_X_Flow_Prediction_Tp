import streamlit as st
import pandas as pd
import plotly.express as px
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
from src.api.url_api import fastapi_api_request_url, flask_api_request_url
from src.visualization.st_plt import plot_complaint_pie_chart, visualize_report
from src.api.st_analysis_tab_helper import complaint_report_dashboard
from src.constants.paths import dataset_path

logger = get_logger(__name__)


def display_complaint_information():
    st.subheader("📊 Complaint Information")
    
    try:
        with st.spinner("🔄 Fetching complaint data from FastAPI..."):
            # Fetch data from FastAPI
            response = fastapi_api_request_url("/read_complaint_counts", timeout=30)
            responce_01 = flask_api_request_url("/all_data_report", timeout=30)
            
            col1, col2, col3, col4, col5, col6 = st.columns(6)


            with col1:
                st.metric(label="Total Complaints", value=0)


            with col2:
                st.metric(label="Open Complaints", value=0)


            with col3:
                st.metric(label="Closed/Open Complaints", value=0)

            with col4:
                st.metric(label="90 Day Open Complaints", value=0)


            with col5:
                st.metric(label="Avg FRT Time", value=0)


            with col6:
                st.metric(label="High Priority", value=0)            
            
            if response.status_code == 200:
                # Convert JSON dictionary back to Series → DataFrame
                data_dict = response.json()
                complaint_counts = pd.Series(data_dict).sort_values(ascending=False)
                complaint_df = complaint_counts.reset_index()
                complaint_df.columns = ["Complaint Type", "Count"]
                
                st.success("✅ Data loaded successfully from FastAPI!")


                complaint_report_dashboard(complaint_df)

                logger.info("Complaint data loaded from FastAPI")
                        
            else:
                raise CustomException(f"Failed to fetch data. Status code: {response.status_code}")            

            st.divider()

            # Pie chart visualization
            pie_chart = plot_complaint_pie_chart(dataset_path, column_name='COMPLAINT TYPE')
            st.plotly_chart(pie_chart, use_container_width=True)

            st.divider()

            st.divider()

            # ===============================
            # All Data Report
            # ===============================
            st.write("## 📊 All Data Report")

            all_data_report = pd.DataFrame(responce_01.json())

            st.dataframe(
                all_data_report,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # ===============================
            # Interactive Filters
            # ===============================
            st.write("## 🔍 Filter & Visualize Data")

            available_categories = sorted(all_data_report["Category"].unique())

            selected_category = st.selectbox(
                "Select Category",
                available_categories,
                index=0
            )

            top_n = st.slider(
                "Select Top N Records",
                min_value=5,
                max_value=30,
                value=12,
                step=1
            )

            st.divider()

            # ===============================
            # Visualization
            # ===============================
            filtered_df = all_data_report[
                all_data_report["Category"] == selected_category
            ]

            if filtered_df.empty:
                st.warning("No data available for the selected category.")
            else:
                fig = visualize_report(
                    report_df=all_data_report,
                    category=selected_category,
                    top_n=top_n
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    theme="streamlit"
                )

                # ===============================
                # Filtered Data View
                # ===============================
                st.write("### 📋 Filtered Data Preview")

                st.dataframe(
                    filtered_df.sort_values("Count", ascending=False).head(top_n),
                    use_container_width=True,
                    hide_index=True
                )

            st.divider()

            st.info(
                "⚠️ This dashboard is under active development. "
                "Advanced analytics and AI-driven insights will be added soon."
            )

    except CustomException as ce:
        logger.error(str(ce))
        st.error(f"❌ {str(ce)}")
    except Exception as e:
        logger.exception("Unexpected error in display_complaint_information")
        st.error("❌ An unexpected error occurred while loading complaint information")
        with st.expander("🔍 Show error details"):
            st.code(str(e))