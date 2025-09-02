"""
Simple test worker script for Railway deployment testing.

This script demonstrates the basic worker functionality that will
be expanded into the full newsletter scraping system.
"""

import time
import logging
from datetime import datetime
from threading import Thread


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestWorker:
    """
    Simple test worker that prints messages every 30 seconds.
    
    This class demonstrates the background worker pattern that will
    be used for the newsletter scraping and processing system.
    """
    
    def __init__(self, interval: int = 30):
        """
        Initialize the test worker.
        
        Args:
            interval (int): Time between messages in seconds (default: 30)
        """
        self.interval = interval
        self.is_running = False
        self.message_count = 0
    
    def log_hello_world(self) -> None:
        """
        Log a hello world message with timestamp and counter.
        
        This simulates the periodic tasks that the newsletter service
        will perform (scraping, analysis, etc.).
        """
        self.message_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Hello World! #{self.message_count} - {timestamp}"
        
        logger.info(message)
        print(message)  # Also print to console for Railway logs
    
    def run_worker(self) -> None:
        """
        Main worker loop that runs every 30 seconds.
        
        This method runs continuously, executing the hello world
        logging function at the specified interval.
        """
        logger.info(f"Starting test worker (interval: {self.interval}s)")
        self.is_running = True
        
        while self.is_running:
            try:
                self.log_hello_world()
                time.sleep(self.interval)
            except KeyboardInterrupt:
                logger.info("Worker interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                time.sleep(5)  # Wait 5 seconds before retrying
        
        self.is_running = False
        logger.info("Test worker stopped")
    
    def start_background_worker(self) -> None:
        """
        Start the worker in a background thread.
        
        This allows the worker to run alongside the Flask keep-alive
        server without blocking either process.
        """
        if not self.is_running:
            logger.info("Starting background worker thread...")
            worker_thread = Thread(target=self.run_worker)
            worker_thread.daemon = True
            worker_thread.start()
            logger.info("Background worker thread started successfully!")
    
    def stop_worker(self) -> None:
        """
        Stop the worker gracefully.
        
        Sets the running flag to False, allowing the worker loop
        to exit cleanly.
        """
        logger.info("Stopping test worker...")
        self.is_running = False


# Create global worker instance
test_worker = TestWorker()