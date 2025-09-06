"""
TikTok scraper configuration for car edit content.

Single responsibility: Define TikTok scraping parameters and settings.
"""

from typing import Dict, List, Any


def get_car_edit_config() -> Dict[str, Any]:
    """
    Get configuration for scraping car edit content from TikTok.
    
    Returns:
        Dict[str, Any]: Apify TikTok scraper configuration
    """
    return {
        "excludePinnedPosts": True,
        "hashtags": [
            "caredit",
            "caredits"
        ],
        "maxProfilesPerQuery": 1,
        "oldestPostDateUnified": "7 days",
        "profileScrapeSections": [
            "videos"
        ],
        "profileSorting": "latest",
        "profiles": [
            "@vqrxzv",
            "@kazumi.zxc", 
            "@psyho71",
            "@prv5t1",
            "@mitovfx",
            "@benyx.yz",
            "@blen.yzf",
            "@iswearty.yz",
            "@jynxx.kxy",
            "@saicodime"
        ],
        "proxyCountryCode": "None",
        "resultsPerPage": 1,
        "scrapeRelatedVideos": False,
        "searchQueries": [
            "car edit",
            "car edits", 
            "car edit sounds"
        ],
        "shouldDownloadAvatars": False,
        "shouldDownloadCovers": True,
        "shouldDownloadMusicCovers": True,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadSubtitles": True,
        "shouldDownloadVideos": True
    }


def get_hashtag_list() -> List[str]:
    """
    Get list of hashtags for car edit content scraping.
    
    Returns:
        List[str]: List of hashtags to scrape
    """
    return ["caredit", "caredits"]


def get_profile_list() -> List[str]:
    """
    Get list of TikTok profiles for car edit content.
    
    Returns:
        List[str]: List of TikTok profile usernames
    """
    return [
        "@vqrxzv", "@kazumi.zxc", "@psyho71", "@prv5t1", "@mitovfx",
        "@benyx.yz", "@blen.yzf", "@iswearty.yz", "@jynxx.kxy", "@saicodime"
    ]


def get_search_queries() -> List[str]:
    """
    Get list of search queries for car edit content.
    
    Returns:
        List[str]: List of search terms
    """
    return ["car edit", "car edits", "car edit sounds"]