"""
Test video filtering pipeline with real Apify data.

This runs the complete filtering pipeline on scraped TikTok videos.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_clients.apify.run_scraper import run_tiktok_scraper, get_scraper_status
from src.api_clients.apify.get_results import get_scraper_results
from src.processors.video_pipeline import process_scraped_videos, log_processing_summary

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_filtering_pipeline():
    """Test the complete video filtering pipeline with real data."""
    logger.info("=== Testing Video Filtering Pipeline ===")
    
    # For testing, let's use our previous scraper run results
    # In production, this would be a new scraper run
    
    logger.info("This test requires a recent scraper run ID.")
    logger.info("Run test_real_apify_scraper.py first to get data, then update this test.")
    
    # Simulate some test data with the structure we know from real scraping
    test_videos = create_test_video_data()
    
    logger.info(f"Testing with {len(test_videos)} simulated videos")
    
    # Process through pipeline
    result = process_scraped_videos(test_videos)
    
    # Log summary
    log_processing_summary(result)
    
    # Show sample results
    show_filtered_results(result)
    
    return result


def create_test_video_data():
    """Create test data that mimics real Apify structure."""
    return [
        # High-performing video
        {
            "id": "7545597742098173240",
            "text": "Epic car edit with sick beats #caredit #supercars",
            "webVideoUrl": "https://www.tiktok.com/@user1/video/7545597742098173240",
            "authorMeta": {"name": "user1", "verified": False},
            "playCount": 25000,
            "diggCount": 1500,
            "commentCount": 89,
            "shareCount": 45,
            "hashtags": [{"name": "caredit"}, {"name": "supercars"}]
        },
        # Duplicate of above (should be filtered)
        {
            "id": "7545597742098173240",
            "text": "Epic car edit with sick beats #caredit #supercars",
            "webVideoUrl": "https://www.tiktok.com/@user1/video/7545597742098173240",
            "authorMeta": {"name": "user1", "verified": False},
            "playCount": 25000,
            "diggCount": 1500,
            "commentCount": 89,
            "shareCount": 45
        },
        # Low-performing video (should be filtered)
        {
            "id": "7545597742098173241",
            "text": "My first car edit attempt",
            "webVideoUrl": "https://www.tiktok.com/@beginner/video/7545597742098173241",
            "authorMeta": {"name": "beginner", "verified": False},
            "playCount": 150,
            "diggCount": 5,
            "commentCount": 1,
            "shareCount": 0
        },
        # Invalid video (missing required fields)
        {
            "id": "",
            "text": "Invalid video with no ID"
        },
        # Another high performer
        {
            "id": "7545597742098173242",
            "text": "JDM car edit compilation 🔥 #jdm #caredit #viral",
            "webVideoUrl": "https://www.tiktok.com/@jdm_king/video/7545597742098173242",
            "authorMeta": {"name": "jdm_king", "verified": True},
            "playCount": 89000,
            "diggCount": 7800,
            "commentCount": 234,
            "shareCount": 156,
            "hashtags": [{"name": "jdm"}, {"name": "caredit"}, {"name": "viral"}]
        },
        # Similar content (should be filtered)
        {
            "id": "7545597742098173243",
            "text": "Epic car edit with sick beats #caredit #cars",
            "webVideoUrl": "https://www.tiktok.com/@copycat/video/7545597742098173243",
            "authorMeta": {"name": "copycat", "verified": False},
            "playCount": 5000,
            "diggCount": 200,
            "commentCount": 15,
            "shareCount": 8
        },
        # Medium performer
        {
            "id": "7545597742098173244",
            "text": "Lamborghini edit with phonk music 🏎️",
            "webVideoUrl": "https://www.tiktok.com/@lambo_edits/video/7545597742098173244",
            "authorMeta": {"name": "lambo_edits", "verified": False},
            "playCount": 12000,
            "diggCount": 890,
            "commentCount": 45,
            "shareCount": 23
        }
    ]


def show_filtered_results(result):
    """Show the filtered results in a readable format."""
    videos = result["videos"]
    
    print("\n" + "="*60)
    print("FILTERED VIDEO RESULTS")
    print("="*60)
    
    if not videos:
        print("No videos passed filtering!")
        return
    
    for i, video in enumerate(videos[:5], 1):  # Show top 5
        author = video.get("authorMeta", {}).get("name", "unknown")
        views = video.get("playCount", 0)
        likes = video.get("diggCount", 0)
        text = video.get("text", "")[:50] + "..." if len(video.get("text", "")) > 50 else video.get("text", "")
        
        print(f"\n{i}. @{author}")
        print(f"   Views: {views:,} | Likes: {likes:,}")
        print(f"   Text: {text}")
    
    print("\n" + "="*60)


def main():
    """Main test function."""
    if not os.environ.get("APIFY_TOKEN"):
        logger.warning("APIFY_TOKEN not set - using simulated data only")
    
    result = test_filtering_pipeline()
    
    logger.info("=== Filtering Pipeline Test Complete ===")
    return result


if __name__ == "__main__":
    main()