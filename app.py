import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Try to import custom modules
try:
    from src.backend_api.streamlit_helper import analysis_dashboard
    from src.constants.paths import dataset_path
except ImportError:
    st.error("⚠️ Unable to import custom modules. Please check your project structure.")
    dataset_path = "data/dataset.xlsx"  # Fallback path

# API Configuration
API_URL = "http://localhost:8000"

# Page Configuration
st.set_page_config(
    page_title="Twitter Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# API STATUS CHECK FUNCTION
# ============================================

def check_api_status():
    """Check if FastAPI is running and accessible"""
    try:
        response = requests.get(f"{API_URL}/healthcheck", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, {"status": "error", "message": "API returned non-200 status"}
    except requests.exceptions.ConnectionError:
        return False, {"status": "error", "message": "Cannot connect to API"}
    except requests.exceptions.Timeout:
        return False, {"status": "error", "message": "Connection timeout"}
    except Exception as e:
        return False, {"status": "error", "message": str(e)}

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown(
        """
        <div style="border: 2px solid #1E90FF; padding: 10px; border-radius: 8px; text-align: center;">
            <h2 style="color: #1E90FF;">📊 Twitter X Control Panel</h2>
        </div>
        <hr>
        """,
        unsafe_allow_html=True
    )    
    
    # Navigation
    st.header("🧭 Navigation")
    
    dashboard_type = st.radio(
        "Select Dashboard",
        [
            "📈 Analysis Dashboard",
            "📊 Mathematics & Statistical Analysis",
            "🔮 Twitter Flow Prediction",
            "🕒 Time Series Analysis",
            "📝 Sentiment Analysis",
            "🤖 AI Chatbot"
        ],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Data Source
    st.header("📁 Data Source")
    
    uploaded_file = st.file_uploader(
        "Upload your data",
        type=['csv', 'xlsx', 'json'],
        help="Supported formats: CSV, Excel, JSON"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ '{uploaded_file.name}' uploaded!")
    
    st.divider()
    
    # API Status Check
    st.header("🔌 API Status")
    
    api_status_placeholder = st.empty()
    
    with api_status_placeholder.container():
        is_connected, api_data = check_api_status()
        
        if is_connected:
            st.success("✅ API Connected")
            
            if api_data.get("dataset_available"):
                st.info("📂 Dataset available")
            else:
                st.warning("⚠️ Dataset not found")
        else:
            st.error("❌ API Disconnected")
            with st.expander("Show error details"):
                st.code(api_data.get("message", "Unknown error"))
                st.write("**Troubleshooting:**")
                st.write("1. Check if FastAPI server is running")
                st.write("2. Run: `uvicorn main:app --reload`")
                st.write("3. Check if port 8000 is available")
    
    # Refresh API status button
    if st.button("🔄 Refresh API Status", use_container_width=True):
        st.rerun()
    
    st.divider()
    
    # Info Section
    with st.expander("ℹ️ Dashboard Info"):
        st.info(f"""
        **Version:** 2.0
        
        **Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
        
        **Status:** {"✅ Connected" if is_connected else "❌ Disconnected"}
        
        **Dataset:** {dataset_path}
        """)
    
    st.caption("© 2024 Twitter Analytics Dashboard | v2.0")

# ============================================
# MAIN CONTENT
# ============================================

# Check API connection before proceeding
is_connected, _ = check_api_status()

if not is_connected:
    st.title("⚠️ API Connection Required")
    st.error("Cannot connect to FastAPI backend. Please ensure the server is running.")
    
    st.markdown("""
    ### 🔧 Quick Fix:
    
    1. Open a terminal in your project directory
    2. Run the following command:
    ```bash
    python run.py
    ```
    
    Or start servers separately:
    ```bash
    # Terminal 1 - FastAPI
    uvicorn main:app --reload
    
    # Terminal 2 - Streamlit
    streamlit run app.py
    ```
    
    3. Refresh this page after the server starts
    """)
    
    if st.button("🔄 Retry Connection", type="primary"):
        st.rerun()
else:
    # Show main dashboard if connected
    try:
        analysis_dashboard(dashboard_type, dataset_path, uploaded_file)
    except NameError:
        st.error("⚠️ Dashboard module not found. Please check your project structure.")
        st.info("Make sure `src/streamlit/st_analyst.py` exists and contains `analysis_dashboard` function.")




