import os
import sys
import time
import requests
import streamlit as st
from src.logging.logger import get_logger

logger = get_logger(__name__)


FASTAPI_URL = "http://localhost:8000"
FLASK_URL = "http://localhost:5000"

def fastapi_api_request_url(endpoint: str, timeout: int = 30, max_retries: int = 3):
    """
    Make API request with retry logic
    
    Parameters:
        endpoint: API endpoint to call
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    
    Returns:
        Response object or None if failed
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{FASTAPI_URL}{endpoint}", timeout=timeout)
            response.raise_for_status()
            logger.info("Fast API request successful")
            return response
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏱️ Request timeout. Retrying... (Attempt {attempt + 2}/{max_retries})")
                time.sleep(2)
            else:
                st.error(f"⏱️ Request timed out after {max_retries} attempts.")
                return None
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Please ensure the FastAPI server is running.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request error: {e}")
            return None
    
    return None


def flask_api_request_url(endpoint: str, timeout: int = 30, max_retries: int = 3):
    """
    Make API request with retry logic
    
    Parameters:
        endpoint: API endpoint to call
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    
    Returns:
        Response object or None if failed
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{FLASK_URL}{endpoint}", timeout=timeout)
            response.raise_for_status()
            logger.info("Flask API request successful")
            return response
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏱️ Request timeout. Retrying... (Attempt {attempt + 2}/{max_retries})")
                time.sleep(2)
            else:
                st.error(f"⏱️ Request timed out after {max_retries} attempts.")
                return None
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Please ensure the FastAPI server is running.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request error: {e}")
            return None
    
    return None