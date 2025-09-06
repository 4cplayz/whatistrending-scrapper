"""
Test the new modular data pipeline.
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.newsletter.data.data_extractor import (
    extract_past_7_days_videos, 
    validate_extracted_data,
    get_data_quality_summary
)
from src.newsletter.data.engagement_calculator import (
    calculate_engagement_rate,
    calculate_performance_score, 
    calculate_viral_metrics,
    determine_viral_threshold,
    calculate_engagement_tiers,
    get_engagement_summary
)
from src.newsletter.data.feature_processor import (
    process_all_analysis_features,
    get_feature_summary
)

def test_complete_data_pipeline():
    """Test the complete new data pipeline."""
    print("🧪 TESTING NEW MODULAR DATA PIPELINE")
    print("="*50)
    
    # Step 1: Extract data
    print("\n📊 Step 1: Data Extraction")
    df = extract_past_7_days_videos()
    
    if not validate_extracted_data(df):
        print("❌ Data validation failed")
        return
    
    quality_summary = get_data_quality_summary(df)
    print(f"✅ Data quality: {quality_summary}")
    
    # Step 2: Calculate engagement metrics
    print("\n📈 Step 2: Engagement Calculation")
    df = calculate_engagement_rate(df)
    df = calculate_performance_score(df)
    df = calculate_viral_metrics(df)
    df, viral_threshold = determine_viral_threshold(df)
    df = calculate_engagement_tiers(df)
    
    engagement_summary = get_engagement_summary(df)
    print(f"✅ Engagement summary: {engagement_summary}")
    
    # Step 3: Process analysis features
    print("\n🔍 Step 3: Feature Processing")
    df = process_all_analysis_features(df)
    
    feature_summary = get_feature_summary(df)
    print(f"✅ Feature summary: {feature_summary}")
    
    # Final summary
    print(f"\n🎯 PIPELINE COMPLETE")
    print(f"📊 Final DataFrame: {len(df)} videos × {len(df.columns)} columns")
    print(f"🚗 Car brands: {df['car_brand'].nunique()} unique")
    print(f"🪝 Hook types: {df['hook_type'].nunique()} unique")
    print(f"🔄 Transitions: {df['transition_type'].nunique()} unique")
    print(f"⭐ Viral videos: {df['is_viral'].sum()}/{len(df)}")
    
    print(f"\n📋 Sample of extracted features:")
    sample_cols = ['video_id', 'views', 'engagement_rate', 'car_brand', 'hook_type', 'is_viral']
    available_cols = [col for col in sample_cols if col in df.columns]
    print(df[available_cols].head(3).to_string())
    
    return df

if __name__ == "__main__":
    test_df = test_complete_data_pipeline()