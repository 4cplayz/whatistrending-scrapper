"""
Video content analyzer using Twelve Labs AI.

Single responsibility: Analyze videos to extract car types, hooks, and transitions.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from src.api_clients.twelve_labs.client import TwelveLabsClient

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
        
        if failed_videos:
            logger.warning("Failed videos:")
            for failed in failed_videos:
                logger.warning(f"  - {failed['video_url']}: {failed['error']}")
        
        return results
    
    def analyze_video_content(self, video_url: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Analyze video to extract car types, hooks, and transitions.
        
        Args:
            video_url (str): URL of the video to analyze
            max_retries (int): Maximum retry attempts for failed uploads
            
        Returns:
            Dict[str, Any]: Analysis results with car info, hooks, and transitions
            
        Raises:
            Exception: If analysis fails after all retries
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt}/{max_retries} for video: {video_url}")
                    # Wait before retry to avoid rate limits
                    time.sleep(5 * attempt)
                else:
                    logger.info(f"Starting analysis for video: {video_url}")
                
                # Upload video for analysis
                upload_result = self.client.upload_video(self.index_id, video_url)
                task_id = upload_result["task_id"]
                
                # Wait for processing to complete
                completion_result = self.client.wait_for_task_completion(task_id)
                video_id = completion_result["video_id"]
                
                # If we get here, upload and processing succeeded
                break
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed for {video_url}: {e}")
                
                if attempt == max_retries:
                    logger.error(f"All {max_retries + 1} attempts failed for {video_url}")
                    raise Exception(f"Video analysis failed after {max_retries + 1} attempts: {last_error}")
                
                continue
        
        try:
            
            # Extract different types of analysis
            analysis_results = {
                "video_id": video_id,
                "video_url": video_url,
                "car_analysis": self._analyze_car_content(video_id),
                "hook_analysis": self._analyze_video_hooks(video_id),
                "transition_analysis": self._analyze_transitions(video_id),
                "general_insights": self._get_general_insights(video_id)
            }
            
            # CRITICAL: Delete task immediately to avoid storage costs
            deletion_success = self.client.delete_task(task_id)
            if deletion_success:
                logger.info(f"Task {task_id} deleted from Twelve Labs to avoid storage costs")
            else:
                logger.warning(f"Failed to delete task {task_id} - may incur storage costs")
            
            # Remove video_id from results since video is deleted
            analysis_results.pop("video_id", None)
            
            logger.info(f"Analysis completed and video deleted for: {video_url}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Failed to extract analysis from video {video_url}: {e}")
            # Try to clean up the video even if analysis extraction failed
            try:
                self.client.delete_task(task_id)
                logger.info(f"Cleaned up failed task {task_id}")
            except:
                logger.warning(f"Could not clean up failed task {task_id}")
            raise
    
    def _cleanup_index(self) -> bool:
        """
        Delete the entire index to clean up all remaining videos.
        
        Returns:
            bool: True if cleanup successful
        """
        if not self.index_id:
            logger.warning("No index to clean up")
            return True
        
        try:
            success = self.client.delete_index(self.index_id)
            if success:
                # Reset index_id since it's deleted
                self.index_id = None
                logger.info("Index successfully deleted - no storage costs")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete index: {e}")
            return False
    
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
            gist = self.client.client.gist(video_id=video_id, types=["topic", "hashtag"])
            
            # Extract car-related information
            car_topics = []
            car_brands = []
            car_types = []
            
            # Analyze topics for car content
            if hasattr(gist, 'topics') and gist.topics:
                for topic in gist.topics:
                    topic_lower = topic.lower()
                    
                    # Car brands
                    car_brand_keywords = [
                        'ferrari', 'lamborghini', 'mclaren', 'porsche', 'bmw', 
                        'mercedes', 'audi', 'toyota', 'honda', 'nissan', 'subaru',
                        'bugatti', 'pagani', 'koenigsegg', 'ford', 'chevrolet'
                    ]
                    
                    for brand in car_brand_keywords:
                        if brand in topic_lower:
                            car_brands.append(brand.title())
                    
                    # Car types
                    car_type_keywords = [
                        'supercar', 'hypercar', 'sports car', 'jdm', 'muscle car',
                        'drift car', 'race car', 'luxury car', 'exotic car'
                    ]
                    
                    for car_type in car_type_keywords:
                        if car_type in topic_lower:
                            car_types.append(car_type.title())
                    
                    # General car topics
                    if any(keyword in topic_lower for keyword in ['car', 'automotive', 'vehicle']):
                        car_topics.append(topic)
            
            return {
                "car_brands": list(set(car_brands)),
                "car_types": list(set(car_types)),
                "car_topics": car_topics,
                "hashtags": gist.hashtags if hasattr(gist, 'hashtags') else []
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze car content: {e}")
            return {"car_brands": [], "car_types": [], "car_topics": [], "hashtags": []}
    
    def _analyze_video_hooks(self, video_id: str) -> Dict[str, Any]:
        """
        Analyze video hooks and engagement elements.
        
        Args:
            video_id (str): Twelve Labs video ID
            
        Returns:
            Dict[str, Any]: Hook analysis results
        """
        try:
            # Get video summary to identify hooks

            summary = self.client.summarize_video(video_id=video_id, type="summary")
            
            # Get title suggestions which often contain hooks
            title = self.client.client.gist(video_id=video_id, types=["title"])
            
            hooks = []
            engagement_elements = []
            
            # Analyze title for hook elements
            if hasattr(title, 'title') and title.title:
                title_text = title.title.lower()
                
                # Common hook patterns
                hook_patterns = [
                    'insane', 'crazy', 'epic', 'mind-blowing', 'incredible',
                    'unbelievable', 'amazing', 'shocking', 'viral', 'trending'
                ]
                
                for pattern in hook_patterns:
                    if pattern in title_text:
                        hooks.append(f"Uses '{pattern}' hook")
            
            # Analyze for engagement elements
            if hasattr(summary, 'summary') and summary.summary:
                summary_text = summary.summary.lower()
                
                engagement_patterns = [
                    ('sound', 'Audio-focused content'),
                    ('music', 'Music-driven engagement'),
                    ('edit', 'Editing-focused content'),
                    ('transition', 'Transition showcase'),
                    ('compilation', 'Compilation format')
                ]
                
                for pattern, description in engagement_patterns:
                    if pattern in summary_text:
                        engagement_elements.append(description)
            
            return {
                "hooks": hooks,
                "engagement_elements": engagement_elements,
                "title": title.title if hasattr(title, 'title') else None,
                "summary": summary.summary if hasattr(summary, 'summary') else None
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze hooks: {e}")
            return {"hooks": [], "engagement_elements": [], "title": None, "summary": None}
    
    def _analyze_transitions(self, video_id: str) -> Dict[str, Any]:
        """
        Analyze video transitions and effects.
        
        Args:
            video_id (str): Twelve Labs video ID
            
        Returns:
            Dict[str, Any]: Transition analysis results
        """
        try:
            # Get detailed summary for transition analysis
            summary = self.client.summarize_video(video_id=video_id, type="summary")
            
            transitions = []
            effects = []
            
            if hasattr(summary, 'summary') and summary.summary:
                summary_text = summary.summary.lower()
                
                # Transition keywords
                transition_keywords = [
                    ('cut', 'Quick cuts'),
                    ('fade', 'Fade transitions'),
                    ('zoom', 'Zoom effects'),
                    ('slow motion', 'Slow motion'),
                    ('speed up', 'Speed ramping'),
                    ('beat drop', 'Beat-synced transitions'),
                    ('sync', 'Music synchronization')
                ]
                
                for keyword, description in transition_keywords:
                    if keyword in summary_text:
                        transitions.append(description)
                
                # Visual effects
                effect_keywords = [
                    ('filter', 'Color filters'),
                    ('glow', 'Glow effects'),
                    ('blur', 'Motion blur'),
                    ('shake', 'Camera shake'),
                    ('lens flare', 'Lens flare'),
                    ('vhs', 'VHS aesthetic'),
                    ('neon', 'Neon effects')
                ]
                
                for keyword, description in effect_keywords:
                    if keyword in summary_text:
                        effects.append(description)
            
            return {
                "transitions": transitions,
                "effects": effects,
                "style": self._determine_editing_style(transitions + effects)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze transitions: {e}")
            return {"transitions": [], "effects": [], "style": "Unknown"}
    
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
            gist = self.client.client.gist(video_id=video_id, types=["title", "topic", "hashtag"])
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
    
    def _determine_editing_style(self, elements: list) -> str:
        """
        Determine overall editing style based on elements.
        
        Args:
            elements (list): List of transition and effect elements
            
        Returns:
            str: Determined editing style
        """
        if not elements:
            return "Minimal"
        
        if len(elements) >= 4:
            return "Heavy editing"
        elif len(elements) >= 2:
            return "Moderate editing"
        else:
            return "Light editing"