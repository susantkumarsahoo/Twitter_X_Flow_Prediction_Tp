import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.constants.paths import dataset_path
import requests
import json

# src/streamlit/st_analyst.py
API_URL = "http://localhost:8000"

def analysis_dashboard(dashboard_type: str, dataset_path: str) -> None:
    """
    Render the Analysis Dashboard if selected.
    
    Parameters:
        dashboard_type (str): The selected dashboard option.
        dataset_path (str): Path to the dataset file.
    """
    # Show the dashboard title directly
    st.title(dashboard_type)

    # ---------------- Analysis Dashboard ----------------
    if dashboard_type == "📈 Analysis Dashboard":
        st.markdown("### Dashboard Content")
        tab1, tab2, tab3 = st.tabs(["📈 Data Visualizations", "📋 Data Table", "📊 Summary"])

        with tab1:
            st.subheader("Missing Values Analysis")

            # Call the API and get the response
            fig_plt = requests.get(f"{API_URL}/figure_plt")
                
            st.plotly_chart(fig_plt.json(), use_container_width=True)
            
        with tab2:
            st.subheader("Data Table")


        with tab3:
            st.subheader("Summary Statistics")
