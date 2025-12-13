import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time
import numpy as np

st.set_page_config(page_title="Sales Dashboard", layout="wide")

API_URL = "http://localhost:8000"

st.title("📊 Sales Analysis Dashboard")


with st.sidebar:
    with st.echo():
        st.write("This code will be printed to the sidebar.")

    with st.spinner("Loading..."):
        time.sleep(5)
    st.success("Done!")

import streamlit as st

with st.container():
    st.write("This is inside the container")

    # You can call any Streamlit command, including custom components:
    st.bar_chart(np.random.randn(50, 3))

st.write("This is outside the container")


# Fetch data
try:
    data = requests.get(f"{API_URL}/data").json()
    summary = requests.get(f"{API_URL}/summary").json()
    category_stats = requests.get(f"{API_URL}/category-stats").json()
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"${summary['total_sales']:,}")
    col2.metric("Average Sales", f"${summary['avg_sales']:.0f}")
    col3.metric("Max Sales", f"${summary['max_sales']:,}")
    col4.metric("Min Sales", f"${summary['min_sales']:,}")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales Over Time")
        fig1 = px.line(df, x='date', y='sales', title='Daily Sales Trend')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Sales by Category")
        fig2 = px.bar(x=list(category_stats.keys()), 
                      y=list(category_stats.values()),
                      labels={'x': 'Category', 'y': 'Total Sales'},
                      title='Category Performance')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Data table
    st.subheader("Raw Data")
    st.dataframe(df, use_container_width=True)
    
except Exception as e:
    st.error(f"Error connecting to API: {e}")
    st.info("Make sure FastAPI backend is running on http://localhost:8000")