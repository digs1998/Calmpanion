import os
import logging
import subprocess
import threading
import time
from flask import Flask, render_template, redirect, url_for, request, jsonify
from config import STREAMLIT_PORT, SECRET_KEY

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", SECRET_KEY)

# Store the Streamlit process
streamlit_process = None

def start_streamlit():
    """Start the Streamlit app as a subprocess"""
    global streamlit_process
    try:
        # Check if streamlit is already running
        if streamlit_process and streamlit_process.poll() is None:
            logger.info("Streamlit already running")
            return
        
        streamlit_cmd = "/home/ubuntu/Calmpanion/venv/bin/streamlit"
        # Start Streamlit on a different port
        cmd = [streamlit_cmd, "run", "streamlit_wrapper.py", "--server.fileWatcherType", "none"]
        
        logger.info(f"Starting Streamlit with command: {' '.join(cmd)}")
        streamlit_process = subprocess.Popen(cmd)
        logger.info(f"Streamlit process started with PID: {streamlit_process.pid}")
        
        # Give Streamlit time to start
        time.sleep(5)
    except Exception as e:
        logger.error(f"Error starting Streamlit: {e}")
        if streamlit_process:
            try:
                streamlit_process.terminate()
            except:
                pass
            streamlit_process = None

# Start Streamlit in a separate thread
threading.Thread(target=start_streamlit, daemon=True).start()

@app.route('/')
def index():
    """Render the landing page"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Redirect to the Streamlit chat interface"""
    return render_template('streamlit.html', streamlit_url=f"http://0.0.0.0:5000")

@app.route('/health')
def health_check():
    """Health check endpoint for the Flask app"""
    return jsonify({"status": "healthy", "app": "flask"})

@app.route('/streamlit-health')
def streamlit_health():
    """Check if Streamlit is running"""
    if streamlit_process and streamlit_process.poll() is None:
        return jsonify({"status": "healthy", "app": "streamlit"})
    else:
        # Try to restart Streamlit
        start_streamlit()
        if streamlit_process and streamlit_process.poll() is None:
            return jsonify({"status": "restarted", "app": "streamlit"})
        return jsonify({"status": "down", "app": "streamlit"}), 503

# Handle the login and signup routes
@app.route('/login', methods=['POST'])
def login():
    """Handle login form submission"""
    # In a real implementation, this would validate credentials against the S3 storage
    # For now, we'll just redirect to the Streamlit app which handles authentication
    return redirect(url_for('chat'))

@app.route('/signup', methods=['POST'])
def signup():
    """Handle signup form submission"""
    # In a real implementation, this would create a new user in S3 storage
    # For now, we'll just redirect to the Streamlit app which handles authentication
    return redirect(url_for('chat'))

@app.route('/guest', methods=['POST'])
def guest():
    """Handle guest access"""
    return redirect(url_for('chat'))

@app.route('/run-streamlit', methods=['POST'])
def run_streamlit_route():
    """Endpoint to get the Streamlit URL after ensuring it's running"""
    # Make sure Streamlit is running
    if not streamlit_process or streamlit_process.poll() is not None:
        start_streamlit()
    
    # Return the Streamlit URL 
    return f"http://0.0.0.0:5000"

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {e}")
    return render_template('index.html', error="Internal server error. Please try again later."), 500

# Cleanup when the Flask app exits
import atexit

@atexit.register
def cleanup():
    """Clean up the Streamlit process when Flask exits"""
    global streamlit_process
    if streamlit_process:
        logger.info(f"Terminating Streamlit process {streamlit_process.pid}")
        try:
            streamlit_process.terminate()
            streamlit_process.wait(timeout=5)
        except:
            try:
                streamlit_process.kill()
            except:
                pass
        streamlit_process = None
