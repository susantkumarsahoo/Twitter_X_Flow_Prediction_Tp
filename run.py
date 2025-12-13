import subprocess
import sys
import time
import signal
import os

# Global process variables
fastapi_process = None
streamlit_process = None

def signal_handler(sig, frame):
    """Handle Ctrl+C to stop both servers"""
    print("\n\nStopping servers...")
    if fastapi_process:
        fastapi_process.terminate()
    if streamlit_process:
        streamlit_process.terminate()
    print("Servers stopped!")
    sys.exit(0)

def run_servers():
    """Run both FastAPI and Streamlit servers"""
    global fastapi_process, streamlit_process
    
    print("="*60)
    print("  Sales Analysis Dashboard - Starting Servers")
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
    
    print("\n✓ Found main.py (FastAPI backend)")
    print("✓ Found app.py (Streamlit frontend)")
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n🚀 Starting FastAPI server...")
    fastapi_process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    print("⏳ Waiting for FastAPI to initialize...")
    time.sleep(3)
    
    print("🚀 Starting Streamlit server...")
    streamlit_process = subprocess.Popen(
        [sys.executable, '-m', 'streamlit', 'run', 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    print("\n" + "="*60)
    print("✅ Both servers are running!")
    print("="*60)
    print("\n📍 Access URLs:")
    print("   FastAPI Backend:  http://localhost:8000")
    print("   Streamlit Dashboard: http://localhost:8501")
    print("\n💡 Press Ctrl+C to stop both servers")
    print("="*60 + "\n")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if fastapi_process.poll() is not None:
                print("\n⚠️  FastAPI process stopped unexpectedly!")
                break
            if streamlit_process.poll() is not None:
                print("\n⚠️  Streamlit process stopped unexpectedly!")
                break
                
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    run_servers()