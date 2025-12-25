import streamlit as st
import pandas as pd
import plotly.express as px
from src.logging.logger import get_logger
from src.exceptions.exception import CustomException
from src.api.url_api import fastapi_api_request_url
from src.visualization.st_plt import plot_complaint_pie_chart
from src.constants.paths import dataset_path

logger = get_logger(__name__)

def display_complaint_information():
    st.subheader("📊 Complaint Information")
    
    try:
        with st.spinner("🔄 Fetching complaint data from FastAPI..."):
            # Fetch data from FastAPI
            response = fastapi_api_request_url("/read_complaint_counts", timeout=30)
            
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

        st.info("⚠️ This project is under development. Please wait for the next release.")
            
    except CustomException as ce:
        logger.error(str(ce))
        st.error(f"❌ {str(ce)}")
    except Exception as e:
        logger.exception("Unexpected error in display_complaint_information")
        st.error("❌ An unexpected error occurred while loading complaint information")
        with st.expander("🔍 Show error details"):
            st.code(str(e))

