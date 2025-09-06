"""
Test the complete newsletter system with real video data and database insertion.
"""
import sys
import os
from dotenv import load_dotenv
import json

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Data pipeline
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
from src.newsletter.analyzers.text.music_analyzer import analyze_individual_music_performance
from src.newsletter.analyzers.text.description_analyzer import analyze_description_length_impact

# Statistics layer
from src.newsletter.statistics.correlation_validator import (
    validate_engagement_correlations, validate_feature_performance_correlations
)
from src.newsletter.statistics.significance_tester import (
    test_categorical_performance_differences, test_numerical_performance_differences
)

# Intelligence layer
from src.newsletter.intelligence.pattern_analyzer import (
    analyze_content_performance_patterns, analyze_creator_behavior_patterns
)
from src.newsletter.intelligence.gpt_insights import (
    generate_all_gpt_insights_sync
)

# Synthesis layer
from src.newsletter.synthesis.trend_synthesizer import (
    synthesize_weekly_trends, generate_momentum_analysis
)
from src.newsletter.synthesis.forecaster import (
    forecast_viral_potential, predict_performance_trajectories
)

# Selection layer
from src.newsletter.selection.champion_selector import (
    select_weekly_champions, select_trend_examples, select_statistical_proof_videos
)

# Generation layer
from src.newsletter.generation.content_generator import (
    generate_database_newsletter_structure, generate_typescript_interfaces, 
    get_database_content_generation_summary
)

# Database connection
from src.database.client.supabase_client import get_supabase_client


def test_complete_newsletter_system_with_database():
    """Test the complete newsletter system and insert results into database."""
    print("🧪 TESTING COMPLETE NEWSLETTER SYSTEM WITH DATABASE")
    print("="*70)
    
    try:
        # Step 1: Data Pipeline
        print("\n📊 Step 1: Data Pipeline")
        df = extract_past_7_days_videos()
        df = calculate_engagement_rate(df)
        df = calculate_performance_score(df)
        df = calculate_viral_metrics(df)
        df, viral_threshold = determine_viral_threshold(df)
        df = calculate_engagement_tiers(df)
        df = process_all_analysis_features(df)
        print(f"✅ Data processed: {len(df)} videos, {len(df.columns)} features")
        
        # Step 2: Run All Analyzers
        print("\n🔍 Step 2: Running All Analyzers")
        analyzer_results = {}
        
        # Content analyzers
        analyzer_results['hook_analysis'] = analyze_individual_hook_performance(df)
        analyzer_results['transition_analysis'] = analyze_individual_transition_performance(df)
        analyzer_results['effects_analysis'] = analyze_individual_effects_performance(df)
        print(f"✅ Content analyzers: {len(analyzer_results)} categories")
        
        # Vehicle analyzers
        analyzer_results['brand_analysis'] = analyze_individual_brand_performance(df)
        analyzer_results['car_type_analysis'] = analyze_car_type_performance(df)
        print(f"✅ Vehicle analyzers completed")
        
        # Creator analyzers
        analyzer_results['creator_analysis'] = analyze_creator_tier_performance(df)
        print(f"✅ Creator analyzers completed")
        
        # Technical analyzers
        analyzer_results['specs_analysis'] = analyze_duration_performance(df)
        analyzer_results['timing_analysis'] = analyze_upload_hour_performance(df)
        analyzer_results['quality_analysis'] = analyze_quality_score_performance(df)
        print(f"✅ Technical analyzers completed")
        
        # Text analyzers
        analyzer_results['hashtag_analysis'] = analyze_individual_hashtag_performance(df)
        analyzer_results['music_analysis'] = analyze_individual_music_performance(df)
        analyzer_results['description_analysis'] = analyze_description_length_impact(df)
        print(f"✅ Text analyzers: {len(analyzer_results)} total analyzers")
        
        # Step 3: Statistical Validation
        print("\n📈 Step 3: Statistical Validation")
        statistical_results = {}
        
        statistical_results['correlation_results'] = validate_engagement_correlations(df)
        statistical_results['feature_correlations'] = validate_feature_performance_correlations(df, analyzer_results)
        statistical_results['significance_results'] = test_categorical_performance_differences(df)
        statistical_results['numerical_tests'] = test_numerical_performance_differences(df, analyzer_results)
        print(f"✅ Statistical validation: {len(statistical_results['significance_results'].get('significant_tests', []))} significant findings")
        
        # Step 4: GPT Intelligence
        print("\n🤖 Step 4: GPT Intelligence Analysis")
        gpt_insights = {}
        
        # Pattern analysis first
        pattern_analysis = analyze_content_performance_patterns(analyzer_results, statistical_results)
        creator_patterns = analyze_creator_behavior_patterns(analyzer_results, statistical_results)
        
        # GPT insights - all generated concurrently
        gpt_insights = generate_all_gpt_insights_sync(pattern_analysis, statistical_results, analyzer_results)
        print(f"✅ GPT analysis: {len(gpt_insights)} insight categories generated concurrently")
        
        # Step 5: Synthesis Layer
        print("\n🔮 Step 5: Trend Synthesis")
        synthesis_results = {}
        
        synthesis_results.update(synthesize_weekly_trends(analyzer_results, statistical_results))
        synthesis_results['momentum_analysis'] = generate_momentum_analysis(analyzer_results)
        
        # Forecasting
        forecasting_results = {}
        forecasting_results.update(forecast_viral_potential(df, synthesis_results))
        forecasting_results.update(predict_performance_trajectories(analyzer_results, statistical_results))
        print(f"✅ Synthesis complete: {len(synthesis_results)} trend categories")
        
        # Step 6: Champion Selection
        print("\n🏆 Step 6: Champion Selection")
        champion_portfolio = select_weekly_champions(df, synthesis_results)
        trend_examples = select_trend_examples(df, gpt_insights)
        statistical_proof = select_statistical_proof_videos(df, statistical_results)
        
        # Combine all selection results
        champion_portfolio.update(trend_examples)
        champion_portfolio.update(statistical_proof)
        print(f"✅ Champion selection: {sum(len(v) if isinstance(v, list) else 1 for v in champion_portfolio.values())} selections")
        
        # Step 7: Database-Ready Content Generation
        print("\n📝 Step 7: Database Content Generation")
        all_analysis_results = {
            'analyzer_results': analyzer_results,
            'statistical_results': statistical_results,
            'gpt_insights': gpt_insights,
            'synthesis_results': synthesis_results,
            'forecasting_results': forecasting_results
        }
        
        newsletter_structure = generate_database_newsletter_structure(df, all_analysis_results, champion_portfolio)
        generation_summary = get_database_content_generation_summary(newsletter_structure)
        print(f"✅ Database structure generated: {generation_summary['total_database_records']} records ready")
        
        # Step 8: Insert into Database
        print("\n💾 Step 8: Database Insertion")
        success_count = insert_newsletter_into_database(newsletter_structure)
        print(f"✅ Database insertion: {success_count} records inserted successfully")
        
        # Step 9: Generate TypeScript Interfaces
        print("\n⚡ Step 9: TypeScript Interface Generation")
        typescript_interfaces = generate_typescript_interfaces()
        
        # Save TypeScript interfaces to file
        with open('newsletter_types.ts', 'w') as f:
            f.write(typescript_interfaces)
        print(f"✅ TypeScript interfaces saved to newsletter_types.ts")
        
        # Final Summary
        print(f"\n🎯 COMPLETE NEWSLETTER SYSTEM TEST RESULTS:")
        print(f"📊 Videos processed: {len(df)}")
        print(f"🔍 Analyzers run: {len(analyzer_results)}")
        print(f"📈 Statistical tests: {len(statistical_results['significance_results'].get('significant_tests', []))}")
        print(f"🤖 GPT insights: {len(gpt_insights)}")
        print(f"🔮 Synthesis categories: {len(synthesis_results)}")
        print(f"🏆 Champions selected: {sum(len(v) if isinstance(v, list) else 1 for v in champion_portfolio.values())}")
        print(f"💾 Database records: {generation_summary['total_database_records']}")
        print(f"⚡ System status: ✅ COMPLETE SUCCESS!")
        
        return newsletter_structure
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def insert_newsletter_into_database(newsletter_structure):
    """Insert newsletter structure into Supabase database."""
    try:
        supabase = get_supabase_client()
        success_count = 0
        
        # Insert main newsletter
        main_data = newsletter_structure['newsletter_main']
        result = supabase.table('newsletters').insert(main_data).execute()
        if result.data:
            newsletter_id = result.data[0]['id']
            success_count += 1
            print(f"✅ Newsletter inserted with ID: {newsletter_id}")
            
            # Insert champions
            for champion in newsletter_structure['newsletter_champions']:
                champion['newsletter_id'] = newsletter_id
            
            if newsletter_structure['newsletter_champions']:
                result = supabase.table('newsletter_champions').insert(newsletter_structure['newsletter_champions']).execute()
                success_count += len(result.data) if result.data else 0
            
            # Insert rankings
            for ranking in newsletter_structure['newsletter_top_rankings']:
                ranking['newsletter_id'] = newsletter_id
                
            if newsletter_structure['newsletter_top_rankings']:
                result = supabase.table('newsletter_top_rankings').insert(newsletter_structure['newsletter_top_rankings']).execute()
                success_count += len(result.data) if result.data else 0
            
            # Insert recommendations
            for rec in newsletter_structure['newsletter_recommendations']:
                rec['newsletter_id'] = newsletter_id
                
            if newsletter_structure['newsletter_recommendations']:
                result = supabase.table('newsletter_recommendations').insert(newsletter_structure['newsletter_recommendations']).execute()
                success_count += len(result.data) if result.data else 0
            
            # Insert statistical findings
            for finding in newsletter_structure['newsletter_statistical_findings']:
                finding['newsletter_id'] = newsletter_id
                
            if newsletter_structure['newsletter_statistical_findings']:
                result = supabase.table('newsletter_statistical_findings').insert(newsletter_structure['newsletter_statistical_findings']).execute()
                success_count += len(result.data) if result.data else 0
        
        return success_count
        
    except Exception as e:
        print(f"❌ Database insertion failed: {e}")
        return 0


def test_database_query():
    """Test querying the inserted newsletter data."""
    try:
        supabase = get_supabase_client()
        
        print("\n📊 Testing Database Queries:")
        
        # Get latest newsletter
        result = supabase.table('newsletters').select('*').order('created_at', desc=True).limit(1).execute()
        if result.data:
            newsletter = result.data[0]
            print(f"✅ Latest newsletter: {newsletter['newsletter_id']}")
            print(f"   - Total videos: {newsletter['total_videos_tracked']}")
            print(f"   - Total views: {newsletter['total_views']:,}")
            print(f"   - Top car brand: {newsletter['top_car_brand']}")
            print(f"   - Top hook: {newsletter['top_hook_type']}")
            
            newsletter_id = newsletter['id']
            
            # Get champions
            result = supabase.table('newsletter_champions').select('*').eq('newsletter_id', newsletter_id).execute()
            print(f"✅ Champions found: {len(result.data) if result.data else 0}")
            
            # Get rankings
            result = supabase.table('newsletter_top_rankings').select('*').eq('newsletter_id', newsletter_id).execute()
            print(f"✅ Rankings found: {len(result.data) if result.data else 0}")
            
            # Get recommendations
            result = supabase.table('newsletter_recommendations').select('*').eq('newsletter_id', newsletter_id).execute()
            print(f"✅ Recommendations found: {len(result.data) if result.data else 0}")
            
            print(f"🎯 Database query test: ✅ SUCCESS")
            
    except Exception as e:
        print(f"❌ Database query test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting Complete Newsletter System Test...")
    newsletter_data = test_complete_newsletter_system_with_database()
    
    if newsletter_data:
        print("\n🔍 Testing database queries...")
        test_database_query()
        
        print(f"\n🎉 Newsletter system test completed successfully!")
        print(f"📁 Check newsletter_types.ts for TypeScript interfaces")
        print(f"💾 Check your database for inserted newsletter data")
    else:
        print(f"\n❌ Newsletter system test failed!")