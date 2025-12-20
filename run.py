import subprocess
import sys
import time
import signal
import os
import requests
from pathlib import Path

from src.logging.logger import get_logger
from src.exceptions.exception import CustomException

logger = get_logger(__name__)

# run.py

# Global process variables
fastapi_process = None
streamlit_process = None
flask_process = None

def signal_handler(sig, frame):
    """Handle Ctrl+C to stop both servers"""
    print("\n\n" + "="*60)
    print("  Stopping servers...")
    print("="*60)
    
    if fastapi_process:
        print("⏹️  Stopping FastAPI server...")
        fastapi_process.terminate()
        try:
            fastapi_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            fastapi_process.kill()
    
    if flask_process:
        print("⏹️  Stopping Flask server...")
        flask_process.terminate()
        try:
            flask_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            flask_process.kill()
    
    if streamlit_process:
        print("⏹️  Stopping Streamlit server...")
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streamlit_process.kill()
    
    print("\n✅ Servers stopped successfully!")
    sys.exit(0)

def check_port_available(port):
    """Check if a port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def wait_for_api(max_attempts=30):
    """Wait for FastAPI to be ready"""
    print("⏳ Waiting for FastAPI to be ready...")
    
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/healthcheck", timeout=2)
            if response.status_code == 200:
                print("✅ FastAPI is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        sys.stdout.write(f"\r   Attempt {i+1}/{max_attempts}...")
        sys.stdout.flush()
        time.sleep(1)
    
    print("\n❌ FastAPI failed to start within expected time")
    return False

def run_servers():
    """Run both FastAPI and Streamlit servers"""
    global fastapi_process, streamlit_process, flask_process
    
    print("\n" + "="*60)
    print("  Twitter Analytics Dashboard - Starting Servers")
    print("="*60)
    
    # Check if files exist
    if not os.path.exists('main.py'):
        print("\n❌ Error: main.py not found!")
        print("Please ensure main.py (FastAPI backend) exists in current directory")
        sys.exit(1)
    
    if not os.path.exists('app.py'):
        print("\n❌ Error: app.py not found!")
        print("Please ensure app.py (Streamlit frontend) exists in current directory")
        sys.exit(1)
    
    if not os.path.exists('flask_app.py'):
        print("\n⚠️  Warning: flask_app.py not found!")
        print("Flask server will not be started")
        flask_exists = False
    else:
        flask_exists = True
    
    print("\n✓ Found main.py (FastAPI backend)")
    print("✓ Found app.py (Streamlit frontend)")
    if flask_exists:
        print("✓ Found flask_app.py (Flask backend)")
    
    # Check if ports are available
    if not check_port_available(8000):
        print("\n⚠️  Port 8000 is already in use!")
        print("Please stop any running FastAPI instances or use a different port")
        sys.exit(1)
    
    if flask_exists and not check_port_available(5000):
        print("\n⚠️  Port 5000 is already in use!")
        print("Please stop any running Flask instances or use a different port")
        sys.exit(1)
    
    if not check_port_available(8501):
        print("\n⚠️  Port 8501 is already in use!")
        print("Please stop any running Streamlit instances or use a different port")
        sys.exit(1)
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "-"*60)
    print("🚀 Starting FastAPI server...")
    print("-"*60)
    
    # Start FastAPI with output visible
    fastapi_process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000', '--log-level', 'info'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    # Wait for FastAPI to be ready
    if not wait_for_api():
        print("\n❌ Failed to start FastAPI. Stopping...")
        signal_handler(None, None)
        return
    
    # Start Flask if file exists
    if flask_exists:
        print("\n" + "-"*60)
        print("🚀 Starting Flask server...")
        print("-"*60)
        
        flask_process = subprocess.Popen(
            [sys.executable, 'flask_app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env={**os.environ, 'FLASK_APP': 'flask_app.py', 'FLASK_RUN_HOST': '0.0.0.0', 'FLASK_RUN_PORT': '5000'}
        )
        time.sleep(2)
    
    print("\n" + "-"*60)
    print("🚀 Starting Streamlit server...")
    print("-"*60)

    # Start Streamlit
    streamlit_process = subprocess.Popen(
        [sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.headless', 'true'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    time.sleep(3)
    
    print("\n" + "="*60)
    print("✅ Servers are running!")
    print("="*60)
    print("\n📍 Access URLs:")
    print("   🔧 FastAPI Backend:      http://localhost:8000")
    print("   📊 FastAPI Docs:         http://localhost:8000/docs")
    if flask_exists:
        print("   🌶️  Flask Backend:        http://localhost:5000")
    print("   🌐 Streamlit Dashboard:  http://localhost:8501")
    print("\n💡 Press Ctrl+C to stop all servers")
    print("="*60 + "\n")
    
    try:
        # Keep the script running and monitor processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if fastapi_process.poll() is not None:
                print("\n⚠️  FastAPI process stopped unexpectedly!")
                print("Exit code:", fastapi_process.returncode)
                break
            
            if flask_exists and flask_process and flask_process.poll() is not None:
                print("\n⚠️  Flask process stopped unexpectedly!")
                print("Exit code:", flask_process.returncode)
                break
            
            if streamlit_process.poll() is not None:
                print("\n⚠️  Streamlit process stopped unexpectedly!")
                print("Exit code:", streamlit_process.returncode)
                break
                
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    # Check for required packages
    try:
        import fastapi
        import uvicorn
        import streamlit
        import pandas
        import plotly
        import flask
    except ImportError as e:
        print(f"\n❌ Missing required package: {e}")
        print("\nPlease install required packages:")
        print("pip install fastapi uvicorn streamlit pandas plotly openpyxl requests flask")
        sys.exit(1)
    
    run_servers()


    