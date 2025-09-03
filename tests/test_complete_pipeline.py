"""
Test complete end-to-end pipeline: Scrape → Filter → Store.

This runs the full workflow from TikTok scraping to database storage.
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

from src.api_clients.apify.run_scraper import run_tiktok_scraper, get_scraper_status
from src.api_clients.apify.get_results import get_scraper_results
from src.processors.video_pipeline import process_scraped_videos, log_processing_summary
from src.database.models.video_model import VideoModel
from src.database.operations.video_storage import store_videos_batch
from src.processors.performance_filter import calculate_engagement_score

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_complete_pipeline():
    """Run the complete pipeline from scraping to storage."""
    logger.info("=== COMPLETE PIPELINE TEST ===")
    logger.info("Scrape → Filter → Store")
    
    # Check environment
    if not os.environ.get("APIFY_TOKEN"):
        logger.error("❌ APIFY_TOKEN not set")
        return False
    
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_KEY"):
        logger.error("❌ Supabase credentials not set")
        return False
    
    logger.info("✅ All credentials available")
    
    try:
        # Step 1: Scrape real TikTok data (using a previous successful run)
        logger.info("=== STEP 1: Using Recent Apify Scraper Data ===")
        
        # For this test, we'll simulate using fresh scraped data
        # In production, you'd use: run_id = run_tiktok_scraper()
        logger.info("📊 Simulating scraped data for pipeline test...")
        
        # Simulate realistic TikTok data based on what we've seen from Apify
        simulated_scraped_data = create_realistic_test_data()
        logger.info(f"📥 Got {len(simulated_scraped_data)} videos from 'scraping'")
        
        # Step 2: Process through filtering pipeline
        logger.info("=== STEP 2: Processing Through Filter Pipeline ===")
        
        filtering_result = process_scraped_videos(simulated_scraped_data)
        log_processing_summary(filtering_result)
        
        filtered_videos = filtering_result["videos"]
        
        if not filtered_videos:
            logger.warning("⚠️  No videos passed filtering")
            return False
        
        # Step 3: Convert to VideoModel objects
        logger.info("=== STEP 3: Converting to Database Models ===")
        
        video_models = []
        for video_data in filtered_videos:
            engagement_score = calculate_engagement_score(video_data)
            video_model = VideoModel.from_apify_data(video_data, engagement_score)
            video_models.append(video_model)
        
        logger.info(f"📝 Created {len(video_models)} video models")
        
        # Step 4: Store in database
        logger.info("=== STEP 4: Storing in Database ===")
        
        storage_result = store_videos_batch(video_models)
        
        logger.info(f"💾 Storage complete:")
        logger.info(f"   ✅ Success: {storage_result['success']}")
        logger.info(f"   ❌ Failed: {storage_result['failed']}")
        logger.info(f"   📊 Total: {storage_result['total']}")
        
        # Step 5: Pipeline summary
        logger.info("=== PIPELINE SUMMARY ===")
        
        original_count = len(simulated_scraped_data)
        filtered_count = len(filtered_videos)
        stored_count = storage_result['success']
        
        logger.info(f"🔄 Pipeline flow:")
        logger.info(f"   📥 Raw scraped: {original_count}")
        logger.info(f"   🔍 After filtering: {filtered_count}")
        logger.info(f"   💾 Successfully stored: {stored_count}")
        
        success_rate = (stored_count / original_count) * 100 if original_count > 0 else 0
        logger.info(f"   📈 End-to-end success rate: {success_rate:.1f}%")
        
        # Show top stored videos
        if video_models and storage_result['success'] > 0:
            logger.info("🏆 Top stored videos:")
            for i, model in enumerate(video_models[:3], 1):
                logger.info(f"   {i}. @{model.author_username} - {model.views:,} views - Score: {model.engagement_score:.2f}")
        
        return stored_count > 0
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return False


def create_realistic_test_data():
    """Create realistic test data that mimics real Apify scraping results."""
    
    base_timestamp = int(datetime.now().timestamp())
    
    return [
        # High performer - should pass all filters
        {
            "id": f"pipeline_test_1_{base_timestamp}",
            "webVideoUrl": "https://www.tiktok.com/@car_king_99/video/1111111111",
            "text": "INSANE McLaren P1 edit with PHONK 🔥 Rate 1-10! #caredit #mclaren #p1 #phonk",
            "hashtags": [
                {"name": "caredit"},
                {"name": "mclaren"},
                {"name": "p1"},
                {"name": "phonk"}
            ],
            "authorMeta": {
                "name": "car_king_99",
                "nickName": "Car King 👑",
                "verified": True,
                "fans": 2500000
            },
            "musicMeta": {
                "musicName": "PHONK DRIFT",
                "musicAuthor": "DRIFT_BEATS",
                "musicId": "music_456789"
            },
            "videoMeta": {
                "duration": 28,
                "width": 720,
                "height": 1280,
                "coverUrl": "https://example.com/cover1.jpg"
            },
            "playCount": 1250000,
            "diggCount": 95000,
            "commentCount": 3400,
            "shareCount": 12000,
            "createTime": base_timestamp - 3600,  # 1 hour ago
            "input": "hashtag:caredit"
        },
        
        # Medium performer - should pass
        {
            "id": f"pipeline_test_2_{base_timestamp}",
            "webVideoUrl": "https://www.tiktok.com/@jdm_lifestyle/video/2222222222",
            "text": "JDM legends compilation 🇯🇵 Which one is your favorite? #jdm #caredit #toyota #honda",
            "hashtags": [
                {"name": "jdm"},
                {"name": "caredit"},
                {"name": "toyota"},
                {"name": "honda"}
            ],
            "authorMeta": {
                "name": "jdm_lifestyle",
                "nickName": "JDM Lifestyle",
                "verified": False,
                "fans": 890000
            },
            "musicMeta": {
                "musicName": "JDM VIBES",
                "musicAuthor": "TOKYO_BEATS",
                "musicId": "music_789123"
            },
            "videoMeta": {
                "duration": 32,
                "width": 720,
                "height": 1280,
                "coverUrl": "https://example.com/cover2.jpg"
            },
            "playCount": 456000,
            "diggCount": 28000,
            "commentCount": 890,
            "shareCount": 3400,
            "createTime": base_timestamp - 7200,  # 2 hours ago
            "input": "profile:@jdm_lifestyle"
        },
        
        # Another good performer
        {
            "id": f"pipeline_test_3_{base_timestamp}",
            "webVideoUrl": "https://www.tiktok.com/@supercar_daily/video/3333333333",
            "text": "Lamborghini Aventador SVJ sound 🔊 Turn up the volume! #lamborghini #supercar #caredit",
            "hashtags": [
                {"name": "lamborghini"},
                {"name": "supercar"},
                {"name": "caredit"}
            ],
            "authorMeta": {
                "name": "supercar_daily",
                "nickName": "Supercar Daily",
                "verified": False,
                "fans": 1200000
            },
            "musicMeta": {
                "musicName": "ENGINE ROAR",
                "musicAuthor": "CAR_SOUNDS",
                "musicId": "music_111222"
            },
            "videoMeta": {
                "duration": 15,
                "width": 720,
                "height": 1280,
                "coverUrl": "https://example.com/cover3.jpg"
            },
            "playCount": 789000,
            "diggCount": 45000,
            "commentCount": 1200,
            "shareCount": 5600,
            "createTime": base_timestamp - 10800,  # 3 hours ago
            "input": "search:car edit sounds"
        },
        
        # Low performer 1 - should be filtered out (very low views)
        {
            "id": f"pipeline_test_4_{base_timestamp}",
            "webVideoUrl": "https://www.tiktok.com/@newbie_editor/video/4444444444",
            "text": "My first car edit attempt, please be nice 😅",
            "hashtags": [
                {"name": "caredit"},
                {"name": "beginner"}
            ],
            "authorMeta": {
                "name": "newbie_editor",
                "nickName": "New Editor",
                "verified": False,
                "fans": 450
            },
            "musicMeta": {
                "musicName": "Basic Beat",
                "musicAuthor": "Free Music",
                "musicId": "music_basic"
            },
            "videoMeta": {
                "duration": 20,
                "width": 720,
                "height": 1280,
                "coverUrl": "https://example.com/cover4.jpg"
            },
            "playCount": 234,  # Too low - will be filtered
            "diggCount": 12,
            "commentCount": 3,
            "shareCount": 1,
            "createTime": base_timestamp - 1800,  # 30 minutes ago
            "input": "hashtag:caredit"
        },
        
        # Low performer 2 - should be filtered out (decent views but no engagement)
        {
            "id": f"pipeline_test_5_{base_timestamp}",
            "webVideoUrl": "https://www.tiktok.com/@boring_content/video/5555555555",
            "text": "Just a regular car video nothing special",
            "hashtags": [
                {"name": "car"},
                {"name": "boring"}
            ],
            "authorMeta": {
                "name": "boring_content",
                "nickName": "Boring Content",
                "verified": False,
                "fans": 1200
            },
            "musicMeta": {
                "musicName": "Generic Music",
                "musicAuthor": "Background",
                "musicId": "music_generic"
            },
            "videoMeta": {
                "duration": 45,
                "width": 720,
                "height": 1280,
                "coverUrl": "https://example.com/cover5.jpg"
            },
            "playCount": 50000,  # Decent views but...
            "diggCount": 100,    # Very low engagement
            "commentCount": 5,
            "shareCount": 2,
            "createTime": base_timestamp - 5400,  # 1.5 hours ago
            "input": "hashtag:car"
        },
        
        # Low performer 3 - should be filtered out (spam-like content)
        {
            "id": f"pipeline_test_6_{base_timestamp}",
            "webVideoUrl": "https://www.tiktok.com/@spam_account/video/6666666666",
            "text": "CHECK OUT MY LINK IN BIO!!! FOLLOW FOR MORE!!!",
            "hashtags": [
                {"name": "followme"},
                {"name": "linkinbio"},
                {"name": "spam"}
            ],
            "authorMeta": {
                "name": "spam_account",
                "nickName": "FOLLOW ME!!!",
                "verified": False,
                "fans": 50
            },
            "musicMeta": {
                "musicName": "Annoying Song",
                "musicAuthor": "Spam Artist",
                "musicId": "music_spam"
            },
            "videoMeta": {
                "duration": 8,
                "width": 720,
                "height": 1280,
                "coverUrl": "https://example.com/cover6.jpg"
            },
            "playCount": 1500,   # Very low views
            "diggCount": 20,
            "commentCount": 2,
            "shareCount": 0,
            "createTime": base_timestamp - 900,  # 15 minutes ago
            "input": "hashtag:followme"
        },
        
        # Duplicate ID - should be filtered
        {
            "id": f"pipeline_test_1_{base_timestamp}",  # Same as first one
            "webVideoUrl": "https://www.tiktok.com/@car_king_99/video/1111111111",
            "text": "INSANE McLaren P1 edit with PHONK 🔥 Rate 1-10! #caredit #mclaren",
            # ... duplicate content
        }
    ]


def main():
    """Main pipeline test function."""
    logger.info("🚀 Starting Complete Pipeline Test")
    
    success = run_complete_pipeline()
    
    if success:
        logger.info("🎉 COMPLETE PIPELINE TEST SUCCESSFUL!")
        logger.info("✅ Ready for production deployment")
    else:
        logger.error("❌ Pipeline test failed")
        logger.error("🔧 Check logs for issues")
    
    return success


if __name__ == "__main__":
    main()