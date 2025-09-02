"""
Flask keep-alive service for Railway deployment.

Single responsibility: Start Flask server in background thread.
"""

from threading import Thread
import logging
from src.utils.flask_app import create_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()


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