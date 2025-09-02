"""
Test real Apify TikTok scraper to analyze actual data structure.

This runs the actual scraper and shows real TikTok data.
"""

import os
import sys
import json
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_clients.apify.run_scraper import run_tiktok_scraper, get_scraper_status
from src.api_clients.apify.get_results import get_scraper_results, parse_video_data
from src.api_clients.apify.config_builder import create_custom_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_real_scraper_test():
    """Run real TikTok scraper with small dataset for testing."""
    logger.info("=== Running Real Apify TikTok Scraper ===")
    
    try:
        # Create a small test configuration
        test_config = create_custom_config(
            hashtags=["caredit"],  # Just one hashtag for testing
            days_back=2,           # Only 2 days to limit data
            results_per_page=3     # Only 3 results for testing
        )
        
        logger.info(f"Test configuration: {json.dumps(test_config, indent=2)}")
        
        # Start the scraper
        logger.info("Starting TikTok scraper...")
        run_id = run_tiktok_scraper()
        
        if not run_id:
            logger.error("❌ Failed to start scraper")
            return None
            
        logger.info(f"✅ Scraper started with run ID: {run_id}")
        
        # Monitor the scraper
        return monitor_scraper_progress(run_id)
        
    except Exception as e:
        logger.error(f"❌ Scraper test failed: {e}")
        return None


def monitor_scraper_progress(run_id):
    """Monitor scraper progress and get results when complete."""
    logger.info("=== Monitoring Scraper Progress ===")
    
    max_wait_time = 300  # 5 minutes max
    check_interval = 10  # Check every 10 seconds
    elapsed_time = 0
    
    while elapsed_time < max_wait_time:
        try:
            status = get_scraper_status(run_id)
            current_status = status.get("status")
            
            logger.info(f"⏳ Status: {current_status} (elapsed: {elapsed_time}s)")
            
            if current_status == "SUCCEEDED":
                logger.info("✅ Scraper completed successfully!")
                return get_and_analyze_results(run_id)
                
            elif current_status == "FAILED":
                logger.error("❌ Scraper failed")
                return None
                
            elif current_status in ["RUNNING", "READY"]:
                logger.info(f"🔄 Scraper still running...")
                
            time.sleep(check_interval)
            elapsed_time += check_interval
            
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            time.sleep(check_interval)
            elapsed_time += check_interval
    
    logger.warning("⏰ Timeout reached - scraper may still be running")
    return None


def get_and_analyze_results(run_id):
    """Get and analyze real scraper results."""
    logger.info("=== Getting Real Scraper Results ===")
    
    try:
        # Get raw results
        raw_results = get_scraper_results(run_id)
        
        if not raw_results:
            logger.warning("No results returned from scraper")
            return None
            
        logger.info(f"📊 Got {len(raw_results)} videos from scraper")
        
        # Analyze first few results
        analyze_real_data_structure(raw_results[:3])  # Analyze first 3 videos
        
        return raw_results
        
    except Exception as e:
        logger.error(f"❌ Failed to get results: {e}")
        return None


def analyze_real_data_structure(videos):
    """Analyze the structure of real TikTok data."""
    logger.info("=== Analyzing Real Data Structure ===")
    
    if not videos:
        logger.warning("No videos to analyze")
        return
    
    # Show first video's raw structure
    first_video = videos[0]
    logger.info("Raw video keys from Apify:")
    logger.info(f"Keys: {list(first_video.keys())}")
    
    # Show parsed structure
    parsed_video = parse_video_data(first_video)
    logger.info("Parsed video structure:")
    logger.info(f"Parsed keys: {list(parsed_video.keys())}")
    
    # Print detailed structure
    print("\n" + "="*60)
    print("REAL APIFY TIKTOK DATA STRUCTURE")
    print("="*60)
    print("\n1. RAW APIFY RESPONSE (first video):")
    print(json.dumps(first_video, indent=2))
    
    print("\n2. PARSED VIDEO DATA:")
    print(json.dumps(parsed_video, indent=2))
    
    print("\n3. FIELD ANALYSIS:")
    print("-" * 30)
    for key, value in parsed_video.items():
        value_type = type(value).__name__
        value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        print(f"  {key}: {value_type} = {value_preview}")
    
    print("\n4. DATABASE RECOMMENDATIONS:")
    print("-" * 30)
    db_recommendations = analyze_field_types(parsed_video)
    for field, db_type in db_recommendations.items():
        print(f"  {field}: {db_type}")


def analyze_field_types(data):
    """Analyze field types for database schema recommendations."""
    recommendations = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            if "url" in key or "http" in str(value):
                recommendations[key] = "TEXT (URL)"
            elif len(str(value)) > 255:
                recommendations[key] = "TEXT"
            else:
                recommendations[key] = "VARCHAR(500)"
        elif isinstance(value, int):
            recommendations[key] = "INTEGER"
        elif isinstance(value, (list, dict)):
            recommendations[key] = "JSON"
        elif key in ["created_time", "scraped_at"]:
            recommendations[key] = "TIMESTAMP"
        else:
            recommendations[key] = "TEXT"
    
    return recommendations


def main():
    """Main test function."""
    logger.info("=== Real Apify Scraper Test ===")
    
    # Check token
    if not os.environ.get("APIFY_TOKEN"):
        logger.error("❌ APIFY_TOKEN not found in environment variables")
        return
    
    logger.info("✅ APIFY_TOKEN found")
    
    # Run the test
    results = run_real_scraper_test()
    
    if results:
        logger.info("=== Test Completed Successfully ===")
        logger.info(f"✅ Got {len(results)} real TikTok videos")
        logger.info("✅ Data structure analyzed")
        logger.info("✅ Database schema recommendations generated")
    else:
        logger.warning("⚠️  Test completed but no results obtained")


if __name__ == "__main__":
    main()