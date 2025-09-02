"""
Configuration validation for TikTok scraper settings.

Single responsibility: Validate scraper configuration parameters.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger(__name__)


def validate_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate TikTok scraper configuration for required fields and formats.
    
    Args:
        config (Dict[str, Any]): Configuration to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        # Check required fields
        required_fields = ["resultsPerPage", "oldestPostDateUnified"]
        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"
        
        # Validate at least one scraping method
        has_hashtags = config.get("hashtags") and len(config["hashtags"]) > 0
        has_profiles = config.get("profiles") and len(config["profiles"]) > 0  
        has_queries = config.get("searchQueries") and len(config["searchQueries"]) > 0
        
        if not (has_hashtags or has_profiles or has_queries):
            return False, "Must have at least one: hashtags, profiles, or search queries"
        
        # Validate results per page
        if not isinstance(config["resultsPerPage"], int) or config["resultsPerPage"] <= 0:
            return False, "resultsPerPage must be positive integer"
        
        logger.info("Configuration validation passed")
        return True, None
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False, f"Validation error: {e}"


def validate_hashtags(hashtags: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate hashtag format and content.
    
    Args:
        hashtags (List[str]): List of hashtags to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not hashtags or not isinstance(hashtags, list):
        return False, "Hashtags must be a non-empty list"
    
    for hashtag in hashtags:
        if not isinstance(hashtag, str) or len(hashtag.strip()) == 0:
            return False, "All hashtags must be non-empty strings"
    
    return True, None


def validate_profiles(profiles: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate TikTok profile format.
    
    Args:
        profiles (List[str]): List of profile usernames to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not profiles or not isinstance(profiles, list):
        return False, "Profiles must be a non-empty list"
    
    for profile in profiles:
        if not isinstance(profile, str):
            return False, "All profiles must be strings"
        
        # Check if profile starts with @
        if not profile.startswith("@"):
            return False, f"Profile '{profile}' must start with '@'"
    
    return True, None


def validate_time_range(time_range: str) -> Tuple[bool, Optional[str]]:
    """
    Validate time range format for oldestPostDateUnified.
    
    Args:
        time_range (str): Time range string (e.g., "7 days")
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(time_range, str):
        return False, "Time range must be a string"
    
    valid_formats = ["days", "hours", "weeks"]
    
    try:
        parts = time_range.strip().split()
        if len(parts) != 2:
            return False, "Time range must be in format 'N days/hours/weeks'"
        
        number, unit = parts
        int(number)  # Check if number is valid
        
        if unit not in valid_formats:
            return False, f"Time unit must be one of: {valid_formats}"
        
        return True, None
        
    except ValueError:
        return False, "First part of time range must be a number"