#!/usr/bin/env python3
"""
Main Pipeline Orchestrator - Complete Weekly Newsletter Automation
Coordinates video ingestion and newsletter generation pipelines.

This is the master pipeline that runs both:
1. Video Ingestion Pipeline (TikTok scraping → database storage)
2. Newsletter Generation Pipeline (data analysis → newsletter creation)
"""

import logging
from datetime import datetime
from src.utils.error_logger import log_newsletter_failure

logger = logging.getLogger(__name__)


def run_complete_weekly_pipeline() -> bool:
    """
    Run the complete weekly newsletter pipeline.
    
    Executes both video ingestion and newsletter generation in sequence.
    
    Returns:
        bool: True if both pipelines completed successfully, False otherwise
    """
    pipeline_start_time = datetime.utcnow()
    
    try:
        logger.info("🚀 STARTING COMPLETE WEEKLY NEWSLETTER PIPELINE")
        logger.info("=" * 70)
        logger.info(f"📅 Pipeline started at: {pipeline_start_time.isoformat()}")
        logger.info("📋 Pipeline sequence: Video Ingestion → Newsletter Generation")
        logger.info("=" * 70)
        
        # ========================================
        # STEP 1: VIDEO INGESTION PIPELINE
        # ========================================
        logger.info("")
        logger.info("📥 STEP 1: VIDEO INGESTION PIPELINE")
        logger.info("=" * 50)
        logger.info("🎯 Scraping TikTok videos and storing in database...")
        
        try:
            from src.schedulers.video_ingestion_pipeline import run_video_ingestion_pipeline
            
            ingestion_success = run_video_ingestion_pipeline()
            
            if not ingestion_success:
                logger.error("❌ Video ingestion pipeline failed")
                log_newsletter_failure("video_ingestion", "Video ingestion pipeline returned failure status")
                return False
                
            logger.info("✅ Video ingestion pipeline completed successfully")
            
        except ImportError as e:
            logger.error(f"❌ Video ingestion pipeline not available: {e}")
            log_newsletter_failure("ingestion_import", f"Cannot import video ingestion pipeline: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Video ingestion pipeline error: {e}")
            log_newsletter_failure("ingestion_exception", f"Unexpected error in video ingestion: {str(e)}")
            return False
        
        # ========================================
        # STEP 2: NEWSLETTER GENERATION PIPELINE  
        # ========================================
        logger.info("")
        logger.info("📰 STEP 2: NEWSLETTER GENERATION PIPELINE")
        logger.info("=" * 50)
        logger.info("🎯 Analyzing videos and generating newsletter...")
        
        try:
            from src.schedulers.newsletter_pipeline import run_newsletter_pipeline
            
            newsletter_success = run_newsletter_pipeline()
            
            if not newsletter_success:
                logger.error("❌ Newsletter generation pipeline failed")
                log_newsletter_failure("newsletter_generation", "Newsletter generation pipeline returned failure status")
                return False
                
            logger.info("✅ Newsletter generation pipeline completed successfully")
            
        except ImportError as e:
            logger.error(f"❌ Newsletter generation pipeline not available: {e}")
            log_newsletter_failure("newsletter_import", f"Cannot import newsletter generation pipeline: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Newsletter generation pipeline error: {e}")
            log_newsletter_failure("newsletter_exception", f"Unexpected error in newsletter generation: {str(e)}")
            return False
        
        # ========================================
        # PIPELINE COMPLETION
        # ========================================
        pipeline_end_time = datetime.utcnow()
        total_duration = (pipeline_end_time - pipeline_start_time).total_seconds()
        
        logger.info("")
        logger.info("🎉 COMPLETE WEEKLY NEWSLETTER PIPELINE FINISHED")
        logger.info("=" * 70)
        logger.info(f"📅 Pipeline completed at: {pipeline_end_time.isoformat()}")
        logger.info(f"⏱️ Total duration: {total_duration:.2f} seconds ({total_duration/60:.1f} minutes)")
        logger.info("✅ Both video ingestion and newsletter generation completed successfully")
        logger.info("📊 Newsletter data ready for website consumption")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        pipeline_end_time = datetime.utcnow()
        total_duration = (pipeline_end_time - pipeline_start_time).total_seconds()
        
        logger.error("")
        logger.error("❌ COMPLETE WEEKLY NEWSLETTER PIPELINE FAILED")
        logger.error("=" * 70)
        logger.error(f"📅 Pipeline failed at: {pipeline_end_time.isoformat()}")
        logger.error(f"⏱️ Duration before failure: {total_duration:.2f} seconds")
        logger.error(f"💥 Error: {e}")
        logger.error("=" * 70)
        
        return False


if __name__ == "__main__":
    """
    Direct execution for testing the complete pipeline.
    """
    print("🧪 Testing Complete Weekly Newsletter Pipeline")
    print("=" * 50)
    
    success = run_complete_weekly_pipeline()
    
    if success:
        print("✅ Pipeline test completed successfully!")
    else:
        print("❌ Pipeline test failed!")
        exit(1)