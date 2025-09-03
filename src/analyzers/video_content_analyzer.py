"""
Video content analyzer using Twelve Labs AI - modular version.

Single responsibility: Coordinate video analysis using specialized detectors.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from src.api_clients.twelve_labs.client import TwelveLabsClient
from src.analyzers.car_brand_detector import detect_car_brands
from src.analyzers.car_type_detector import detect_car_types
from src.analyzers.hook_detector import analyze_video_hooks
from src.analyzers.transition_detector import analyze_transitions

logger = logging.getLogger(__name__)


class VideoContentAnalyzer:
    """
    Analyzes video content using Twelve Labs AI to extract:
    - Car types and brands featured
    - Video hooks and engagement elements  
    - Transition styles and effects
    """
    
    def __init__(self, index_name: str = "car_content_analysis"):
        """
        Initialize video content analyzer.
        
        Args:
            index_name (str): Name of the Twelve Labs index to use
        """
        self.client = TwelveLabsClient()
        self.index_name = index_name
        self.index_id = None
        
        # Get or create analysis index
        self._setup_index()
    
    def _setup_index(self):
        """
        Set up Twelve Labs index for video analysis.
        
        Raises:
            Exception: If index setup fails
        """
        try:
            # Try to find existing index
            existing_index = self.client.get_index_by_name(self.index_name)
            
            if existing_index:
                self.index_id = existing_index["id"]
                logger.info(f"Using existing index: {self.index_id}")
            else:
                # Create new index
                new_index = self.client.create_index(self.index_name)
                self.index_id = new_index["id"]
                logger.info(f"Created new index: {self.index_id}")
                
        except Exception as e:
            logger.error(f"Failed to setup index: {e}")
            raise
    
    def analyze_videos_batch(self, video_urls: List[str], max_retries: int = 2) -> List[Dict[str, Any]]:
        """
        Analyze multiple videos in batch and clean up index afterward.
        
        Args:
            video_urls (List[str]): List of video URLs to analyze
            max_retries (int): Maximum retry attempts for failed videos
            
        Returns:
            List[Dict[str, Any]]: List of analysis results (successful only)
        """
        results = []
        failed_videos = []
        
        logger.info(f"Starting batch analysis of {len(video_urls)} videos")
        
        for i, video_url in enumerate(video_urls, 1):
            logger.info(f"Processing video {i}/{len(video_urls)}: {video_url}")
            
            try:
                result = self.analyze_video_content(video_url, max_retries=max_retries)
                results.append(result)
                logger.info(f"✅ Successfully analyzed video {i}/{len(video_urls)}")
                
            except Exception as e:
                logger.error(f"❌ Failed to analyze video {i}/{len(video_urls)}: {e}")
                failed_videos.append({
                    "video_url": video_url,
                    "error": str(e)
                })
        
        # Clean up the entire index after batch processing
        logger.info("Cleaning up Twelve Labs index to avoid storage costs")
        cleanup_success = self._cleanup_index()
        
        if cleanup_success:
            logger.info("✅ Index cleanup successful - no storage costs")
        else:
            logger.warning("⚠️ Index cleanup failed - may incur storage costs")
        
        # Log batch results
        logger.info(f"Batch analysis complete:")
        logger.info(f"  ✅ Successful: {len(results)}")
        logger.info(f"  ❌ Failed: {len(failed_videos)}")
        
        return results
    
    def analyze_video_content(self, video_url: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Analyze video to extract car types, hooks, and transitions.
        
        Args:
            video_url (str): URL of the video to analyze
            max_retries (int): Maximum retry attempts for failed uploads
            
        Returns:
            Dict[str, Any]: Analysis results with car info, hooks, and transitions
        """
        # Upload and process video
        video_id = self._upload_and_process_video(video_url, max_retries)
        
        try:
            # Extract different types of analysis using specialized detectors
            car_analysis = self._analyze_car_content(video_id)
            hook_analysis = analyze_video_hooks(video_id, self.client)
            transition_analysis = analyze_transitions(video_id, self.client)
            general_insights = self._get_general_insights(video_id)
            
            analysis_results = {
                "video_url": video_url,
                "car_analysis": car_analysis,
                "hook_analysis": hook_analysis,
                "transition_analysis": transition_analysis,
                "general_insights": general_insights
            }
            
            # Clean up video immediately
            self._cleanup_video(video_id)
            
            logger.info(f"Analysis completed and video deleted for: {video_url}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Failed to extract analysis from video {video_url}: {e}")
            self._cleanup_video(video_id)
            raise
    
    def _upload_and_process_video(self, video_url: str, max_retries: int) -> str:
        """
        Upload video to Twelve Labs and wait for processing.
        
        Args:
            video_url (str): URL of video to upload
            max_retries (int): Maximum retry attempts
            
        Returns:
            str: Video ID after successful processing
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt}/{max_retries} for video: {video_url}")
                    time.sleep(5 * attempt)
                else:
                    logger.info(f"Starting analysis for video: {video_url}")
                
                # Upload video for analysis
                upload_result = self.client.upload_video(self.index_id, video_url)
                task_id = upload_result["task_id"]
                
                # Wait for processing to complete
                completion_result = self.client.wait_for_task_completion(task_id)
                return completion_result["video_id"]
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed for {video_url}: {e}")
                
                if attempt == max_retries:
                    raise Exception(f"Video analysis failed after {max_retries + 1} attempts: {last_error}")
                
                continue
    
    def _analyze_car_content(self, video_id: str) -> Dict[str, Any]:
        """
        Extract car-specific content from video.
        
        Args:
            video_id (str): Twelve Labs video ID
            
        Returns:
            Dict[str, Any]: Car analysis results
        """
        try:
            # Use gist to get topics and analyze for car content
            gist = self.client.gist(video_id=video_id, types=["topic", "hashtag"])
            
            # Extract basic car information from topics
            car_topics = []
            existing_brands = []
            
            # Analyze topics for car content
            if hasattr(gist, 'topics') and gist.topics:
                car_topics = [topic for topic in gist.topics 
                            if any(keyword in topic.lower() for keyword in ['car', 'automotive', 'vehicle'])]
                
                # Detect car types from topics
                car_types = detect_car_types(gist.topics)
            else:
                car_types = []
            
            # Force car brand detection (will analyze summary if no existing brands)
            car_brands = detect_car_brands(video_id, self.client, existing_brands)
            
            return {
                "car_brands": car_brands,
                "car_types": car_types,
                "car_topics": car_topics,
                "hashtags": gist.hashtags if hasattr(gist, 'hashtags') else []
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze car content: {e}")
            return {"car_brands": [], "car_types": [], "car_topics": [], "hashtags": []}
    
    def _get_general_insights(self, video_id: str) -> Dict[str, Any]:
        """
        Get general video insights and metadata.
        
        Args:
            video_id (str): Twelve Labs video ID
            
        Returns:
            Dict[str, Any]: General insights
        """
        try:
            # Get comprehensive analysis
            gist = self.client.gist(video_id=video_id, types=["title", "topic", "hashtag"])
            summary = self.client.summarize_video(video_id=video_id, type="summary")
            
            return {
                "suggested_title": gist.title if hasattr(gist, 'title') else None,
                "topics": gist.topics if hasattr(gist, 'topics') else [],
                "hashtags": gist.hashtags if hasattr(gist, 'hashtags') else [],
                "summary": summary.summary if hasattr(summary, 'summary') else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get general insights: {e}")
            return {"suggested_title": None, "topics": [], "hashtags": [], "summary": None}
    
    def _cleanup_video(self, video_id: str):
        """Clean up video to avoid storage costs."""
        try:
            self.client.delete_task(video_id)
        except:
            logger.warning(f"Could not clean up video {video_id}")
    
    def _cleanup_index(self) -> bool:
        """
        Delete the entire index to clean up all remaining videos.
        
        Returns:
            bool: True if cleanup successful
        """
        if not self.index_id:
            return True
        
        try:
            success = self.client.delete_index(self.index_id)
            if success:
                self.index_id = None
            return success
        except Exception as e:
            logger.error(f"Failed to delete index: {e}")
            return False