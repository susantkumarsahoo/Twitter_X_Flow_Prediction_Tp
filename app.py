import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard", layout="wide")

API_URL = "http://localhost:8000"

# Sidebar
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
    st.title("📈 Sales Analysis")
    
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
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Sales by Category")
        fig2 = px.bar(x=list(category_stats.keys()), 
                      y=list(category_stats.values()),
                      labels={'x': 'Category', 'y': 'Total Sales'},
                      title='Category Performance')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Data table
    st.subheader("Raw Data")
    st.dataframe(df, use_container_width=True, height=300)

# Page 2: Statistical Calculation
elif page == "Statistical Calculation":
    st.title("📊 Statistical Calculations")
    
    st.subheader("Overall Statistics")
    col1, col2 = st.columns(2)
    
    # Pre-calculate statistics
    sales_mean = df['sales'].mean()
    sales_median = df['sales'].median()
    sales_std = df['sales'].std()
    sales_var = df['sales'].var()
    sales_min = df['sales'].min()
    sales_max = df['sales'].max()
    sales_q25 = df['sales'].quantile(0.25)
    sales_q50 = df['sales'].quantile(0.50)
    sales_q75 = df['sales'].quantile(0.75)
    
    with col1:
        st.write("**Sales Statistics:**")
        st.write(f"- Mean: ${sales_mean:.2f}")
        st.write(f"- Median: ${sales_median:.2f}")
        st.write(f"- Std Dev: ${sales_std:.2f}")
        st.write(f"- Variance: ${sales_var:.2f}")
    
    with col2:
        st.write("**Range & Quartiles:**")
        st.write(f"- Min: ${sales_min}")
        st.write(f"- 25th Percentile: ${sales_q25:.2f}")
        st.write(f"- 50th Percentile: ${sales_q50:.2f}")
        st.write(f"- 75th Percentile: ${sales_q75:.2f}")
        st.write(f"- Max: ${sales_max}")
    
    # Category-wise statistics (cached)
    st.subheader("Category-wise Statistics")
    category_stats_df = df.groupby('category')['sales'].agg([
        ('Count', 'count'),
        ('Total', 'sum'),
        ('Average', 'mean'),
        ('Min', 'min'),
        ('Max', 'max'),
        ('Std Dev', 'std')
    ]).round(2)
    st.dataframe(category_stats_df, use_container_width=True)
    
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