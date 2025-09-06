#!/usr/bin/env python3
"""
Production Newsletter Generation Pipeline
Single entry point for complete TikTok car edit newsletter generation.

Usage:
    python -m src.schedulers.newsletter_pipeline
    
This script will:
1. Extract video data from database
2. Run all analysis layers
3. Generate GPT insights
4. Create newsletter content
5. Insert into all newsletter database tables
"""
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/newsletter_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

load_dotenv()

def run_newsletter_pipeline():
    """Run the complete newsletter generation pipeline."""
    try:
        logger.info("🚀 Starting Newsletter Generation Pipeline")
        logger.info("=" * 60)
        
        # Import all required modules
        from src.newsletter.data.data_extractor import extract_past_7_days_videos
        from src.newsletter.data.engagement_calculator import (
            calculate_engagement_rate, calculate_performance_score, 
            calculate_viral_metrics, determine_viral_threshold, calculate_engagement_tiers
        )
        from src.newsletter.data.feature_processor import process_all_analysis_features
        
        # All analyzers
        from src.newsletter.analyzers.content.hook_analyzer import analyze_individual_hook_performance
        from src.newsletter.analyzers.content.transition_analyzer import analyze_individual_transition_performance
        from src.newsletter.analyzers.content.effects_analyzer import analyze_individual_effects_performance
        from src.newsletter.analyzers.vehicle.car_brand_analyzer import analyze_individual_brand_performance
        from src.newsletter.analyzers.vehicle.car_type_analyzer import analyze_car_type_performance
        from src.newsletter.analyzers.creator.creator_analyzer import analyze_creator_tier_performance
        from src.newsletter.analyzers.technical.specs_analyzer import analyze_duration_performance
        from src.newsletter.analyzers.technical.timing_analyzer import analyze_upload_hour_performance
        from src.newsletter.analyzers.technical.quality_analyzer import analyze_quality_score_performance
        from src.newsletter.analyzers.text.hashtag_analyzer import analyze_individual_hashtag_performance
        from src.newsletter.analyzers.text.description_analyzer import get_description_analysis_summary
        from src.newsletter.analyzers.text.music_analyzer import analyze_individual_music_performance
        
        # Statistics and intelligence
        from src.newsletter.statistics.correlation_validator import validate_performance_differences
        from src.newsletter.intelligence.gpt_insights import generate_all_gpt_insights_sync
        from src.newsletter.intelligence.pattern_analyzer import analyze_content_performance_patterns
        
        # Synthesis and selection
        from src.newsletter.synthesis.trend_synthesizer import synthesize_weekly_trends, generate_momentum_analysis
        from src.newsletter.synthesis.forecaster import forecast_viral_potential, predict_performance_trajectories
        from src.newsletter.selection.champion_selector import select_weekly_champions, select_trend_examples, select_statistical_proof_videos
        
        # Generation and database
        from src.newsletter.generation.content_generator import generate_database_newsletter_structure
        from src.database.client.supabase_client import get_supabase_client
        
        pipeline_start_time = datetime.now()
        
        # STEP 1: Data Extraction and Processing
        logger.info("📊 Step 1: Data Extraction and Processing")
        df = extract_past_7_days_videos()
        
        if df.empty:
            logger.error("❌ No video data available for processing")
            return False
            
        logger.info(f"✅ Extracted {len(df)} videos from database")
        
        # Calculate engagement metrics
        df = calculate_engagement_rate(df)
        df = calculate_performance_score(df)
        df = calculate_viral_metrics(df)
        df, viral_threshold = determine_viral_threshold(df)
        df = calculate_engagement_tiers(df)
        
        # Process analysis features
        df = process_all_analysis_features(df)
        logger.info(f"✅ Data processing complete: {len(df)} videos, {len(df.columns)} features")
        
        # STEP 2: Multi-Layer Analysis
        logger.info("\n🔍 Step 2: Running Multi-Layer Analysis")
        analyzer_results = {}
        
        # Content analyzers
        analyzer_results['hook_analysis'] = analyze_individual_hook_performance(df)
        analyzer_results['transition_analysis'] = analyze_individual_transition_performance(df)
        analyzer_results['effects_analysis'] = analyze_individual_effects_performance(df)
        
        # Vehicle analyzers
        analyzer_results['brand_analysis'] = analyze_individual_brand_performance(df)
        analyzer_results['car_type_analysis'] = analyze_car_type_performance(df)
        
        # Creator analyzers
        analyzer_results['creator_analysis'] = analyze_creator_tier_performance(df)
        
        # Technical analyzers
        analyzer_results['duration_analysis'] = analyze_duration_performance(df)
        analyzer_results['timing_analysis'] = analyze_upload_hour_performance(df)
        analyzer_results['quality_analysis'] = analyze_quality_score_performance(df)
        
        # Text analyzers
        analyzer_results['hashtag_analysis'] = analyze_individual_hashtag_performance(df)
        analyzer_results['description_analysis'] = get_description_analysis_summary(df)
        analyzer_results['music_analysis'] = analyze_individual_music_performance(df)
        
        logger.info(f"✅ Analysis complete: {len(analyzer_results)} analyzer categories")
        
        # STEP 3: Statistical Validation
        logger.info("\n📈 Step 3: Statistical Validation")
        statistical_results = validate_performance_differences(analyzer_results)
        significant_count = len(statistical_results.get('significant_differences', []))
        logger.info(f"✅ Statistical validation: {significant_count} significant findings")
        
        # STEP 4: GPT Intelligence Analysis
        logger.info("\n🤖 Step 4: GPT Intelligence Analysis")
        pattern_analysis = analyze_content_performance_patterns(analyzer_results, statistical_results)
        gpt_insights = generate_all_gpt_insights_sync(pattern_analysis, statistical_results, analyzer_results)
        insight_categories = len([k for k, v in gpt_insights.items() if v])
        logger.info(f"✅ GPT analysis: {insight_categories} insight categories generated")
        
        # STEP 5: Trend Synthesis and Forecasting
        logger.info("\n🔮 Step 5: Trend Synthesis and Forecasting")
        synthesis_results = synthesize_weekly_trends(analyzer_results, statistical_results)
        synthesis_results.update(generate_momentum_analysis(analyzer_results))
        
        # Forecasting
        forecasting_results = {}
        forecasting_results.update(forecast_viral_potential(df, synthesis_results))
        forecasting_results.update(predict_performance_trajectories(analyzer_results, statistical_results))
        
        logger.info(f"✅ Synthesis complete: {len(synthesis_results)} trend categories")
        
        # STEP 6: Champion Selection
        logger.info("\n🏆 Step 6: Champion Selection")
        champion_portfolio = select_weekly_champions(df, synthesis_results)
        trend_examples = select_trend_examples(df, gpt_insights)
        statistical_proof = select_statistical_proof_videos(df, statistical_results)
        
        # Combine all selection results
        champion_portfolio.update(trend_examples)
        champion_portfolio.update(statistical_proof)
        
        total_selections = sum(len(v) if isinstance(v, list) else 1 for v in champion_portfolio.values())
        logger.info(f"✅ Champion selection: {total_selections} selections")
        
        # STEP 7: Database-Ready Content Generation
        logger.info("\n📝 Step 7: Database Content Generation")
        all_analysis_results = {
            'analyzer_results': analyzer_results,
            'statistical_results': statistical_results,
            'gpt_insights': gpt_insights,
            'synthesis_results': synthesis_results,
            'forecasting_results': forecasting_results
        }
        
        newsletter_structure = generate_database_newsletter_structure(df, all_analysis_results, champion_portfolio)
        
        total_records = (
            1 + # newsletter_main
            len(newsletter_structure['newsletter_champions']) +
            len(newsletter_structure['newsletter_top_rankings']) + 
            len(newsletter_structure['newsletter_recommendations']) +
            len(newsletter_structure['newsletter_statistical_findings'])
        )
        logger.info(f"✅ Database structure generated: {total_records} records ready")
        
        # STEP 8: Database Insertion
        logger.info("\n💾 Step 8: Database Insertion")
        success_count = insert_newsletter_into_database(newsletter_structure)
        
        if success_count > 0:
            logger.info(f"✅ Database insertion successful: {success_count} records inserted")
        else:
            logger.error("❌ Database insertion failed")
            return False
        
        # STEP 9: Summary Report
        pipeline_end_time = datetime.now()
        duration = (pipeline_end_time - pipeline_start_time).total_seconds()
        
        logger.info("\n🎯 NEWSLETTER GENERATION COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"📊 Videos processed: {len(df)}")
        logger.info(f"🔍 Analyzers executed: {len(analyzer_results)}")
        logger.info(f"📈 Statistical tests: {significant_count}")
        logger.info(f"🤖 GPT insights: {insight_categories}")
        logger.info(f"🔮 Synthesis categories: {len(synthesis_results)}")
        logger.info(f"🏆 Champions selected: {total_selections}")
        logger.info(f"💾 Database records: {total_records}")
        logger.info(f"⏱️ Pipeline duration: {duration:.2f} seconds")
        logger.info(f"📅 Newsletter ID: {newsletter_structure['newsletter_main']['newsletter_id']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Newsletter pipeline failed: {e}", exc_info=True)
        return False


def insert_newsletter_into_database(newsletter_structure):
    """Insert newsletter structure into all database tables."""
    try:
        from src.database.client.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        success_count = 0
        
        # Insert main newsletter
        main_result = supabase.table('newsletters').insert(newsletter_structure['newsletter_main']).execute()
        if main_result.data:
            newsletter_id = main_result.data[0]['id']
            success_count += len(main_result.data)
            logger.info(f"✅ Newsletter inserted with ID: {newsletter_id}")
            
            # Insert champions with newsletter_id
            for champion in newsletter_structure['newsletter_champions']:
                champion['newsletter_id'] = newsletter_id
            
            if newsletter_structure['newsletter_champions']:
                champions_result = supabase.table('newsletter_champions').insert(newsletter_structure['newsletter_champions']).execute()
                success_count += len(champions_result.data) if champions_result.data else 0
            
            # Insert rankings with newsletter_id
            for ranking in newsletter_structure['newsletter_top_rankings']:
                ranking['newsletter_id'] = newsletter_id
                
            if newsletter_structure['newsletter_top_rankings']:
                rankings_result = supabase.table('newsletter_top_rankings').insert(newsletter_structure['newsletter_top_rankings']).execute()
                success_count += len(rankings_result.data) if rankings_result.data else 0
            
            # Insert recommendations with newsletter_id
            for rec in newsletter_structure['newsletter_recommendations']:
                rec['newsletter_id'] = newsletter_id
                
            if newsletter_structure['newsletter_recommendations']:
                recs_result = supabase.table('newsletter_recommendations').insert(newsletter_structure['newsletter_recommendations']).execute()
                success_count += len(recs_result.data) if recs_result.data else 0
            
            # Insert statistical findings with newsletter_id
            for finding in newsletter_structure['newsletter_statistical_findings']:
                finding['newsletter_id'] = newsletter_id
                
            if newsletter_structure['newsletter_statistical_findings']:
                findings_result = supabase.table('newsletter_statistical_findings').insert(newsletter_structure['newsletter_statistical_findings']).execute()
                success_count += len(findings_result.data) if findings_result.data else 0
                
        return success_count
        
    except Exception as e:
        logger.error(f"Database insertion failed: {e}")
        return 0


if __name__ == "__main__":
    logger.info("Newsletter Generation Pipeline Starting...")
    success = run_newsletter_pipeline()
    
    if success:
        logger.info("🎉 Newsletter generation completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Newsletter generation failed!")
        sys.exit(1)