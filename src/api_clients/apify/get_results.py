"""
Apify scraper results retrieval functionality.

Single responsibility: Fetch and process TikTok scraping results.
"""

import logging
from typing import List, Dict, Any, Optional
from src.api_clients.apify.apify_client import get_apify_client

logger = logging.getLogger(__name__)


def get_scraper_results(run_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Retrieve results from completed TikTok scraper run.
    
    Args:
        run_id (str): Run ID of the completed scraping job
        
    Returns:
        Optional[List[Dict[str, Any]]]: List of scraped video data
        
    Raises:
        ConnectionError: If Apify client connection fails
        ValueError: If results retrieval fails
    """
    try:
        client = get_apify_client()
        
        # Get dataset items from the run
        dataset_client = client.dataset(client.run(run_id).get()["defaultDatasetId"])
        items = list(dataset_client.iterate_items())
        
        logger.info(f"Retrieved {len(items)} items from run {run_id}")
        return items
        
    except Exception as e:
        logger.error(f"Failed to get scraper results: {e}")
        raise ValueError(f"Results retrieval failed: {e}")


def parse_video_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and clean raw TikTok video data from Apify.
    
    Args:
        raw_data (Dict[str, Any]): Raw video data from scraper
        
    Returns:
        Dict[str, Any]: Cleaned and structured video data
    """
    try:
        parsed_data = {
            "video_id": raw_data.get("id"),
            "video_url": raw_data.get("webVideoUrl"),
            "description": raw_data.get("text", ""),
            "hashtags": raw_data.get("hashtags", []),
            "music_title": raw_data.get("musicMeta", {}).get("musicName"),
            "music_author": raw_data.get("musicMeta", {}).get("musicAuthor"),
            "author_username": raw_data.get("authorMeta", {}).get("name"),
            "author_nickname": raw_data.get("authorMeta", {}).get("nickName"),
            "video_meta": {
                "duration": raw_data.get("videoMeta", {}).get("duration"),
                "width": raw_data.get("videoMeta", {}).get("width"),
                "height": raw_data.get("videoMeta", {}).get("height"),
                "covers": raw_data.get("videoMeta", {}).get("covers", [])
            },
            "stats": {
                "views": raw_data.get("stats", {}).get("playCount", 0),
                "likes": raw_data.get("stats", {}).get("diggCount", 0),
                "comments": raw_data.get("stats", {}).get("commentCount", 0),
                "shares": raw_data.get("stats", {}).get("shareCount", 0)
            },
            "created_time": raw_data.get("createTime"),
            "scraped_at": raw_data.get("collected_at")
        }
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"Failed to parse video data: {e}")
        return raw_data  # Return raw data if parsing fails