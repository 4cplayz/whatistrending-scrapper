"""
Real-world test of Twelve Labs video analysis with actual Apify data.

Tests the complete flow: Apify scraping → filtering → Twelve Labs analysis → storage.
Limited to 10 videos max to control costs.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_clients.apify.run_scraper import run_tiktok_scraper, get_scraper_status
from src.api_clients.apify.get_results import get_scraper_results
from src.processors.video_pipeline import process_scraped_videos
from src.analyzers.video_content_analyzer import VideoContentAnalyzer
from src.database.models.video_model import VideoModel
from src.database.operations.video_storage import store_videos_batch

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_real_analysis_pipeline():
    """
    Test complete analysis pipeline with real Apify data and Twelve Labs.
    Limited to max 10 videos to control costs.
    """
    logger.info("=== REAL TWELVE LABS ANALYSIS TEST ===")
    logger.info("Apify → Filter → Twelve Labs → Store")
    
    # Check environment
    required_vars = ["APIFY_TOKEN", "TWELVE_LABS_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All credentials available")
    
    try:
        # Step 1: Run small Apify scrape (limited results)
        logger.info("=== STEP 1: Running Small Apify Scrape ===")
        
        # COMPLETE OVERRIDE - explicitly clear ALL sources from base config
        scrape_config = {
            # Clear all base config sources
            "hashtags": ["caredit"],               # Only 1 hashtag  
            "profiles": [],                        # OVERRIDE: empty profiles array
            "searchQueries": [],                   # OVERRIDE: empty search queries
            "resultsPerPage": 1,                   # Only 1 video per source
            "maxProfilesPerQuery": 1,              # Minimum required by API
            
            # Other settings
            "excludePinnedPosts": True,
            "oldestPostDateUnified": "7 days",
            "profileScrapeSections": ["videos"],
            "profileSorting": "latest",
            "proxyCountryCode": "None",
            "scrapeRelatedVideos": False,
            
            # Minimal downloads
            "shouldDownloadAvatars": False,
            "shouldDownloadCovers": False,         # Don't need covers for analysis
            "shouldDownloadMusicCovers": False,
            "shouldDownloadSlideshowImages": False,
            "shouldDownloadSubtitles": False,
            "shouldDownloadVideos": True           # CRITICAL: Need actual video file URLs for Twelve Labs
        }
        
        logger.info("🚀 Starting Apify scraper with limited config...")
        run_id = run_tiktok_scraper(custom_config=scrape_config)
        logger.info(f"📋 Scraper run ID: {run_id}")
        
        # Wait for completion
        logger.info("⏳ Waiting for Apify scraper to complete...")
        final_status = get_scraper_status(run_id, wait_for_completion=True)
        
        if final_status != "SUCCEEDED":
            logger.error(f"❌ Apify scraper failed with status: {final_status}")
            return False
        
        # Get results
        scraped_data = get_scraper_results(run_id)
        logger.info(f"📥 Got {len(scraped_data)} raw videos from Apify")
        
        if not scraped_data:
            logger.error("❌ No videos returned from Apify")
            return False
        
        # Step 2: Filter videos
        logger.info("=== STEP 2: Filtering Videos ===")
        
        filtering_result = process_scraped_videos(scraped_data)
        filtered_videos = filtering_result["videos"]
        
        logger.info(f"🔍 Filtering: {len(scraped_data)} → {len(filtered_videos)} videos")
        
        if not filtered_videos:
            logger.error("❌ No videos passed filtering")
            return False
        
        # Limit to max 3 videos for Twelve Labs analysis (cost control)
        analysis_videos = filtered_videos[:3]
        logger.info(f"💰 Limiting to {len(analysis_videos)} videos for Twelve Labs analysis")
        
        # Step 3: Twelve Labs Analysis
        logger.info("=== STEP 3: Twelve Labs Video Analysis ===")
        
        analyzer = VideoContentAnalyzer(index_name=f"test_analysis_{int(datetime.now().timestamp())}")
        
        # Extract actual video download URLs for Twelve Labs analysis
        video_download_urls = []
        for video in analysis_videos:
            # Check for video download URL in mediaUrls field
            media_urls = video.get("mediaUrls", {})
            download_url = None
            
            # Try different possible video URL fields
            if isinstance(media_urls, dict) and "video" in media_urls:
                download_url = media_urls["video"]
            elif isinstance(media_urls, list) and media_urls:
                # If it's a list, take the first video URL
                for url_entry in media_urls:
                    if isinstance(url_entry, dict) and "video" in url_entry:
                        download_url = url_entry["video"]
                        break
                    elif isinstance(url_entry, str):
                        download_url = url_entry
                        break
            
            if download_url:
                video_download_urls.append(download_url)
                logger.info(f"Found download URL: {download_url}")
                logger.info(f"TikTok page URL: {video.get('webVideoUrl', 'N/A')}")
            else:
                logger.warning(f"Video {video.get('id', 'unknown')} missing video download URL")
                logger.info(f"mediaUrls structure: {media_urls}")
                logger.info(f"Available keys: {list(video.keys())}")
        
        if not video_download_urls:
            logger.error("❌ No valid download URLs for analysis")
            return False
        
        logger.info(f"🧠 Analyzing {len(video_download_urls)} videos with Twelve Labs...")
        
        # Perform batch analysis using download URLs
        analysis_results = analyzer.analyze_videos_batch(video_download_urls, max_retries=2)
        
        logger.info(f"✅ Analysis complete: {len(analysis_results)} successful")
        
        # Step 4: Create VideoModels with analysis data
        logger.info("=== STEP 4: Creating Enhanced Video Models ===")
        
        enhanced_videos = []
        
        for i, video_data in enumerate(analysis_videos):
            if i < len(analysis_results):
                # Get corresponding analysis result
                analysis = analysis_results[i]
                
                # Create video model
                from src.processors.performance_filter import calculate_engagement_score
                engagement_score = calculate_engagement_score(video_data)
                video_model = VideoModel.from_apify_data(video_data, engagement_score)
                
                # Add analysis results
                video_model.update_analysis_results(analysis)
                
                enhanced_videos.append(video_model)
                
                # Log analysis insights
                logger.info(f"📊 Video @{video_model.author_username}:")
                if analysis.get("car_analysis", {}).get("car_brands"):
                    logger.info(f"   🚗 Cars: {analysis['car_analysis']['car_brands']}")
                if analysis.get("hook_analysis", {}).get("hooks"):
                    logger.info(f"   🎣 Hooks: {analysis['hook_analysis']['hooks']}")
                if analysis.get("transition_analysis", {}).get("transitions"):
                    logger.info(f"   ✨ Transitions: {analysis['transition_analysis']['transitions']}")
        
        # Step 5: Store enhanced videos
        logger.info("=== STEP 5: Storing Enhanced Videos ===")
        
        if enhanced_videos:
            storage_result = store_videos_batch(enhanced_videos)
            
            logger.info(f"💾 Storage results:")
            logger.info(f"   ✅ Stored: {storage_result['success']}")
            logger.info(f"   ❌ Failed: {storage_result['failed']}")
            
            # Step 6: Verify analysis data in database
            logger.info("=== STEP 6: Verifying Analysis Data ===")
            
            from src.database.client.supabase_client import get_supabase_client
            client = get_supabase_client()
            
            # Get recently stored videos with analysis
            recent_videos = client.table('videos').select('*').not_.is_('analysis_results', 'null').order('processed_at', desc=True).limit(5).execute()
            
            logger.info(f"📋 Found {len(recent_videos.data)} videos with analysis data:")
            
            for video in recent_videos.data:
                analysis = video.get('analysis_results', {})
                logger.info(f"   @{video['author_username']} - {video['views']:,} views")
                
                # Show car analysis
                car_analysis = analysis.get('car_analysis', {})
                if car_analysis.get('car_brands'):
                    logger.info(f"     🚗 Brands: {car_analysis['car_brands']}")
                if car_analysis.get('car_types'):
                    logger.info(f"     🏎️  Types: {car_analysis['car_types']}")
                
                # Show hooks
                hook_analysis = analysis.get('hook_analysis', {})
                if hook_analysis.get('hooks'):
                    logger.info(f"     🎣 Hooks: {hook_analysis['hooks']}")
                
                # Show transitions
                transition_analysis = analysis.get('transition_analysis', {})
                if transition_analysis.get('style'):
                    logger.info(f"     ✨ Style: {transition_analysis['style']}")
        
        # Final summary
        logger.info("=== FINAL SUMMARY ===")
        logger.info(f"📊 Pipeline Results:")
        logger.info(f"   📥 Scraped: {len(scraped_data)} videos")
        logger.info(f"   🔍 Filtered: {len(filtered_videos)} videos") 
        logger.info(f"   🧠 Analyzed: {len(analysis_results)} videos")
        logger.info(f"   💾 Stored: {storage_result['success'] if 'storage_result' in locals() else 0} videos")
        
        success = len(analysis_results) > 0 and ('storage_result' in locals() and storage_result['success'] > 0)
        
        if success:
            logger.info("🎉 REAL ANALYSIS TEST SUCCESSFUL!")
            logger.info("✅ Complete pipeline working: Apify → Filter → Twelve Labs → Database")
        else:
            logger.error("❌ Analysis test failed")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Main test function."""
    logger.info("🚀 Starting Real Twelve Labs Analysis Test")
    logger.info("⚠️  This will use real Twelve Labs API credits")
    
    success = test_real_analysis_pipeline()
    
    if success:
        logger.info("🎉 TEST PASSED - Ready for production!")
    else:
        logger.error("❌ TEST FAILED - Check logs for issues")
    
    return success


if __name__ == "__main__":
    main()