#!/usr/bin/env python3
"""
End-to-End System Validation Test
Complete test of video ingestion + newsletter generation + database validation.

This will:
1. Scrape 2 videos per 10 users (~20 videos max)
2. Run complete newsletter generation  
3. Print all database results for validation
"""
import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/end_to_end_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def run_end_to_end_test():
    """Run complete end-to-end system test."""
    try:
        logger.info("🚀 STARTING END-TO-END SYSTEM VALIDATION")
        logger.info("=" * 70)
        logger.info("📱 Phase 1: Video Ingestion (2 videos × 10 users)")  
        logger.info("📰 Phase 2: Newsletter Generation")
        logger.info("🔍 Phase 3: Database Validation & Results")
        logger.info("=" * 70)
        
        test_start_time = datetime.now()
        
        # PHASE 1: Video Ingestion Pipeline
        logger.info("\n📱 PHASE 1: VIDEO INGESTION PIPELINE")
        logger.info("-" * 50)
        
        success = run_small_scale_video_ingestion()
        if not success:
            logger.error("❌ Video ingestion failed - aborting test")
            return False
        
        logger.info("✅ Video ingestion completed successfully")
        time.sleep(2)  # Brief pause between phases
        
        # PHASE 2: Newsletter Generation Pipeline  
        logger.info("\n📰 PHASE 2: NEWSLETTER GENERATION PIPELINE")
        logger.info("-" * 50)
        
        success = run_newsletter_generation()
        if not success:
            logger.error("❌ Newsletter generation failed")
            return False
            
        logger.info("✅ Newsletter generation completed successfully")
        time.sleep(1)
        
        # PHASE 3: Database Validation & Results
        logger.info("\n🔍 PHASE 3: DATABASE VALIDATION & RESULTS")
        logger.info("-" * 50)
        
        validation_results = print_complete_database_results()
        
        # Final Summary
        test_end_time = datetime.now()
        duration = (test_end_time - test_start_time).total_seconds()
        
        logger.info("\n🎯 END-TO-END TEST COMPLETE!")
        logger.info("=" * 70)
        logger.info(f"⏱️ Total test duration: {duration/60:.2f} minutes")
        logger.info(f"📊 Videos in database: {validation_results.get('total_videos', 0)}")
        logger.info(f"📰 Newsletters generated: {validation_results.get('total_newsletters', 0)}")
        logger.info(f"🏆 Champions found: {validation_results.get('total_champions', 0)}")
        logger.info(f"📈 Total database records: {validation_results.get('total_records', 0)}")
        
        if validation_results.get('total_records', 0) > 0:
            logger.info("🎉 END-TO-END VALIDATION: ✅ SUCCESS!")
            return True
        else:
            logger.error("💥 END-TO-END VALIDATION: ❌ FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"❌ End-to-end test failed: {e}", exc_info=True)
        return False


def run_small_scale_video_ingestion():
    """Run video ingestion with small scale limits."""
    try:
        # Import here to avoid import issues
        from src.schedulers.video_ingestion_pipeline import run_video_ingestion_pipeline
        
        logger.info("🔄 Starting small-scale video ingestion...")
        logger.info("   Target: ~20 videos (2 per user × 10 users)")
        
        # Run with limited scope
        success = run_video_ingestion_pipeline(max_videos=20)
        
        if success:
            logger.info("✅ Video ingestion pipeline completed")
        else:
            logger.error("❌ Video ingestion pipeline failed")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Error in video ingestion: {e}")
        return False


def run_newsletter_generation():
    """Run newsletter generation pipeline."""
    try:
        from src.schedulers.newsletter_pipeline import run_newsletter_pipeline
        
        logger.info("🔄 Starting newsletter generation...")
        
        success = run_newsletter_pipeline()
        
        if success:
            logger.info("✅ Newsletter generation pipeline completed")
        else:
            logger.error("❌ Newsletter generation pipeline failed")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Error in newsletter generation: {e}")
        return False


def print_complete_database_results():
    """Print complete database results for validation."""
    try:
        from supabase import create_client
        
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
        results = {}
        
        logger.info("🔍 COMPLETE DATABASE VALIDATION RESULTS")
        logger.info("=" * 60)
        
        # 1. Videos Table
        logger.info("\n📱 VIDEOS TABLE:")
        videos = supabase.table('videos').select('*').order('created_at', desc=True).execute()
        results['total_videos'] = len(videos.data)
        
        logger.info(f"   Total videos: {len(videos.data)}")
        for i, video in enumerate(videos.data[:5], 1):  # Show top 5
            logger.info(f"   {i}. @{video.get('author_username', 'unknown'):15} - {video.get('views', 0):8,} views - Status: {video.get('analysis_status', 'unknown')}")
        
        if len(videos.data) > 5:
            logger.info(f"   ... and {len(videos.data) - 5} more videos")
        
        # 2. Newsletters Table
        logger.info("\n📰 NEWSLETTERS TABLE:")
        newsletters = supabase.table('newsletters').select('*').order('created_at', desc=True).execute()
        results['total_newsletters'] = len(newsletters.data)
        
        if newsletters.data:
            nl = newsletters.data[0]  # Latest newsletter
            logger.info(f"   Newsletter ID: {nl['newsletter_id']}")
            logger.info(f"   Period: {nl['week_start_date']} to {nl['week_end_date']}")
            logger.info(f"   Videos tracked: {nl['total_videos_tracked']}")
            logger.info(f"   Total views: {nl['total_views']:,}")
            logger.info(f"   Total creators: {nl['total_creators']}")
            logger.info(f"   Avg engagement: {nl['avg_engagement_rate']:.2f}%")
            logger.info(f"   Viral videos: {nl['viral_videos_count']}")
            logger.info(f"   Top car brand: {nl['top_car_brand']} ({nl['top_car_brand_views']:,} views)")
            logger.info(f"   Top hook: {nl['top_hook_type']}")
        else:
            logger.warning("   No newsletters found!")
        
        # 3. Champions Table
        logger.info("\n🏆 CHAMPIONS TABLE:")
        champions = supabase.table('newsletter_champions').select('*').execute()
        results['total_champions'] = len(champions.data)
        
        logger.info(f"   Total champions: {len(champions.data)}")
        champion_categories = {}
        for champ in champions.data:
            category = champ['category']
            if category not in champion_categories:
                champion_categories[category] = []
            champion_categories[category].append(champ)
        
        for category, champs in champion_categories.items():
            logger.info(f"   {category}: {len(champs)} champions")
            for champ in champs[:2]:  # Show top 2 per category
                logger.info(f"      - {champ['element_name']} by @{champ['author_username']} ({champ['views']:,} views)")
        
        # 4. Rankings Table  
        logger.info("\n📊 RANKINGS TABLE:")
        rankings = supabase.table('newsletter_top_rankings').select('*').execute()
        results['total_rankings'] = len(rankings.data)
        
        ranking_categories = {}
        for rank in rankings.data:
            category = rank['category']
            if category not in ranking_categories:
                ranking_categories[category] = []
            ranking_categories[category].append(rank)
        
        logger.info(f"   Total rankings: {len(rankings.data)}")
        for category, ranks in ranking_categories.items():
            logger.info(f"   {category}: {len(ranks)} items")
            # Show top 3 in each category
            sorted_ranks = sorted(ranks, key=lambda x: x['rank_position'])[:3]
            for rank in sorted_ranks:
                logger.info(f"      #{rank['rank_position']}: {rank['element_name']} ({rank['avg_views']:,} avg views)")
        
        # 5. Recommendations Table
        logger.info("\n💡 RECOMMENDATIONS TABLE:")
        recommendations = supabase.table('newsletter_recommendations').select('*').execute()
        results['total_recommendations'] = len(recommendations.data)
        
        logger.info(f"   Total recommendations: {len(recommendations.data)}")
        rec_types = {}
        for rec in recommendations.data:
            rec_type = rec['recommendation_type']
            if rec_type not in rec_types:
                rec_types[rec_type] = 0
            rec_types[rec_type] += 1
        
        for rec_type, count in rec_types.items():
            logger.info(f"   {rec_type}: {count} recommendations")
        
        # Show sample recommendations
        for rec in recommendations.data[:3]:
            logger.info(f"      - {rec['recommendation_title'][:50]}... (Target: {rec['target_audience']})")
        
        # 6. Statistical Findings Table
        logger.info("\n📈 STATISTICAL FINDINGS TABLE:")
        findings = supabase.table('newsletter_statistical_findings').select('*').execute()
        results['total_statistical_findings'] = len(findings.data)
        
        logger.info(f"   Total findings: {len(findings.data)}")
        for finding in findings.data:
            logger.info(f"      - {finding['finding_type']}: {finding['variable_tested']}")
            logger.info(f"        P-value: {finding['p_value']:.6f}, Effect: {finding['effect_magnitude']}")
        
        # 7. Overall Summary
        total_records = (
            results['total_videos'] + 
            results['total_newsletters'] + 
            results['total_champions'] + 
            results['total_rankings'] + 
            results['total_recommendations'] + 
            results['total_statistical_findings']
        )
        results['total_records'] = total_records
        
        logger.info("\n📋 DATABASE SUMMARY:")
        logger.info(f"   Videos: {results['total_videos']}")
        logger.info(f"   Newsletters: {results['total_newsletters']}")  
        logger.info(f"   Champions: {results['total_champions']}")
        logger.info(f"   Rankings: {results['total_rankings']}")
        logger.info(f"   Recommendations: {results['total_recommendations']}")
        logger.info(f"   Statistical findings: {results['total_statistical_findings']}")
        logger.info(f"   TOTAL RECORDS: {total_records}")
        
        # 8. Data Quality Check
        logger.info("\n✅ DATA QUALITY VALIDATION:")
        if results['total_videos'] > 0:
            logger.info("   ✅ Videos table populated")
        else:
            logger.warning("   ⚠️ No videos found")
            
        if results['total_newsletters'] > 0:
            logger.info("   ✅ Newsletter generated")
        else:
            logger.warning("   ⚠️ No newsletter generated")
            
        if results['total_champions'] > 0:
            logger.info("   ✅ Champions selected")
        else:
            logger.warning("   ⚠️ No champions selected")
            
        if total_records > 20:
            logger.info("   ✅ Comprehensive data generated")
        else:
            logger.warning("   ⚠️ Limited data generated")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error printing database results: {e}")
        return {'total_records': 0}


if __name__ == "__main__":
    logger.info("End-to-End System Test Starting...")
    
    success = run_end_to_end_test()
    
    if success:
        logger.info("🎉 End-to-end validation completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 End-to-end validation failed!")
        sys.exit(1)