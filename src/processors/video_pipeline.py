"""
Complete video processing pipeline that filters and prepares data for storage.

Single responsibility: Coordinate the entire video filtering and processing workflow.
"""

import logging
from typing import List, Dict, Any
from src.processors.video_validator import validate_video_data
from src.processors.duplicate_filter import remove_duplicates, detect_similar_content
from src.processors.performance_filter import filter_by_performance, get_top_performers

logger = logging.getLogger(__name__)


def process_scraped_videos(raw_videos: List[Dict[str, Any]], 
                          config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process raw scraped videos through complete filtering pipeline.
    
    Args:
        raw_videos (List[Dict[str, Any]]): Raw video data from Apify
        config (Dict[str, Any]): Processing configuration options
        
    Returns:
        Dict[str, Any]: Processing results with filtered videos and stats
    """
    if not config:
        config = get_default_config()
    
    logger.info(f"Starting video processing pipeline with {len(raw_videos)} raw videos")
    
    stats = {
        "input_count": len(raw_videos),
        "validation_failed": 0,
        "duplicates_removed": 0,
        "similar_removed": 0,
        "performance_filtered": 0,
        "final_count": 0
    }
    
    # Step 1: Validate video data
    valid_videos = []
    for video in raw_videos:
        is_valid, reason = validate_video_data(video)
        if is_valid:
            valid_videos.append(video)
        else:
            stats["validation_failed"] += 1
            logger.debug(f"Invalid video {video.get('id', 'unknown')}: {reason}")
    
    logger.info(f"Step 1 - Validation: {len(valid_videos)} valid, {stats['validation_failed']} invalid")
    
    # Step 2: Remove exact duplicates
    original_count = len(valid_videos)
    unique_videos = remove_duplicates(valid_videos)
    stats["duplicates_removed"] = original_count - len(unique_videos)
    
    # Step 3: Remove similar content
    original_count = len(unique_videos)
    diverse_videos = detect_similar_content(unique_videos)
    stats["similar_removed"] = original_count - len(diverse_videos)
    
    # Step 4: Filter by performance
    original_count = len(diverse_videos)
    high_performance = filter_by_performance(
        diverse_videos,
        min_views=config.get("min_views", 1000),
        min_engagement_rate=config.get("min_engagement_rate", 0.02)
    )
    stats["performance_filtered"] = original_count - len(high_performance)
    
    # Step 5: Get top performers
    top_videos = get_top_performers(
        high_performance,
        top_n=config.get("max_videos", 50)
    )
    
    stats["final_count"] = len(top_videos)
    
    logger.info(f"Pipeline complete: {stats['input_count']} → {stats['final_count']} videos")
    
    return {
        "videos": top_videos,
        "stats": stats,
        "config": config
    }


def get_default_config() -> Dict[str, Any]:
    """
    Get default processing configuration.
    
    Returns:
        Dict[str, Any]: Default configuration settings
    """
    return {
        "min_views": 1000,           # Minimum view count
        "min_engagement_rate": 0.02, # Minimum 2% engagement rate
        "max_videos": 50,            # Maximum videos to keep
        "enable_similarity_check": True,
        "enable_performance_filter": True
    }


def log_processing_summary(result: Dict[str, Any]) -> None:
    """
    Log detailed processing summary.
    
    Args:
        result (Dict[str, Any]): Processing result from process_scraped_videos
    """
    stats = result["stats"]
    videos = result["videos"]
    
    logger.info("=== VIDEO PROCESSING SUMMARY ===")
    logger.info(f"Input videos: {stats['input_count']}")
    logger.info(f"Validation failures: {stats['validation_failed']}")
    logger.info(f"Duplicates removed: {stats['duplicates_removed']}")
    logger.info(f"Similar content removed: {stats['similar_removed']}")
    logger.info(f"Performance filtered: {stats['performance_filtered']}")
    logger.info(f"Final videos: {stats['final_count']}")
    
    if videos:
        top_video = videos[0]
        logger.info(f"Top video: @{top_video.get('authorMeta', {}).get('name')} - {top_video.get('playCount', 0)} views")
    
    retention_rate = (stats['final_count'] / stats['input_count']) * 100 if stats['input_count'] > 0 else 0
    logger.info(f"Retention rate: {retention_rate:.1f}%")