import sys
import os
import subprocess

def install_dependencies():
    """Install required dependencies."""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def start_redis():
    """Start Redis server if not already running."""
    try:
        subprocess.Popen(['redis-server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Redis server started.")
    except FileNotFoundError:
        print("Redis server not found. Please install Redis manually.")

def start_api_server():
    """Start the FastAPI server."""
    subprocess.check_call([
        sys.executable, '-m', 'uvicorn', 
        'searchEngine.api.route:app', 
        '--host', '0.0.0.0', 
        '--port', '8000', 
        '--reload'
    ])

def main():
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("🚀 Search Engine Startup Script 🚀")
    
    # Install dependencies
    print("Installing dependencies...")
    install_dependencies()
    
    # Start Redis (optional)
    start_redis()
    
    # Start API server
    print("Starting Search Engine API...")
    start_api_server()

if __name__ == '__main__':
    main()
