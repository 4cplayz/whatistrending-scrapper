"""
Video data storage operations for Supabase database.

Single responsibility: Handle video data insertion and retrieval operations.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.database.client.supabase_client import get_supabase_client
from src.database.models.video_model import VideoModel

logger = logging.getLogger(__name__)


def store_video(video: VideoModel) -> Optional[str]:
    """
    Store a single video in the database.
    
    Args:
        video (VideoModel): Video model to store
        
    Returns:
        Optional[str]: Database UUID if successful, None if failed
        
    Raises:
        ValueError: If video data is invalid
        ConnectionError: If database connection fails
    """
    try:
        supabase = get_supabase_client()
        video_data = video.to_dict()
        
        response = (
            supabase.table("videos")
            .upsert(video_data, on_conflict="video_id")
            .execute()
        )
        
        if response.data:
            db_id = response.data[0].get("id")
            logger.info(f"Stored video {video.video_id} with DB ID: {db_id}")
            return db_id
        else:
            logger.error(f"Failed to store video {video.video_id}: No data returned")
            return None
            
    except Exception as e:
        logger.error(f"Error storing video {video.video_id}: {e}")
        raise ValueError(f"Video storage failed: {e}")


def store_videos_batch(videos: List[VideoModel]) -> Dict[str, Any]:
    """
    Store multiple videos in a single batch operation.
    
    Args:
        videos (List[VideoModel]): List of video models to store
        
    Returns:
        Dict[str, Any]: Storage results with success/failure counts
        
    Raises:
        ConnectionError: If database connection fails
    """
    try:
        if not videos:
            return {"success": 0, "failed": 0, "total": 0}
        
        supabase = get_supabase_client()
        video_data_list = [video.to_dict() for video in videos]
        
        response = (
            supabase.table("videos")
            .upsert(video_data_list, on_conflict="video_id")
            .execute()
        )
        
        success_count = len(response.data) if response.data else 0
        failed_count = len(videos) - success_count
        
        logger.info(f"Batch storage: {success_count} success, {failed_count} failed")
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(videos),
            "stored_ids": [item.get("id") for item in (response.data or [])]
        }
        
    except Exception as e:
        logger.error(f"Batch storage failed: {e}")
        raise ConnectionError(f"Database batch operation failed: {e}")


def get_video_by_tiktok_id(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve video by TikTok video ID.
    
    Args:
        video_id (str): TikTok video ID
        
    Returns:
        Optional[Dict[str, Any]]: Video data if found, None otherwise
    """
    try:
        supabase = get_supabase_client()
        
        response = (
            supabase.table("videos")
            .select("*")
            .eq("video_id", video_id)
            .execute()
        )
        
        if response.data:
            logger.debug(f"Found video {video_id}")
            return response.data[0]
        else:
            logger.debug(f"Video {video_id} not found")
            return None
            
    except Exception as e:
        logger.error(f"Error retrieving video {video_id}: {e}")
        return None


def check_video_exists(video_id: str) -> bool:
    """
    Check if video already exists in database.
    
    Args:
        video_id (str): TikTok video ID to check
        
    Returns:
        bool: True if video exists, False otherwise
    """
    try:
        video = get_video_by_tiktok_id(video_id)
        return video is not None
        
    except Exception as e:
        logger.error(f"Error checking video existence {video_id}: {e}")
        return False


def get_videos_for_analysis(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get videos that are pending analysis.
    
    Args:
        limit (int): Maximum number of videos to return
        
    Returns:
        List[Dict[str, Any]]: Videos pending analysis
    """
    try:
        supabase = get_supabase_client()
        
        response = (
            supabase.table("videos")
            .select("*")
            .eq("analysis_status", "pending")
            .order("engagement_score", desc=True)
            .limit(limit)
            .execute()
        )
        
        videos = response.data or []
        logger.info(f"Found {len(videos)} videos pending analysis")
        return videos
        
    except Exception as e:
        logger.error(f"Error getting videos for analysis: {e}")
        return []


def update_analysis_status(video_id: str, status: str, 
                          results: Optional[Dict[str, Any]] = None) -> bool:
    """
    Update video analysis status and results.
    
    Args:
        video_id (str): TikTok video ID
        status (str): New analysis status
        results (Optional[Dict[str, Any]]): Analysis results if completed
        
    Returns:
        bool: True if updated successfully, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        update_data = {
            "analysis_status": status,
            "analysis_started_at": datetime.now().isoformat() if status == "processing" else None,
            "analysis_completed_at": datetime.now().isoformat() if status == "completed" else None
        }
        
        if results:
            update_data["analysis_results"] = results
        
        response = (
            supabase.table("videos")
            .update(update_data)
            .eq("video_id", video_id)
            .execute()
        )
        
        success = bool(response.data)
        if success:
            logger.info(f"Updated analysis status for {video_id}: {status}")
        else:
            logger.error(f"Failed to update analysis status for {video_id}")
            
        return success
        
    except Exception as e:
        logger.error(f"Error updating analysis status for {video_id}: {e}")
        return False