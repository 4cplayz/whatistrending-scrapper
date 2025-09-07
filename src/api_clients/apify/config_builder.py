"""
TikTok scraper configuration builder with modification capabilities.

Single responsibility: Build and modify TikTok scraping configurations.
"""

import logging
from typing import Dict, List, Any, Optional
from src.config.tiktok_config import get_car_edit_config

logger = logging.getLogger(__name__)


def create_custom_config(
    hashtags: Optional[List[str]] = None,
    profiles: Optional[List[str]] = None,
    search_queries: Optional[List[str]] = None,
    days_back: int = 7,
    results_per_page: int = 5
) -> Dict[str, Any]:
    """
    Create custom TikTok scraper configuration.
    
    Args:
        hashtags (Optional[List[str]]): Custom hashtags to scrape
        profiles (Optional[List[str]]): Custom profiles to scrape  
        search_queries (Optional[List[str]]): Custom search terms
        days_back (int): Number of days to look back (default: 7)
        results_per_page (int): Results per page (default: 5)
        
    Returns:
        Dict[str, Any]: Custom scraper configuration
    """
    base_config = get_car_edit_config()
    
    if hashtags:
        base_config["hashtags"] = hashtags
        logger.info(f"Updated hashtags: {hashtags}")
    
    if profiles:
        base_config["profiles"] = profiles
        logger.info(f"Updated profiles: {len(profiles)} profiles")
    
    if search_queries:
        base_config["searchQueries"] = search_queries
        logger.info(f"Updated search queries: {search_queries}")
    
    base_config["oldestPostDateUnified"] = f"{days_back} days"
    base_config["resultsPerPage"] = results_per_page
    
    return base_config


def add_hashtags_to_config(config: Dict[str, Any], 
                          new_hashtags: List[str]) -> Dict[str, Any]:
    """
    Add new hashtags to existing configuration.
    
    Args:
        config (Dict[str, Any]): Existing configuration
        new_hashtags (List[str]): Hashtags to add
        
    Returns:
        Dict[str, Any]: Updated configuration
    """
    current_hashtags = config.get("hashtags", [])
    updated_hashtags = list(set(current_hashtags + new_hashtags))
    config["hashtags"] = updated_hashtags
    
    logger.info(f"Added {len(new_hashtags)} hashtags, total: {len(updated_hashtags)}")
    return config


def add_profiles_to_config(config: Dict[str, Any], 
                          new_profiles: List[str]) -> Dict[str, Any]:
    """
    Add new profiles to existing configuration.
    
    Args:
        config (Dict[str, Any]): Existing configuration
        new_profiles (List[str]): Profiles to add
        
    Returns:
        Dict[str, Any]: Updated configuration
    """
    current_profiles = config.get("profiles", [])
    updated_profiles = list(set(current_profiles + new_profiles))
    config["profiles"] = updated_profiles
    
    logger.info(f"Added {len(new_profiles)} profiles, total: {len(updated_profiles)}")
    return config


def set_time_range(config: Dict[str, Any], days: int) -> Dict[str, Any]:
    """
    Set time range for content scraping.
    
    Args:
        config (Dict[str, Any]): Configuration to modify
        days (int): Number of days to look back
        
    Returns:
        Dict[str, Any]: Updated configuration
    """
    config["oldestPostDateUnified"] = f"{days} days"
    logger.info(f"Set time range to {days} days")
    return config


def set_results_limit(config: Dict[str, Any], limit: int) -> Dict[str, Any]:
    """
    Set results per page limit.
    
    Args:
        config (Dict[str, Any]): Configuration to modify
        limit (int): Results per page limit
        
    Returns:
        Dict[str, Any]: Updated configuration
    """
    config["resultsPerPage"] = limit
    logger.info(f"Set results per page to {limit}")
    return config