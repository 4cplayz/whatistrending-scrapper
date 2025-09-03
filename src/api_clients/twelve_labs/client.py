"""
Twelve Labs API client for video analysis.

Single responsibility: Handle Twelve Labs API interactions and authentication.
"""

import os
import logging
from typing import Optional, Dict, Any
from twelvelabs import TwelveLabs

logger = logging.getLogger(__name__)


class TwelveLabsClient:
    """
    Client wrapper for Twelve Labs Video Understanding Platform.
    
    Handles authentication, index management, and basic API operations.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Twelve Labs client.
        
        Args:
            api_key (Optional[str]): API key, defaults to environment variable
            
        Raises:
            ValueError: If API key is not provided
        """
        self.api_key = api_key or os.environ.get("TWELVE_LABS_API_KEY")
        
        if not self.api_key:
            raise ValueError("TWELVE_LABS_API_KEY must be set")
        
        try:
            # Try new SDK initialization format first
            self.client = TwelveLabs(api_key=self.api_key)
            logger.info("Twelve Labs client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twelve Labs client: {e}")
            # Try alternative initialization
            try:
                from twelvelabs import TwelveLabsClient as TLClient
                self.client = TLClient(api_key=self.api_key)
                logger.info("Twelve Labs client initialized with alternative method")
            except Exception as e2:
                logger.error(f"Both initialization methods failed: {e}, {e2}")
                raise
    
    def create_index(self, index_name: str) -> Dict[str, Any]:
        """
        Create a new index for video analysis.
        
        Args:
            index_name (str): Name for the new index
            
        Returns:
            Dict[str, Any]: Index creation response
            
        Raises:
            Exception: If index creation fails
        """
        try:
            from twelvelabs.indexes import IndexesCreateRequestModelsItem
            
            index = self.client.indexes.create(
                index_name=index_name,
                models=[
                    IndexesCreateRequestModelsItem(
                        model_name="pegasus1.2",
                        model_options=["visual", "audio"],
                    ),
                ]
            )
            
            logger.info(f"Created Twelve Labs index: {index.id}")
            return {
                "id": index.id,
                "name": index_name
            }
            
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            raise
    
    def get_index_by_name(self, index_name: str) -> Optional[Dict[str, Any]]:
        """
        Find index by name.
        
        Args:
            index_name (str): Name of the index to find
            
        Returns:
            Optional[Dict[str, Any]]: Index info if found, None otherwise
        """
        try:
            indexes_response = self.client.indexes.list()
            indexes = indexes_response.data if hasattr(indexes_response, 'data') else indexes_response
            
            for index in indexes:
                if hasattr(index, 'index_name') and index.index_name == index_name:
                    return {
                        "id": index.id,
                        "name": index.index_name
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to list indexes: {e}")
            return None
    
    def upload_video(self, index_id: str, video_url: str) -> Dict[str, Any]:
        """
        Upload video to Twelve Labs for analysis.
        
        Args:
            index_id (str): ID of the target index
            video_url (str): URL of the video to analyze
            
        Returns:
            Dict[str, Any]: Upload task response
            
        Raises:
            Exception: If upload fails
        """
        try:
            task = self.client.tasks.create(
                index_id=index_id,
                video_url=video_url
            )
            
            logger.info(f"Created upload task: {task.id} for video: {video_url}")
            return {
                "task_id": task.id,
                "video_url": video_url,
                "index_id": index_id
            }
            
        except Exception as e:
            logger.error(f"Failed to upload video {video_url}: {e}")
            raise
    
    def wait_for_task_completion(self, task_id: str) -> Dict[str, Any]:
        """
        Wait for video indexing task to complete.
        
        Args:
            task_id (str): ID of the task to monitor
            
        Returns:
            Dict[str, Any]: Completed task response
            
        Raises:
            Exception: If task fails or times out
        """
        try:
            def status_callback(task):
                logger.info(f"Task {task_id} status: {task.status}")
            
            task = self.client.tasks.wait_for_done(task_id, callback=status_callback)
            
            if task.status != "ready":
                raise Exception(f"Indexing failed with status {task.status}")
            
            logger.info(f"Task completed successfully. Video ID: {task.video_id}")
            return {
                "task_id": task_id,
                "video_id": task.video_id,
                "status": task.status
            }
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            raise

    def summarize_video(self, video_id: str, type: str) -> Dict[str, Any]:
        """
        Summarize a video.

        Args:
            video_id (str): The ID of the video to summarize.
            type (str): The type of summary to generate.

        Returns:
            Dict[str, Any]: The summary of the video.
        """
        try:
            summary = self.client.summarize(video_id=video_id, type=type)
            logger.info(f"Summarized video {video_id} with type {type}")
            return summary
        except Exception as e:
            logger.error(f"Failed to summarize video {video_id}: {e}")
            raise
    
    def analyze(self, video_id: str, prompt: str) -> Dict[str, Any]:
        """
        Analyze a video with custom prompt.

        Args:
            video_id (str): The ID of the video to analyze.
            prompt (str): Custom prompt for analysis.

        Returns:
            Dict[str, Any]: The analysis result.
        """
        try:
            result = self.client.analyze(video_id=video_id, prompt=prompt)
            logger.info(f"Analyzed video {video_id} with custom prompt")
            return result
        except Exception as e:
            logger.error(f"Failed to analyze video {video_id}: {e}")
            raise
    
    def gist(self, video_id: str, types: list) -> Dict[str, Any]:
        """
        Get gist (title, topics, hashtags) for a video.

        Args:
            video_id (str): The ID of the video.
            types (list): List of gist types to retrieve.

        Returns:
            Dict[str, Any]: The gist result.
        """
        try:
            result = self.client.gist(video_id=video_id, types=types)
            logger.info(f"Got gist for video {video_id} with types {types}")
            return result
        except Exception as e:
            logger.error(f"Failed to get gist for video {video_id}: {e}")
            raise

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from Twelve Labs.
        
        Args:
            task_id (str): The ID of the task to delete.
            
        Returns:
            bool: True if deletion successful
        """
        try:
            self.client.tasks.delete(task_id)
            logger.info(f"Deleted task {task_id} from Twelve Labs")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False
    
    def delete_index(self, index_id: str) -> bool:
        """
        Delete entire index to clean up all videos at once.
        
        Args:
            index_id (str): Index ID to delete
            
        Returns:
            bool: True if deletion successful
        """
        try:
            self.client.indexes.delete(index_id)
            logger.info(f"Deleted index {index_id} from Twelve Labs")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete index {index_id}: {e}")
            return False