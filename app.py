import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from nicegui import ui


st.set_page_config(page_title="Sales Dashboard", layout="wide")

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Sales Dashboard - Energy Consumption", layout="wide")

# Custom header using Markdown + HTML

# Sidebar
st.sidebar.markdown(
    """
    <div style="background-color:#1E3A8A;padding:10px;border-radius:5px">
        <h3 style="color:white;text-align:center;">⚡ Energy Consumption Dashboard</h3>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("📊 Dashboard Menu")
page = st.sidebar.radio("Select Option:", ["Analysis", "Statistical Calculation"])

# Cache data fetching
@st.cache_data(ttl=300)
def fetch_all_data():
    """Fetch all data from API with caching"""
    try:
        data = requests.get(f"{API_URL}/data", timeout=5).json()
        summary = requests.get(f"{API_URL}/summary", timeout=5).json()
        category_stats = requests.get(f"{API_URL}/category-stats", timeout=5).json()
        return data, summary, category_stats, None
    except Exception as e:
        return None, None, None, str(e)

# Fetch data once
data, summary, category_stats, error = fetch_all_data()

if error:
    st.error(f"Error connecting to API: {error}")
    st.info("Make sure FastAPI backend is running on http://localhost:8000")
    st.stop()

# Convert to DataFrame once
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

# Page 1: Analysis
if page == "Analysis":


    st.markdown(
        """
        <div style="background-color:#1E3A8A;padding:10px;border-radius:5px">
            <h2 style="color:white;text-align:center;">⚡ Energy Consumption Dashboard</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.title("📈 Sales Analysis")

    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"${summary['total_sales']:,}")
    col2.metric("Average Sales", f"${summary['avg_sales']:.0f}")
    col3.metric("Max Sales", f"${summary['max_sales']:,}")
    col4.metric("Min Sales", f"${summary['min_sales']:,}")
    
# Page 2: Statistical Calculation
elif page == "Statistical Calculation":

    st.markdown(
        """
        <style>
            .top-header {
                background-color: #1E3A8A;
                padding: 15px;
                margin: 0;
                border-radius: 0;
                position: relative;
                top: -2.5em;
            }
        </style>
        <div class="top-header">
            <h2 style="color:white;text-align:center;">⚡ Energy Consumption Dashboard</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    

    st.title("📊 Statistical Calculations")

    
    st.subheader("Overall Statistics")
    col1, col2 = st.columns(2)
      
    with col1:
        st.write("**Sales Statistics:**")

    with col2:
        st.write("**Range & Quartiles:**")

    # Category-wise statistics (cached)
    st.subheader("Category-wise Statistics")

 
    # Distribution plot
    st.subheader("Sales Distribution")
    fig = px.histogram(df, x='sales', nbins=20, title='Sales Distribution')
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
    
    # Box plot
    st.subheader("Sales Box Plot by Category")
    fig2 = px.box(df, x='category', y='sales', title='Sales Distribution by Category')
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)