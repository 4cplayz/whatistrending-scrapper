"""
Video data model for database storage.

Single responsibility: Define video table structure and data validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import json


@dataclass
class VideoModel:
    """
    Video model representing a filtered TikTok video ready for storage.
    
    Based on real Apify data structure and filtering pipeline results.
    """
    
    # Primary identifiers
    video_id: str
    video_url: str
    
    # Content data
    description: str
    
    # Author information
    author_username: str
    
    # Optional fields with defaults
    hashtags: List[Dict[str, str]] = field(default_factory=list)
    author_nickname: Optional[str] = None
    author_verified: bool = False
    author_followers: Optional[int] = None
    
    # Music/Audio data
    music_title: Optional[str] = None
    music_author: Optional[str] = None
    music_id: Optional[str] = None
    
    # Video metadata
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    cover_url: Optional[str] = None
    
    # Performance metrics
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    engagement_score: float = 0.0
    
    # Timestamps
    created_at: Optional[datetime] = None
    scraped_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    # Processing metadata
    scrape_source: str = "apify"  # hashtag, profile, search
    quality_score: Optional[float] = None
    
    # Analysis data (for Twelve Labs integration)
    analysis_status: str = "completed"  # pending, processing, completed, failed  
    analysis_results: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert video model to dictionary for database operations.
        
        Returns:
            Dict[str, Any]: Dictionary representation for database storage
        """
        return {
            "video_id": self.video_id,
            "video_url": self.video_url,
            "description": self.description,
            "hashtags": self.hashtags if self.hashtags else [],
            "author_username": self.author_username,
            "author_nickname": self.author_nickname,
            "author_verified": self.author_verified,
            "author_followers": self.author_followers,
            "music_title": self.music_title,
            "music_author": self.music_author,
            "music_id": self.music_id,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "cover_url": self.cover_url,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "engagement_score": self.engagement_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "scrape_source": self.scrape_source,
            "quality_score": self.quality_score,
            "analysis_status": self.analysis_status,
            "analysis_results": self.analysis_results
        }
    
    @classmethod
    def from_apify_data(cls, apify_video: Dict[str, Any], engagement_score: float = 0.0) -> "VideoModel":
        """
        Create VideoModel from filtered Apify video data.
        
        Args:
            apify_video (Dict[str, Any]): Filtered video data from Apify
            engagement_score (float): Calculated engagement score
            
        Returns:
            VideoModel: Video model instance ready for database storage
        """
        author_meta = apify_video.get("authorMeta", {})
        music_meta = apify_video.get("musicMeta", {})
        video_meta = apify_video.get("videoMeta", {})
        
        # Convert Unix timestamp to datetime
        created_timestamp = apify_video.get("createTime")
        created_at = None
        if created_timestamp:
            try:
                created_at = datetime.fromtimestamp(created_timestamp)
            except (ValueError, TypeError):
                pass
        
        return cls(
            video_id=apify_video.get("id", ""),
            video_url=apify_video.get("webVideoUrl", ""),  # Keep TikTok page URL for database
            description=apify_video.get("text", ""),
            hashtags=apify_video.get("hashtags", []),
            author_username=author_meta.get("name", ""),
            author_nickname=author_meta.get("nickName"),
            author_verified=author_meta.get("verified", False),
            author_followers=author_meta.get("fans"),
            music_title=music_meta.get("musicName"),
            music_author=music_meta.get("musicAuthor"),
            music_id=music_meta.get("musicId"),
            duration=video_meta.get("duration"),
            width=video_meta.get("width"),
            height=video_meta.get("height"),
            cover_url=video_meta.get("coverUrl"),
            views=apify_video.get("playCount", 0),
            likes=apify_video.get("diggCount", 0),
            comments=apify_video.get("commentCount", 0),
            shares=apify_video.get("shareCount", 0),
            engagement_score=engagement_score,
            created_at=created_at,
            scraped_at=datetime.now(),
            processed_at=datetime.now(),
            scrape_source=apify_video.get("input", "unknown"),
            analysis_status="completed"  # Filtered videos are ready for newsletter
        )
    
    def update_analysis_results(self, analysis_data: Dict[str, Any]) -> None:
        """
        Update video model with Twelve Labs analysis results.
        
        Args:
            analysis_data (Dict[str, Any]): Analysis results from Twelve Labs
        """
        self.analysis_results = analysis_data
        self.analysis_status = "completed"