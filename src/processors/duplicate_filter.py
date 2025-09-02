"""
Duplicate video detection and removal.

Single responsibility: Identify and filter duplicate videos from scraped data.
"""

import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


def remove_duplicates(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate videos based on video ID.
    
    Args:
        videos (List[Dict[str, Any]]): List of video data
        
    Returns:
        List[Dict[str, Any]]: Deduplicated video list
    """
    seen_ids: Set[str] = set()
    unique_videos = []
    duplicates_count = 0
    
    for video in videos:
        video_id = video.get("id")
        
        if not video_id:
            logger.warning("Video without ID found, skipping")
            continue
            
        if video_id in seen_ids:
            duplicates_count += 1
            logger.debug(f"Duplicate found: {video_id}")
            continue
            
        seen_ids.add(video_id)
        unique_videos.append(video)
    
    logger.info(f"Removed {duplicates_count} duplicates, kept {len(unique_videos)} unique videos")
    return unique_videos


def detect_similar_content(videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect videos with very similar descriptions (potential duplicates).
    
    Args:
        videos (List[Dict[str, Any]]): List of video data
        
    Returns:
        List[Dict[str, Any]]: Videos with similar content removed
    """
    unique_videos = []
    seen_texts: Set[str] = set()
    similar_removed = 0
    
    for video in videos:
        text = video.get("text", "").lower().strip()
        
        # Skip videos with empty or very short text
        if len(text) < 10:
            unique_videos.append(video)
            continue
            
        # Create a simplified version for comparison
        simplified_text = "".join(text.split())[:100]  # Remove spaces, take first 100 chars
        
        if simplified_text in seen_texts:
            similar_removed += 1
            logger.debug(f"Similar content found: {video.get('id')}")
            continue
            
        seen_texts.add(simplified_text)
        unique_videos.append(video)
    
    logger.info(f"Removed {similar_removed} videos with similar content")
    return unique_videos