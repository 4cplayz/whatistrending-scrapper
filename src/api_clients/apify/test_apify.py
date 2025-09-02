"""
Test script to explore Apify API structure and data format.

Single responsibility: Test and log actual API responses.
"""

import json
import logging
from typing import Dict, Any
from src.api_clients.apify.config_builder import create_custom_config
from src.api_clients.apify.config_validator import validate_config
from src.api_clients.apify.run_scraper import run_tiktok_scraper, get_scraper_status
from src.api_clients.apify.get_results import get_scraper_results, parse_video_data

logger = logging.getLogger(__name__)


def test_config_creation() -> Dict[str, Any]:
    """
    Test configuration creation and validation.
    
    Returns:
        Dict[str, Any]: Test configuration
    """
    logger.info("=== Testing Config Creation ===")
    
    # Test custom config creation
    custom_config = create_custom_config(
        hashtags=["caredit", "cars"],
        days_back=3,
        results_per_page=2
    )
    
    # Validate config
    is_valid, error = validate_config(custom_config)
    
    if is_valid:
        logger.info("✅ Configuration is valid")
        logger.info(f"Config preview: {json.dumps(custom_config, indent=2)}")
    else:
        logger.error(f"❌ Configuration invalid: {error}")
    
    return custom_config


def simulate_scraper_response() -> Dict[str, Any]:
    """
    Simulate expected TikTok scraper response structure.
    
    Returns:
        Dict[str, Any]: Simulated video data response
    """
    logger.info("=== Simulating Scraper Response ===")
    
    # Based on typical TikTok scraper response
    simulated_response = {
        "id": "7234567890123456789",
        "text": "Amazing car edit with epic music 🔥 #caredit #cars",
        "webVideoUrl": "https://www.tiktok.com/@user/video/7234567890123456789",
        "hashtags": ["caredit", "cars", "automotive", "edit"],
        "musicMeta": {
            "musicName": "Epic Beat",
            "musicAuthor": "DJ Producer",
            "musicId": "123456"
        },
        "authorMeta": {
            "name": "car_editor_pro",
            "nickName": "Car Editor Pro",
            "id": "user123456",
            "verified": False
        },
        "videoMeta": {
            "duration": 30,
            "width": 720,
            "height": 1280,
            "covers": [
                "https://example.com/cover1.jpg",
                "https://example.com/cover2.jpg"
            ]
        },
        "stats": {
            "playCount": 125000,
            "diggCount": 8500,
            "commentCount": 230,
            "shareCount": 450
        },
        "createTime": "2025-09-01T12:00:00Z",
        "collected_at": "2025-09-02T18:00:00Z"
    }
    
    # Test parsing
    parsed_data = parse_video_data(simulated_response)
    
    logger.info("Raw response keys:", list(simulated_response.keys()))
    logger.info("Parsed data keys:", list(parsed_data.keys()))
    logger.info(f"Parsed video data: {json.dumps(parsed_data, indent=2)}")
    
    return parsed_data


def analyze_data_structure(sample_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Analyze data structure to plan database schema.
    
    Args:
        sample_data (Dict[str, Any]): Sample video data
        
    Returns:
        Dict[str, str]: Field types and database recommendations
    """
    logger.info("=== Analyzing Data Structure ===")
    
    structure_analysis = {
        "video_id": "VARCHAR (Primary Key)",
        "video_url": "TEXT (URL)",
        "description": "TEXT",
        "hashtags": "JSON Array",
        "music_title": "VARCHAR",
        "music_author": "VARCHAR", 
        "author_username": "VARCHAR",
        "author_nickname": "VARCHAR",
        "video_meta": "JSON Object",
        "stats": "JSON Object (views, likes, comments, shares)",
        "created_time": "TIMESTAMP",
        "scraped_at": "TIMESTAMP"
    }
    
    logger.info("Recommended database fields:")
    for field, db_type in structure_analysis.items():
        logger.info(f"  {field}: {db_type}")
    
    return structure_analysis


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    config = test_config_creation()
    sample_data = simulate_scraper_response() 
    db_structure = analyze_data_structure(sample_data)
    
    logger.info("=== Apify API Exploration Complete ===")
    logger.info("Next steps:")
    logger.info("1. Add APIFY_TOKEN to environment variables")
    logger.info("2. Test actual scraper run")
    logger.info("3. Design database schema based on structure analysis")