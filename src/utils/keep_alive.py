"""
Flask keep-alive service for Railway deployment.

This keeps the Railway service active by providing an HTTP endpoint
that Railway can ping to ensure the service stays running.
"""

from flask import Flask
from threading import Thread
import time
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """
    Health check endpoint for Railway.
    
    Returns:
        str: Simple alive message
    """
    return "Newsletter Service is Alive! 🚀"


@app.route('/health')
def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "newsletter-scraper",
        "timestamp": time.time()
    }


@app.route('/status')
def status():
    """
    Status endpoint showing service information.
    
    Returns:
        dict: Service status and information
    """
    return {
        "service": "Newsletter Scraper Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/", "/health", "/status"]
    }


def run_flask():
    """
    Run the Flask application.
    
    Starts the Flask server on host 0.0.0.0 and port 8080
    for Railway compatibility.
    """
    logger.info("Starting Flask keep-alive server...")
    app.run(host='0.0.0.0', port=8080, debug=False)


def keep_alive():
    """
    Start the keep-alive Flask server in a separate thread.
    
    This function starts the Flask server in a background thread
    so it doesn't block the main application logic.
    """
    logger.info("Initializing keep-alive service...")
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    logger.info("Keep-alive service started successfully!")