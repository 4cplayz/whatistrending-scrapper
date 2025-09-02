"""
Apify TikTok scraper execution functionality.

Single responsibility: Execute TikTok scraping jobs with Apify.
"""

import logging
from typing import Dict, Any, Optional
from src.api_clients.apify.apify_client import get_apify_client
from src.api_clients.apify.tiktok_config import get_car_edit_config

logger = logging.getLogger(__name__)


def run_tiktok_scraper(actor_id: str = "clockworks/free-tiktok-scraper") -> Optional[str]:
    """
    Run TikTok scraper with car edit configuration.
    
    Args:
        actor_id (str): Apify actor ID for TikTok scraper
        
    Returns:
        Optional[str]: Run ID of the started scraping job
        
    Raises:
        ConnectionError: If Apify client connection fails
        ValueError: If scraper run fails
    """
    try:
        client = get_apify_client()
        config = get_car_edit_config()
        
        # Start the scraper run
        run = client.actor(actor_id).call(run_input=config)
        run_id = run.get("id")
        
        logger.info(f"TikTok scraper started with run ID: {run_id}")
        return run_id
        
    except Exception as e:
        logger.error(f"Failed to run TikTok scraper: {e}")
        raise ValueError(f"TikTok scraper execution failed: {e}")


def get_scraper_status(run_id: str) -> Optional[Dict[str, Any]]:
    """
    Get status of running TikTok scraper job.
    
    Args:
        run_id (str): Run ID of the scraping job
        
    Returns:
        Optional[Dict[str, Any]]: Status information of the run
        
    Raises:
        ConnectionError: If Apify client connection fails
        ValueError: If status check fails
    """
    try:
        client = get_apify_client()
        run_info = client.run(run_id).get()
        
        status = {
            "id": run_info.get("id"),
            "status": run_info.get("status"),
            "startedAt": run_info.get("startedAt"),
            "finishedAt": run_info.get("finishedAt"),
            "stats": run_info.get("stats", {})
        }
        
        logger.info(f"Run {run_id} status: {status['status']}")
        return status
        
    except Exception as e:
        logger.error(f"Failed to get scraper status: {e}")
        raise ValueError(f"Status check failed: {e}")