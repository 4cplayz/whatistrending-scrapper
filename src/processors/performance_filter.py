"""
Performance-based video filtering for quality content selection.

Single responsibility: Filter videos based on engagement and performance metrics.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def calculate_engagement_score(video: Dict[str, Any]) -> float:
    """
    Calculate engagement score for a video based on metrics.
    
    Args:
        video (Dict[str, Any]): Video data with stats
        
    Returns:
        float: Engagement score (higher is better)
    """
    try:
        views = video.get("playCount", 0)
        likes = video.get("diggCount", 0)
        comments = video.get("commentCount", 0)
        shares = video.get("shareCount", 0)
        
        if views == 0:
            return 0.0
        
        # Calculate engagement rate
        total_engagements = likes + comments + (shares * 3)  # Weight shares higher
        engagement_rate = total_engagements / views
        
        # Boost score for videos with high absolute numbers
        volume_boost = min(views / 10000, 2.0)  # Max 2x boost for 10k+ views
        
        score = engagement_rate + volume_boost
        
        logger.debug(f"Video {video.get('id')}: score={score:.3f}, views={views}, engagements={total_engagements}")
        return score
        
    except Exception as e:
        logger.error(f"Error calculating engagement score: {e}")
        return 0.0


def filter_by_performance(videos: List[Dict[str, Any]], 
                         min_views: int = 1000,
                         min_engagement_rate: float = 0.02) -> List[Dict[str, Any]]:
    """
    Filter videos by minimum performance thresholds.
    
    Args:
        videos (List[Dict[str, Any]]): List of video data
        min_views (int): Minimum view count required
        min_engagement_rate (float): Minimum engagement rate (2% default)
        
    Returns:
        List[Dict[str, Any]]: Filtered high-performance videos
    """
    high_performance = []
    filtered_count = 0
    
    for video in videos:
        views = video.get("playCount", 0)
        
        # Filter by minimum views
        if views < min_views:
            filtered_count += 1
            logger.debug(f"Filtered low views: {video.get('id')} ({views} views)")
            continue
        
        # Filter by engagement rate
        engagement_score = calculate_engagement_score(video)
        if engagement_score < min_engagement_rate:
            filtered_count += 1
            logger.debug(f"Filtered low engagement: {video.get('id')} (score: {engagement_score:.3f})")
            continue
        
        high_performance.append(video)
    
    logger.info(f"Performance filter: kept {len(high_performance)}, filtered {filtered_count}")
    return high_performance


def get_top_performers(videos: List[Dict[str, Any]], top_n: int = 50) -> List[Dict[str, Any]]:
    """
    Get top N performing videos by engagement score.
    
    Args:
        videos (List[Dict[str, Any]]): List of video data
        top_n (int): Number of top videos to return
        
    Returns:
        List[Dict[str, Any]]: Top performing videos sorted by engagement
    """
    # Calculate scores and sort
    videos_with_scores = []
    
    for video in videos:
        score = calculate_engagement_score(video)
        videos_with_scores.append((video, score))
    
    # Sort by score descending
    videos_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    top_videos = [video for video, score in videos_with_scores[:top_n]]
    
    logger.info(f"Selected top {len(top_videos)} performers from {len(videos)} videos")
    
    if top_videos:
        top_score = videos_with_scores[0][1]
        logger.info(f"Top video score: {top_score:.3f} (ID: {top_videos[0].get('id')})")
    
    return top_videos