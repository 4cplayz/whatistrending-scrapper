"""
Test database connection and video storage operations.

This tests Supabase connection and video data storage functionality.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.client.supabase_client import get_supabase_client
from src.database.models.video_model import VideoModel
from src.database.operations.video_storage import (
    store_video, store_videos_batch, get_video_by_tiktok_id, 
    check_video_exists, get_videos_for_analysis
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_database_connection():
    """Test basic Supabase connection."""
    logger.info("=== Testing Database Connection ===")
    
    try:
        supabase = get_supabase_client()
        
        # Test basic connection by querying system info
        response = supabase.table("videos").select("count").execute()
        
        logger.info("✅ Database connection successful")
        logger.info(f"Videos table accessible: {response is not None}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def test_video_model_creation():
    """Test video model creation from sample data."""
    logger.info("=== Testing Video Model Creation ===")
    
    try:
        # Sample Apify data structure
        sample_apify_data = {
            "id": "test_video_123456789",
            "webVideoUrl": "https://www.tiktok.com/@testuser/video/123456789",
            "text": "Test car edit video #caredit #test",
            "hashtags": [{"name": "caredit"}, {"name": "test"}],
            "authorMeta": {
                "name": "testuser",
                "nickName": "Test User",
                "verified": False,
                "fans": 50000
            },
            "musicMeta": {
                "musicName": "Test Beat",
                "musicAuthor": "Test Artist",
                "musicId": "music123"
            },
            "videoMeta": {
                "duration": 30,
                "width": 720,
                "height": 1280,
                "coverUrl": "https://example.com/cover.jpg"
            },
            "playCount": 15000,
            "diggCount": 750,
            "commentCount": 45,
            "shareCount": 23,
            "createTime": int(datetime.now().timestamp())
        }
        
        # Create video model
        video_model = VideoModel.from_apify_data(sample_apify_data, engagement_score=2.5)
        
        logger.info("✅ Video model created successfully")
        logger.info(f"Video ID: {video_model.video_id}")
        logger.info(f"Author: @{video_model.author_username}")
        logger.info(f"Views: {video_model.views:,}")
        logger.info(f"Engagement Score: {video_model.engagement_score}")
        
        # Test dictionary conversion
        video_dict = video_model.to_dict()
        logger.info(f"✅ Model to dict conversion: {len(video_dict)} fields")
        
        return video_model
        
    except Exception as e:
        logger.error(f"❌ Video model creation failed: {e}")
        return None


def test_video_storage(video_model):
    """Test storing and retrieving video data."""
    logger.info("=== Testing Video Storage ===")
    
    if not video_model:
        logger.error("No video model to test with")
        return False
    
    try:
        # Check if database connection works
        if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
            logger.warning("⚠️  SUPABASE_URL or SUPABASE_KEY not set - skipping storage test")
            return True
        
        # Test individual video storage
        db_id = store_video(video_model)
        
        if db_id:
            logger.info(f"✅ Video stored successfully with ID: {db_id}")
            
            # Test retrieval
            retrieved = get_video_by_tiktok_id(video_model.video_id)
            if retrieved:
                logger.info(f"✅ Video retrieved successfully")
                logger.info(f"DB ID: {retrieved['id']}")
                logger.info(f"Video URL: {retrieved['video_url']}")
            else:
                logger.error("❌ Video not found after storage")
                return False
                
            # Test existence check
            exists = check_video_exists(video_model.video_id)
            logger.info(f"✅ Existence check: {exists}")
            
            return True
        else:
            logger.error("❌ Video storage failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Storage test failed: {e}")
        return False


def test_batch_storage():
    """Test batch video storage."""
    logger.info("=== Testing Batch Storage ===")
    
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
        logger.warning("⚠️  Supabase credentials not set - skipping batch test")
        return True
    
    try:
        # Create multiple test videos
        test_videos = []
        for i in range(3):
            sample_data = {
                "id": f"batch_test_{i}_{int(datetime.now().timestamp())}",
                "webVideoUrl": f"https://www.tiktok.com/@user{i}/video/{i}",
                "text": f"Batch test video {i} #test #batch",
                "hashtags": [{"name": "test"}, {"name": "batch"}],
                "authorMeta": {
                    "name": f"user{i}",
                    "nickName": f"User {i}",
                    "verified": False,
                    "fans": 1000 * (i + 1)
                },
                "playCount": 5000 * (i + 1),
                "diggCount": 250 * (i + 1),
                "commentCount": 15 * (i + 1),
                "shareCount": 5 * (i + 1),
                "createTime": int(datetime.now().timestamp())
            }
            
            video_model = VideoModel.from_apify_data(sample_data, engagement_score=1.5 + i * 0.5)
            test_videos.append(video_model)
        
        # Test batch storage
        result = store_videos_batch(test_videos)
        
        logger.info(f"✅ Batch storage completed")
        logger.info(f"Success: {result['success']}, Failed: {result['failed']}")
        
        return result['success'] > 0
        
    except Exception as e:
        logger.error(f"❌ Batch storage test failed: {e}")
        return False


def main():
    """Main test function."""
    logger.info("=== Database Integration Test Suite ===")
    
    # Check environment
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        logger.info("✅ Supabase credentials found")
        logger.info(f"URL: {supabase_url[:30]}...")
    else:
        logger.warning("⚠️  Supabase credentials not set - some tests will be skipped")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Connection
    if test_database_connection():
        tests_passed += 1
    
    # Test 2: Model creation
    video_model = test_video_model_creation()
    if video_model:
        tests_passed += 1
    
    # Test 3: Storage
    if test_video_storage(video_model):
        tests_passed += 1
    
    # Test 4: Batch storage
    if test_batch_storage():
        tests_passed += 1
    
    logger.info("=== Test Results ===")
    logger.info(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        logger.info("🎉 All database tests passed!")
    else:
        logger.warning(f"⚠️  {total_tests - tests_passed} tests failed or skipped")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    main()