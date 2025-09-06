#!/usr/bin/env python3
"""
Test newsletter generation with existing database data only.
No video scraping or AI analysis - just newsletter pipeline.
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_newsletter_generation_only():
    """Test just the newsletter generation pipeline with existing database data."""
    logger.info("🧪 Testing Newsletter Generation with Existing Database Data")
    logger.info("=" * 60)
    
    try:
        # Import newsletter pipeline
        from src.schedulers.newsletter_pipeline import run_newsletter_pipeline
        
        # Run newsletter generation
        logger.info("🚀 Running newsletter generation pipeline...")
        success = run_newsletter_pipeline()
        
        if success:
            logger.info("✅ Newsletter generation successful!")
            
            # Check database results
            from src.database.client.supabase_client import get_supabase_client
            client = get_supabase_client()
            
            # Get latest newsletter
            newsletter_result = client.table('newsletters').select('*').order('created_at', desc=True).limit(1).execute()
            logger.info(f"📰 Latest newsletter: {len(newsletter_result.data)} record(s)")
            
            # Get champions
            champions_result = client.table('newsletter_champions').select('*').execute()
            logger.info(f"🏆 Champions: {len(champions_result.data)} record(s)")
            
            if len(champions_result.data) > 0:
                for champion in champions_result.data[:3]:
                    logger.info(f"   - {champion.get('category', 'Unknown')}: @{champion.get('author_username', 'Unknown')} ({champion.get('views', 0):,} views)")
            
            # Get statistical findings
            findings_result = client.table('newsletter_statistical_findings').select('*').execute()
            logger.info(f"📈 Statistical findings: {len(findings_result.data)} record(s)")
            
            if len(findings_result.data) > 0:
                for finding in findings_result.data[:3]:
                    logger.info(f"   - {finding.get('finding_type', 'Unknown')}: {finding.get('variable_tested', 'Unknown')} (effect: {finding.get('effect_size', 0):.3f})")
            
            return True
        else:
            logger.error("❌ Newsletter generation failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = test_newsletter_generation_only()
    
    if success:
        logger.info("🎉 Newsletter generation test PASSED!")
        sys.exit(0)
    else:
        logger.error("💥 Newsletter generation test FAILED!")
        sys.exit(1)