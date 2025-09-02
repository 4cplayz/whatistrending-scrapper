"""
Main entry point for the Newsletter Scraper Service.

This script combines the Flask keep-alive server with the background
worker functionality, making it suitable for Railway deployment.
"""

import logging
import signal
import sys
import time
from src.utils.keep_alive import keep_alive
from src.schedulers.test_worker import test_worker


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """
    Handle system signals for graceful shutdown.
    
    Args:
        signum (int): Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    test_worker.stop_worker()
    sys.exit(0)


def main():
    """
    Main function that starts both the keep-alive server and worker.
    
    This function:
    1. Sets up signal handlers for graceful shutdown
    2. Starts the Flask keep-alive server in background
    3. Starts the test worker in background
    4. Keeps the main process alive
    """
    logger.info("=== Newsletter Scraper Service Starting ===")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the Flask keep-alive server
        logger.info("Starting keep-alive server...")
        keep_alive()
        
        # Give Flask a moment to start
        time.sleep(2)
        
        # Start the background worker
        logger.info("Starting background worker...")
        test_worker.start_background_worker()
        
        logger.info("=== All services started successfully ===")
        logger.info("Service is running - accessible at http://0.0.0.0:8080")
        logger.info("Press Ctrl+C to stop the service")
        
        # Keep the main process alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        logger.info("Cleaning up...")
        test_worker.stop_worker()
        logger.info("=== Newsletter Scraper Service Stopped ===")


if __name__ == "__main__":
    main()