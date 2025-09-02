"""
Video data validation and quality checks.

Single responsibility: Validate individual video data quality and completeness.
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


def validate_video_data(video: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate if video data is complete and usable.
    
    Args:
        video (Dict[str, Any]): Raw video data from Apify
        
    Returns:
        Tuple[bool, str]: (is_valid, reason_if_invalid)
    """
    try:
        # Check required fields
        required_fields = ["id", "webVideoUrl", "authorMeta"]
        for field in required_fields:
            if not video.get(field):
                return False, f"Missing required field: {field}"
        
        # Check video ID format
        video_id = video.get("id", "")
        if not video_id or len(video_id) < 10:
            return False, "Invalid video ID format"
        
        # Check author data
        author = video.get("authorMeta", {})
        if not author.get("name"):
            return False, "Missing author name"
        
        # Check for minimum data quality
        if not video.get("text") and not video.get("hashtags"):
            return False, "No text or hashtags - low quality content"
        
        logger.debug(f"Video {video_id} passed validation")
        return True, ""
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False, f"Validation exception: {e}"