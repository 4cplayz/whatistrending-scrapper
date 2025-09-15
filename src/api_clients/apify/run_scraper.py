"""
Apify TikTok scraper execution functionality.

Single responsibility: Execute TikTok scraping jobs with Apify.
"""

import logging
import time
from typing import Dict, Any, Optional
from src.api_clients.apify.apify_client import get_apify_client
from src.config.tiktok_config import get_car_edit_config
from src.utils.error_logger import log_api_failure

logger = logging.getLogger(__name__)


def run_tiktok_scraper(actor_id: str = "clockworks/free-tiktok-scraper", custom_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Run TikTok scraper with car edit configuration or custom config.
    
    Args:
        actor_id (str): Apify actor ID for TikTok scraper
        custom_config (Optional[Dict[str, Any]]): Custom configuration to override defaults
        
    Returns:
        Optional[str]: Run ID of the started scraping job
        
    Raises:
        ConnectionError: If Apify client connection fails
        ValueError: If scraper run fails
    """
    try:
        client = get_apify_client()
        
        if custom_config:
            # Use custom config - completely override base config
            config = custom_config
            logger.info("Using completely custom scraper configuration (no base merge)")
        else:
            config = get_car_edit_config()
            logger.info("Using default car edit configuration")
        
        # Start the scraper run
        run = client.actor(actor_id).call(run_input=config)
        run_id = run.get("id")
        
        logger.info(f"TikTok scraper started with run ID: {run_id}")
        return run_id
        
    except Exception as e:
        logger.error(f"Failed to run TikTok scraper: {e}")
        log_api_failure("apify_scraper", f"TikTok scraper execution failed: {str(e)}", {"actor_id": actor_id})
        raise ValueError(f"TikTok scraper execution failed: {e}")


def get_scraper_status(run_id: str, wait_for_completion: bool = False, timeout: int = 300) -> str:
    """
    Get status of running TikTok scraper job.
    
    Args:
        run_id (str): Run ID of the scraping job
        wait_for_completion (bool): Whether to wait for completion
        timeout (int): Maximum wait time in seconds
        
    Returns:
        str: Final status of the run
        
    Raises:
        ConnectionError: If Apify client connection fails
        ValueError: If status check fails
        TimeoutError: If waiting exceeds timeout
    """
    try:
        client = get_apify_client()
        
        if not wait_for_completion:
            # Single status check
            run_info = client.run(run_id).get()
            status = run_info.get("status")
            logger.info(f"Run {run_id} status: {status}")
            return status
        
        # Wait for completion
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout:
            run_info = client.run(run_id).get()
            current_status = run_info.get("status")
            
            if current_status != last_status:
                logger.info(f"Run {run_id} status: {current_status}")
                last_status = current_status
            
            if current_status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                logger.info(f"Run {run_id} completed with status: {current_status}")
                return current_status
            
            time.sleep(10)  # Wait 10 seconds between checks
        
        raise TimeoutError(f"Run {run_id} did not complete within {timeout} seconds")
        
    except Exception as e:
        logger.error(f"Failed to get scraper status: {e}")
        if isinstance(e, TimeoutError):
            raise
        raise ValueError(f"Status check failed: {e}")