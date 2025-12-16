import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Analytics Pro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! How can I help you analyze your data today?"}
    ]

# Sidebar Navigation
with st.sidebar:
    st.title("📊 Analytics Pro")
    st.caption("AI-Powered Platform")
    st.divider()
    
    # Main Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Overview", "📊 Analytics Dashboard", "📈 Statistical Dashboard", 
         "🔮 Prediction Engine", "🤖 AI Chatbot", "💾 Data Management", 
         "👥 User Management", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Sub-navigation based on main selection
    if page == "📊 Analytics Dashboard":
        st.subheader("Analytics Options")
        analytics_sub = st.selectbox(
            "Select Analysis Type",
            ["⚡ Real-time Analytics", "🕐 Historical Data", "📊 Comparative Analysis"]
        )
    elif page == "📈 Statistical Dashboard":
        st.subheader("Statistical Options")
        stats_sub = st.selectbox(
            "Select Statistics Type",
            ["📋 Descriptive Stats", "🔗 Correlation Analysis", "📉 Regression Models"]
        )
    elif page == "🔮 Prediction Engine":
        st.subheader("Prediction Options")
        pred_sub = st.selectbox(
            "Select Prediction Type",
            ["📅 Time Series Forecast", "📈 Trend Prediction", "⚠️ Anomaly Detection"]
        )
    elif page == "🤖 AI Chatbot":
        st.subheader("AI Options")
        ai_sub = st.selectbox(
            "Select AI Feature",
            ["💬 Chat Interface", "🧠 AI Insights", "📄 Auto Reports"]
        )
    
    st.divider()
    
    # User Profile
    st.markdown("### 👤 User Profile")
    st.write("**User Name**")
    st.caption("Administrator")

# Generate sample data
@st.cache_data
def generate_sample_data():
    dates = pd.date_range(start='2024-01-01', end='2024-12-17', freq='D')
    data = pd.DataFrame({
        'Date': dates,
        'Sales': np.random.randint(1000, 5000, len(dates)) + np.linspace(1000, 3000, len(dates)),
        'Customers': np.random.randint(50, 200, len(dates)),
        'Revenue': np.random.randint(10000, 50000, len(dates)),
        'Conversion_Rate': np.random.uniform(0.02, 0.08, len(dates))
    })
    return data

data = generate_sample_data()

# Main Content Area
if page == "🏠 Overview":
    st.markdown('<p class="main-header">Dashboard Overview</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Welcome to your AI-powered analytics platform</p>', unsafe_allow_html=True)
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Records",
            value="24,567",
            delta="↑ 12.5%"
        )
    
    with col2:
        st.metric(
            label="🔮 Predictions Made",
            value="1,234",
            delta="↑ 8.3%"
        )
    
    with col3:
        st.metric(
            label="🤖 AI Interactions",
            value="5,678",
            delta="↑ 15.7%"
        )
    
    with col4:
        st.metric(
            label="👥 Active Users",
            value="342",
            delta="↑ 5.2%"
        )
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Sales Trend")
        fig = px.line(data.tail(30), x='Date', y='Sales', 
                     title='Last 30 Days Sales Performance')
        fig.update_traces(line_color='#667eea')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue Distribution")
        fig = px.bar(data.tail(30), x='Date', y='Revenue',
                    title='Daily Revenue')
        fig.update_traces(marker_color='#764ba2')
        st.plotly_chart(fig, use_container_width=True)

elif page == "📊 Analytics Dashboard":
    st.markdown('<p class="main-header">Analytics Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Visualize your data with interactive charts and graphs</p>', unsafe_allow_html=True)
    
    # Date range selector
    col1, col2 = st.columns([3, 1])
    with col1:
        date_range = st.date_input(
            "Select Date Range",
            value=(data['Date'].min(), data['Date'].max()),
            min_value=data['Date'].min(),
            max_value=data['Date'].max()
        )
    with col2:
        metric_choice = st.selectbox("Select Metric", ['Sales', 'Revenue', 'Customers'])
    
    # Filter data
    if len(date_range) == 2:
        mask = (data['Date'] >= pd.Timestamp(date_range[0])) & (data['Date'] <= pd.Timestamp(date_range[1]))
        filtered_data = data.loc[mask]
    else:
        filtered_data = data
    
    # Main chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_data['Date'],
        y=filtered_data[metric_choice],
        mode='lines+markers',
        name=metric_choice,
        line=dict(color='#667eea', width=3)
    ))
    fig.update_layout(
        title=f'{metric_choice} Over Time',
        xaxis_title='Date',
        yaxis_title=metric_choice,
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average " + metric_choice, f"{filtered_data[metric_choice].mean():.2f}")
    with col2:
        st.metric("Maximum " + metric_choice, f"{filtered_data[metric_choice].max():.2f}")
    with col3:
        st.metric("Minimum " + metric_choice, f"{filtered_data[metric_choice].min():.2f}")

elif page == "📈 Statistical Dashboard":
    st.markdown('<p class="main-header">Statistical Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advanced statistical analysis and modeling</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribution Analysis")
        fig = px.histogram(data, x='Sales', nbins=50, 
                          title='Sales Distribution',
                          marginal='box')
        fig.update_traces(marker_color='#667eea')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Descriptive Statistics")
        st.dataframe(data[['Sales', 'Revenue', 'Customers']].describe(), use_container_width=True)
    
    with col2:
        st.subheader("🔗 Correlation Matrix")
        corr_data = data[['Sales', 'Revenue', 'Customers', 'Conversion_Rate']].corr()
        fig = px.imshow(corr_data, 
                       text_auto=True, 
                       color_continuous_scale='RdBu_r',
                       title='Correlation Heatmap')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📈 Scatter Plot Analysis")
        fig = px.scatter(data, x='Sales', y='Revenue', 
                        trendline='ols',
                        title='Sales vs Revenue Correlation')
        st.plotly_chart(fig, use_container_width=True)

elif page == "🔮 Prediction Engine":
    st.markdown('<p class="main-header">Prediction Engine</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered forecasting and trend analysis</p>', unsafe_allow_html=True)
    
    # Forecast parameters
    col1, col2, col3 = st.columns(3)
    with col1:
        forecast_days = st.slider("Forecast Days", 7, 90, 30)
    with col2:
        confidence = st.slider("Confidence Level (%)", 80, 99, 95)
    with col3:
        model_type = st.selectbox("Model Type", ["Linear", "Polynomial", "Exponential"])
    
    # Generate forecast (simple linear forecast for demo)
    last_date = data['Date'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days, freq='D')
    
    # Simple linear trend
    trend = np.polyfit(range(len(data)), data['Sales'], 1)
    forecast_values = np.polyval(trend, range(len(data), len(data) + forecast_days))
    
    # Add some variance
    forecast_upper = forecast_values * 1.1
    forecast_lower = forecast_values * 0.9
    
    # Plot
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=data['Date'].tail(90),
        y=data['Sales'].tail(90),
        mode='lines',
        name='Historical',
        line=dict(color='#667eea', width=2)
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=forecast_values,
        mode='lines',
        name='Forecast',
        line=dict(color='#f59e0b', width=2, dash='dash')
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=forecast_upper,
        mode='lines',
        name='Upper Bound',
        line=dict(width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=forecast_lower,
        mode='lines',
        name='Lower Bound',
        line=dict(width=0),
        fillcolor='rgba(245, 158, 11, 0.2)',
        fill='tonexty',
        showlegend=True
    ))
    
    fig.update_layout(
        title=f'{forecast_days}-Day Sales Forecast',
        xaxis_title='Date',
        yaxis_title='Sales',
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Forecast metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Predicted Average", f"{forecast_values.mean():.2f}")
    with col2:
        st.metric("Predicted Growth", f"{((forecast_values[-1] / data['Sales'].iloc[-1] - 1) * 100):.1f}%")
    with col3:
        st.metric("Confidence Level", f"{confidence}%")

elif page == "🤖 AI Chatbot":
    st.markdown('<p class="main-header">AI Chatbot</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interact with your data using natural language</p>', unsafe_allow_html=True)
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(message["content"])
            else:
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your data...")
    
    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Generate response (simple demo response)
        if "sales" in user_input.lower():
            response = f"Based on the data, your average sales are {data['Sales'].mean():.2f} with a total of {data['Sales'].sum():.0f} across all records. The trend shows a {((data['Sales'].iloc[-1] / data['Sales'].iloc[0] - 1) * 100):.1f}% change over the period."
        elif "revenue" in user_input.lower():
            response = f"Your total revenue is ${data['Revenue'].sum():,.0f} with an average daily revenue of ${data['Revenue'].mean():,.0f}."
        elif "predict" in user_input.lower() or "forecast" in user_input.lower():
            response = "I can help you with predictions! Navigate to the Prediction Engine section to see detailed forecasts and trend analysis."
        else:
            response = "I'm here to help you analyze your data! You can ask me about sales, revenue, customers, trends, or predictions."
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

elif page == "💾 Data Management":
    st.markdown('<p class="main-header">Data Management</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Manage your data sources and uploads</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload Data", "📊 View Data", "🔄 Data Sync"])
    
    with tab1:
        st.subheader("Upload New Data")
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            st.dataframe(df.head(10), use_container_width=True)
    
    with tab2:
        st.subheader("Current Dataset")
        st.dataframe(data, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Rows", len(data))
        with col2:
            st.metric("Total Columns", len(data.columns))
    
    with tab3:
        st.subheader("Data Synchronization")
        st.info("Configure automatic data sync from external sources")
        source = st.selectbox("Select Source", ["Database", "API", "Cloud Storage", "Local File"])
        if st.button("Sync Now"):
            with st.spinner("Syncing data..."):
                st.success("Data synchronized successfully!")

elif page == "👥 User Management":
    st.markdown('<p class="main-header">User Management</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Manage team members and permissions</p>', unsafe_allow_html=True)
    
    # Sample users
    users = pd.DataFrame({
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams'],
        'Email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com'],
        'Role': ['Admin', 'Analyst', 'Viewer', 'Analyst'],
        'Status': ['Active', 'Active', 'Inactive', 'Active'],
        'Last Login': ['2024-12-17', '2024-12-16', '2024-12-10', '2024-12-17']
    })
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Add New User", use_container_width=True):
            st.info("New user form would appear here")
    
    st.dataframe(users, use_container_width=True)

elif page == "⚙️ Settings":
    st.markdown('<p class="main-header">Settings</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Configure your dashboard preferences</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🎨 Appearance", "🔔 Notifications", "🔒 Security"])
    
    with tab1:
        st.subheader("Appearance Settings")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        st.color_picker("Accent Color", "#667eea")
        st.slider("Chart Animation Speed", 0, 100, 50)
    
    with tab2:
        st.subheader("Notification Preferences")
        st.checkbox("Email Notifications", value=True)
        st.checkbox("Push Notifications", value=False)
        st.checkbox("Prediction Alerts", value=True)
    
    with tab3:
        st.subheader("Security Settings")
        st.checkbox("Two-Factor Authentication", value=True)
        st.checkbox("Session Timeout (30 minutes)", value=True)
        if st.button("Change Password"):
            st.info("Password change form would appear here")

# Footer
st.divider()
st.caption("© 2024 Analytics Pro - AI-Powered Analytics Platform")