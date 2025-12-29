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

            df = pd.read_excel(dataset_path)
            total_rows, total_columns = df.shape
            status_counts = df['CLOSED/OPEN'].value_counts()
            closed_complaints = status_counts.get('Closed', 0)
            open_complaints = status_counts.get('Open', 0)
            ninety_days_ago = pd.Timestamp.now() - pd.Timedelta(days=90)    
            df['90_DAY_OPEN_COMPLAINTS'] = ( (df['DATE'] >= ninety_days_ago) & (df['CLOSED/OPEN'] == 'Open') )
            ninety_day_open_count = df['90_DAY_OPEN_COMPLAINTS'].sum()
            thrty_days_ago = pd.Timestamp.now() - pd.Timedelta(days=30)
            df['30_DAY_OPEN_COMPLAINTS'] = ( (df['DATE'] >= thrty_days_ago) & (df['CLOSED/OPEN'] == 'Open') )
            thrty_days_ago = df['30_DAY_OPEN_COMPLAINTS'].sum()
            df['DATE'] = pd.to_datetime(df['DATE'])
            last_date = df['DATE'].max()
            last_day_rows = df[df['DATE'] == last_date]
            counts = last_day_rows['DATE'].value_counts()
            total_count = counts.sum()

            with col1:
                st.metric(label="Total Complaints", value=total_rows)
               
            with col2:
                st.metric(label="Open Complaints", value=open_complaints)

            with col3:
                st.metric(label="Closed Complaints", value=closed_complaints)
            with col4:
                st.metric(label="90 Day Open Complaints", value=ninety_day_open_count)

            with col5:
                st.metric(label="30 Day Open Complaints", value=thrty_days_ago) 

            with col6:
                st.metric(label="Last Day Complaints", value=counts)           
            
            if response is None:
                st.error("❌ Backend API is not responding")
                return

            if response.status_code == 200:
                            
                             
                # Convert JSON dictionary back to Series → DataFrame
                data_dict = response.json()
                complaint_counts = pd.Series(data_dict).sort_values(ascending=False)
                complaint_df = complaint_counts.reset_index()
                complaint_df.columns = ["Complaint Type", "Count"]
                
                st.success("✅ Data loaded successfully from API!")


                complaint_report_dashboard(complaint_df)

                logger.info("Complaint data loaded from FastAPI")
                        
            else:
                raise CustomException(f"Failed to fetch data. Status code: {response.status_code}")   
                     
            st.divider()

            st.divider()
            st.write("## 📊 Data Distributions")
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
            st.write("## 🔍 All Data & Visualization")

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

                st.divider()

                # ===============================
                # Filtered Data View
                # ===============================
                st.write("### 📋 Data Report Preview")

                st.dataframe(
                    filtered_df.sort_values("Count", ascending=False).head(top_n),
                    use_container_width=True,
                    hide_index=True
                )

            st.divider()

            st.info(
                "⚠️ This application is under active development. "
                "Advanced analytics and AI-driven insights will be available soon."
            )


    except CustomException as ce:
        logger.error(str(ce))
        st.error(f"❌ {str(ce)}")
    except Exception as e:
        logger.exception("Unexpected error in display_complaint_information")
        st.error("❌ An unexpected error occurred while loading complaint information")
        with st.expander("🔍 Show error details"):
            st.code(str(e))