#!/usr/bin/env python3
"""
Production Video Ingestion Pipeline
Complete TikTok video scraping, AI analysis, and database storage pipeline.

Usage:
    python -m src.schedulers.video_ingestion_pipeline
    
This script will:
1. Scrape TikTok videos via Apify
2. Filter and validate video data  
3. Analyze videos with Twelve Labs AI
4. Store complete results in videos database table
"""
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/video_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

load_dotenv()


def run_video_ingestion_pipeline(max_videos: int = 50):
    """
    Run the complete video ingestion pipeline.
    
    Args:
        max_videos (int): Maximum number of videos to process (cost control)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("🚀 Starting Video Ingestion Pipeline")
        logger.info("=" * 60)
        logger.info(f"📊 Maximum videos to process: {max_videos}")
        
        # Import required modules
        from src.api_clients.apify.run_scraper import run_tiktok_scraper, get_scraper_status
        from src.api_clients.apify.get_results import get_scraper_results
        from src.processors.video_pipeline import process_scraped_videos
        from src.analyzers.video_content_analyzer import VideoContentAnalyzer
        from src.database.models.video_model import VideoModel
        from src.database.operations.video_storage import store_videos_batch
        
        pipeline_start_time = datetime.now()
        
        # Validate environment variables
        if not _validate_environment():
            return False
        
        # STEP 1: TikTok Video Scraping
        logger.info("\n📱 Step 1: TikTok Video Scraping")
        scraper_run_id = run_tiktok_scraper()
        
        if not scraper_run_id:
            logger.error("❌ Failed to start Apify scraper")
            return False
            
        logger.info(f"✅ Scraper started with run ID: {scraper_run_id}")
        
        # Wait for scraper to complete
        logger.info("⏳ Waiting for scraper to complete...")
        if not _wait_for_scraper_completion(scraper_run_id):
            logger.error("❌ Scraper failed or timed out")
            return False
        
        # STEP 2: Get Scraper Results
        logger.info("\n📥 Step 2: Retrieving Scraper Results")
        raw_videos = get_scraper_results(scraper_run_id)
        
        if not raw_videos:
            logger.error("❌ No videos returned from scraper")
            return False
            
        logger.info(f"✅ Retrieved {len(raw_videos)} raw videos from scraper")
        
        # STEP 3: Video Processing and Filtering
        logger.info("\n🔍 Step 3: Video Processing and Filtering")
        config = {
            'min_views': 1000,
            'min_engagement': 0.001,
            'max_duplicates': 0.8,
            'require_car_content': True,
            'max_videos': max_videos
        }
        
        processing_results = process_scraped_videos(raw_videos, config)
        filtered_videos = processing_results.get('videos', [])
        
        if not filtered_videos:
            logger.error("❌ No videos passed filtering criteria")
            return False
            
        logger.info(f"✅ Filtered to {len(filtered_videos)} quality videos")
        stats = processing_results.get('stats', {})
        logger.info(f"   - Removed duplicates: {stats.get('duplicates_removed', 0)}")
        logger.info(f"   - Removed low performance: {stats.get('performance_filtered', 0)}")
        logger.info(f"   - Validation failed: {stats.get('validation_failed', 0)}")
        
        # STEP 4: AI Analysis with Twelve Labs
        logger.info("\n🤖 Step 4: AI Analysis with Twelve Labs")
        analyzer = VideoContentAnalyzer()
        analyzed_videos = []
        
        for i, video in enumerate(filtered_videos, 1):
            try:
                logger.info(f"   Analyzing video {i}/{len(filtered_videos)}: {video.get('id', 'unknown')}")
                
                # Extract video download URL (not page URL)
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
                
                if not download_url:
                    logger.warning(f"   ⚠️ Video {i} missing video download URL, skipping analysis")
                    video['analysis_status'] = 'no_download_url'
                    continue
                
                logger.info(f"   Using download URL: {download_url}")
                
                analysis_result = analyzer.analyze_video_content(
                    video_url=download_url
                )
                
                if analysis_result:
                    video['analysis_results'] = analysis_result
                    video['analysis_status'] = 'completed'
                    analyzed_videos.append(video)
                    logger.info(f"   ✅ Analysis complete for video {i}")
                else:
                    video['analysis_status'] = 'failed'
                    logger.warning(f"   ⚠️ Analysis failed for video {i}")
                
                # Add delay to avoid rate limits
                if i < len(filtered_videos):
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"   ❌ Error analyzing video {i}: {e}")
                video['analysis_status'] = 'error'
                continue
        
        logger.info(f"✅ AI Analysis complete: {len(analyzed_videos)} videos analyzed successfully")
        
        # STEP 5: Convert to Database Models
        logger.info("\n📦 Step 5: Converting to Database Models")
        video_models = []
        
        for video_data in analyzed_videos:
            try:
                from src.processors.performance_filter import calculate_engagement_score
                engagement_score = calculate_engagement_score(video_data)
                video_model = VideoModel.from_apify_data(video_data, engagement_score)
                
                # Add the AI analysis results to the video model
                if video_data.get('analysis_results'):
                    video_model.update_analysis_results(video_data['analysis_results'])
                    logger.info(f"   📊 Added analysis results for @{video_model.author_username}")
                else:
                    logger.warning(f"   ⚠️ No analysis results found for @{video_model.author_username}")
                
                video_models.append(video_model)
            except Exception as e:
                logger.error(f"   ❌ Error converting video to model: {e}")
                continue
        
        logger.info(f"✅ Created {len(video_models)} video database models")
        
        # STEP 6: Database Storage
        logger.info("\n💾 Step 6: Database Storage")
        storage_results = store_videos_batch(video_models)
        
        if storage_results.get('success', 0) > 0:
            logger.info(f"✅ Database storage successful: {storage_results['success']} videos stored")
            logger.info(f"   - Success: {storage_results.get('success', 0)}")
            logger.info(f"   - Failed: {storage_results.get('failed', 0)}")
            logger.info(f"   - Total: {storage_results.get('total', 0)}")
        else:
            logger.error("❌ Database storage failed")
            return False
        
        # STEP 7: Pipeline Summary
        pipeline_end_time = datetime.now()
        duration = (pipeline_end_time - pipeline_start_time).total_seconds()
        
        logger.info("\n🎯 VIDEO INGESTION PIPELINE COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"📱 Videos scraped: {len(raw_videos)}")
        logger.info(f"🔍 Videos filtered: {len(filtered_videos)}")
        logger.info(f"🤖 Videos analyzed: {len(analyzed_videos)}")
        logger.info(f"💾 Videos stored: {storage_results.get('success', 0)}")
        logger.info(f"⏱️ Total pipeline duration: {duration/60:.2f} minutes")
        logger.info(f"💰 Estimated Twelve Labs cost: ${len(analyzed_videos) * 0.05:.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Video ingestion pipeline failed: {e}", exc_info=True)
        return False


def _validate_environment():
    """Validate all required environment variables are present."""
    required_vars = ["APIFY_TOKEN", "TWELVE_LABS_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All required environment variables present")
    return True


def _wait_for_scraper_completion(run_id: str, max_wait_minutes: int = 10):
    """
    Wait for Apify scraper to complete.
    
    Args:
        run_id (str): Apify run ID
        max_wait_minutes (int): Maximum time to wait
        
    Returns:
        bool: True if completed successfully, False if failed/timeout
    """
    from src.api_clients.apify.run_scraper import get_scraper_status
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while time.time() - start_time < max_wait_seconds:
        try:
            status = get_scraper_status(run_id)
            
            if status == "SUCCEEDED":
                logger.info("✅ Scraper completed successfully")
                return True
            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                logger.error(f"❌ Scraper failed with status: {status}")
                return False
            elif status in ["RUNNING", "READY"]:
                logger.info(f"   Status: {status} - waiting...")
                time.sleep(30)  # Check every 30 seconds
            else:
                logger.warning(f"   Unknown status: {status} - continuing to wait...")
                time.sleep(30)
                
        except Exception as e:
            logger.error(f"Error checking scraper status: {e}")
            time.sleep(30)
    
    logger.error(f"❌ Scraper timed out after {max_wait_minutes} minutes")
    return False


def run_quick_test_ingestion():
    """Run a quick test with just 5 videos."""
    logger.info("🧪 Running quick test ingestion (5 videos max)")
    return run_video_ingestion_pipeline(max_videos=5)


def run_production_ingestion():
    """Run production ingestion with default limits."""
    logger.info("🏭 Running production ingestion (50 videos max)")
    return run_video_ingestion_pipeline(max_videos=50)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Ingestion Pipeline")
    parser.add_argument("--test", action="store_true", help="Run quick test with 5 videos")
    parser.add_argument("--max-videos", type=int, default=50, help="Maximum videos to process")
    
    args = parser.parse_args()
    
    if args.test:
        success = run_quick_test_ingestion()
    else:
        success = run_video_ingestion_pipeline(max_videos=args.max_videos)
    
    if success:
        logger.info("🎉 Video ingestion completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Video ingestion failed!")
        sys.exit(1)