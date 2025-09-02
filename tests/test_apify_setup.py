"""
Test Apify setup and configuration without API calls.

This tests our Apify client setup and shows expected data structure.
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

from src.api_clients.apify.test_apify import test_config_creation, simulate_scraper_response, analyze_data_structure

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test Apify setup and show expected data structure."""
    logger.info("=== Testing Apify Setup ===")
    
    # Check if APIFY_TOKEN is set
    apify_token = os.environ.get("APIFY_TOKEN")
    if apify_token:
        logger.info("✅ APIFY_TOKEN is set")
        logger.info(f"Token preview: {apify_token[:10]}...")
    else:
        logger.warning("⚠️  APIFY_TOKEN not set - will simulate responses")
    
    try:
        # Test configuration creation
        config = test_config_creation()
        
        # Simulate API response to see data structure
        sample_data = simulate_scraper_response()
        
        # Analyze what database structure we'll need
        db_structure = analyze_data_structure(sample_data)
        
        logger.info("\n=== Summary ===")
        logger.info("✅ Apify client setup working")
        logger.info("✅ Configuration system working")
        logger.info("✅ Data parsing system ready")
        logger.info("✅ Database structure analyzed")
        
        print("\n" + "="*50)
        print("EXPECTED APIFY RESPONSE STRUCTURE:")
        print("="*50)
        print(json.dumps(sample_data, indent=2))
        
        print("\n" + "="*50)
        print("RECOMMENDED DATABASE FIELDS:")
        print("="*50)
        for field, db_type in db_structure.items():
            print(f"  {field}: {db_type}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()