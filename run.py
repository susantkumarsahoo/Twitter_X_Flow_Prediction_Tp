import subprocess
import sys
import time
import signal
import os
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

from src.logging.logger import get_logger
from src.exceptions.exception import CustomException

logger = get_logger(__name__)

# Global process variables
fastapi_process = None
streamlit_process = None
flask_process = None
shutdown_event = threading.Event()

def signal_handler(sig, frame):
    """Handle Ctrl+C to stop both servers"""
    if shutdown_event.is_set():
        return  # Already shutting down
    
    shutdown_event.set()
    print("\n\n" + "="*60)
    print("  Stopping servers...")
    print("="*60)
    
    processes = [
        (fastapi_process, "FastAPI"),
        (flask_process, "Flask"),
        (streamlit_process, "Streamlit")
    ]
    
    for process, name in processes:
        if process:
            print(f"⏹️  Stopping {name} server...")
            try:
                process.terminate()
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print(f"⚠️  Force killing {name}...")
                process.kill()
                process.wait()
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
    
    print("\n✅ Servers stopped successfully!")
    sys.exit(0)

def check_port_available(port):
    """Check if a port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = s.connect_ex(('localhost', port))
            return result != 0
    except Exception as e:
        logger.error(f"Error checking port {port}: {e}")
        return False

def wait_for_api(max_attempts=30, timeout=2):
    """Wait for FastAPI to be ready with exponential backoff"""
    print("⏳ Waiting for FastAPI to be ready...")
    
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(
        max_retries=0,
        pool_connections=1,
        pool_maxsize=1
    ))
    
    for i in range(max_attempts):
        if shutdown_event.is_set():
            return False
        
        try:
            response = session.get(
                "http://localhost:8000/healthcheck", 
                timeout=timeout,
                headers={'Connection': 'close'}
            )
            if response.status_code == 200:
                print("\n✅ FastAPI is ready!")
                session.close()
                return True
        except requests.exceptions.RequestException:
            pass
        
        sys.stdout.write(f"\r   Attempt {i+1}/{max_attempts}...")
        sys.stdout.flush()
        
        # Exponential backoff: 0.5s, 1s, 2s, then 2s
        wait_time = min(0.5 * (2 ** i), 2)
        time.sleep(wait_time)
    
    session.close()
    print("\n❌ FastAPI failed to start within expected time")
    return False

def monitor_process_output(process, name):
    """Monitor and log process output in real-time"""
    try:
        for line in iter(process.stdout.readline, ''):
            if shutdown_event.is_set():
                break
            if line:
                print(f"[{name}] {line.rstrip()}")
    except Exception as e:
        logger.error(f"Error monitoring {name}: {e}")

def run_servers():
    """Run FastAPI, Flask, and Streamlit servers with optimized startup"""
    global fastapi_process, streamlit_process, flask_process
    
    print("\n" + "="*60)
    print("  Twitter Analytics Dashboard - Starting Servers")
    print("="*60)
    
    # Check if files exist
    required_files = {
        'fastapi_app.py': 'FastAPI backend',
        'streamlit_app.py': 'Streamlit frontend'
    }
    
    optional_files = {
        'flask_app.py': 'Flask backend'
    }
    
    for file, desc in required_files.items():
        if not os.path.exists(file):
            print(f"\n❌ Error: {file} not found!")
            print(f"Please ensure {file} ({desc}) exists in current directory")
            sys.exit(1)
        print(f"✓ Found {file} ({desc})")
    
    flask_exists = os.path.exists('flask_app.py')
    if flask_exists:
        print("✓ Found flask_app.py (Flask backend)")
    else:
        print("⚠️  flask_app.py not found - Flask server will not be started")
    
    # Check if ports are available
    ports_to_check = [
        (8000, 'FastAPI'),
        (8501, 'Streamlit')
    ]
    
    if flask_exists:
        ports_to_check.append((5000, 'Flask'))
    
    for port, service in ports_to_check:
        if not check_port_available(port):
            print(f"\n⚠️  Port {port} is already in use ({service})!")
            print(f"Please stop any running {service} instances or use a different port")
            sys.exit(1)
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start FastAPI with optimized settings
        print("\n" + "-"*60)
        print("🚀 Starting FastAPI server...")
        print("-"*60)
        
        fastapi_env = os.environ.copy()
        fastapi_env.update({
            'PYTHONUNBUFFERED': '1',
            'UVICORN_WORKERS': '1',  # Single worker for development
        })
        
        fastapi_process = subprocess.Popen(
            [
                sys.executable, '-m', 'uvicorn', 
                'fastapi_app:app', 
                '--host', '0.0.0.0', 
                '--port', '8000',
                '--log-level', 'info',
                '--timeout-keep-alive', '30',  # Reduced timeout
                '--limit-concurrency', '100',  # Limit concurrent connections
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=fastapi_env
        )
        
        # Start monitoring FastAPI output in background
        fastapi_monitor = threading.Thread(
            target=monitor_process_output,
            args=(fastapi_process, "FastAPI"),
            daemon=True
        )
        fastapi_monitor.start()
        
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
            
            flask_env = os.environ.copy()
            flask_env.update({
                'FLASK_APP': 'flask_app.py',
                'FLASK_ENV': 'development',
                'FLASK_RUN_HOST': '0.0.0.0',
                'FLASK_RUN_PORT': '5000',
                'PYTHONUNBUFFERED': '1'
            })
            
            flask_process = subprocess.Popen(
                [sys.executable, 'flask_app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=flask_env
            )
            
            flask_monitor = threading.Thread(
                target=monitor_process_output,
                args=(flask_process, "Flask"),
                daemon=True
            )
            flask_monitor.start()
            time.sleep(2)
        
        # Start Streamlit
        print("\n" + "-"*60)
        print("🚀 Starting Streamlit server...")
        print("-"*60)
        
        streamlit_env = os.environ.copy()
        streamlit_env['PYTHONUNBUFFERED'] = '1'
        
        streamlit_process = subprocess.Popen(
            [
                sys.executable, '-m', 'streamlit', 'run', 
                'streamlit_app.py',
                '--server.headless', 'true',
                '--server.runOnSave', 'false',  # Disable auto-reload
                '--browser.gatherUsageStats', 'false',
                '--server.maxUploadSize', '200',  # MB
                '--server.enableXsrfProtection', 'false',  # For development
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=streamlit_env
        )
        
        streamlit_monitor = threading.Thread(
            target=monitor_process_output,
            args=(streamlit_process, "Streamlit"),
            daemon=True
        )
        streamlit_monitor.start()
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
        
        # Monitor processes
        while not shutdown_event.is_set():
            time.sleep(1)
            
            # Check if processes are still running
            if fastapi_process.poll() is not None:
                print("\n⚠️  FastAPI process stopped unexpectedly!")
                print("Exit code:", fastapi_process.returncode)
                signal_handler(None, None)
                break
            
            if flask_exists and flask_process and flask_process.poll() is not None:
                print("\n⚠️  Flask process stopped unexpectedly!")
                print("Exit code:", flask_process.returncode)
                signal_handler(None, None)
                break
            
            if streamlit_process.poll() is not None:
                print("\n⚠️  Streamlit process stopped unexpectedly!")
                print("Exit code:", streamlit_process.returncode)
                signal_handler(None, None)
                break
    
    except Exception as e:
        logger.error(f"Error in run_servers: {e}")
        signal_handler(None, None)

if __name__ == "__main__":
    # Check for required packages
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'plotly': 'plotly',
        'flask': 'flask',
        'requests': 'requests'
    }
    
    missing_packages = []
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
        print("\nPlease install required packages:")
        print("pip install fastapi uvicorn streamlit pandas plotly openpyxl requests flask")
        sys.exit(1)
    
    run_servers()

# python run.py