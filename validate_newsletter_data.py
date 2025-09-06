#!/usr/bin/env python3
"""
Validate newsletter data in Supabase against original videos table data.
Check if the generated newsletter metrics are accurate and make sense.
"""
import os
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()

def validate_newsletter_data():
    """Load and validate all newsletter data from Supabase."""
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    
    print("🔍 NEWSLETTER DATA VALIDATION")
    print("=" * 60)
    
    # 1. Get the latest newsletter
    newsletters = supabase.table('newsletters').select('*').order('created_at', desc=True).limit(1).execute()
    if not newsletters.data:
        print("❌ No newsletters found in database!")
        return
    
    newsletter = newsletters.data[0]
    newsletter_id = newsletter['id']
    
    print(f"📰 Latest Newsletter: {newsletter['newsletter_id']}")
    print(f"📅 Period: {newsletter['week_start_date']} to {newsletter['week_end_date']}")
    print()
    
    # 2. Get original video data for validation
    videos = supabase.table('videos').select('*').execute()
    video_data = videos.data
    
    print(f"📊 MAIN NEWSLETTER METRICS VALIDATION:")
    print(f"   Videos tracked: {newsletter['total_videos_tracked']} (DB has {len(video_data)} videos)")
    print(f"   Total views: {newsletter['total_views']:,}")
    print(f"   Total creators: {newsletter['total_creators']}")
    print(f"   Avg engagement rate: {newsletter['avg_engagement_rate']:.2f}%")
    print(f"   Viral videos: {newsletter['viral_videos_count']}")
    print(f"   Viral success rate: {newsletter['viral_success_rate']:.2f}%")
    print()
    
    # 3. Validate against actual video data
    if video_data:
        actual_total_views = sum(v['views'] for v in video_data)
        actual_creators = len(set(v['author_username'] for v in video_data))
        
        print(f"✅ VALIDATION CHECK:")
        print(f"   Total views - Newsletter: {newsletter['total_views']:,}, Actual: {actual_total_views:,}")
        print(f"   Creators - Newsletter: {newsletter['total_creators']}, Actual: {actual_creators}")
        
        views_match = abs(newsletter['total_views'] - actual_total_views) / max(actual_total_views, 1) < 0.01
        creators_match = newsletter['total_creators'] == actual_creators
        
        print(f"   Views match: {'✅' if views_match else '❌'}")
        print(f"   Creators match: {'✅' if creators_match else '❌'}")
    print()
    
    # 4. Check top performers make sense
    print(f"🏆 TOP PERFORMERS:")
    print(f"   Car brand: {newsletter['top_car_brand']} ({newsletter['top_car_brand_views']:,} views)")
    print(f"   Hook type: {newsletter['top_hook_type']} ({newsletter['top_hook_views']:,} views)")
    print(f"   Transition: {newsletter['top_transition_type']} ({newsletter['top_transition_views']:,} views)")
    print(f"   Music track: {newsletter['top_music_track']} ({newsletter['top_music_track_views']:,} views)")
    print(f"   Top hashtag: {newsletter['top_hashtag']} ({newsletter['top_hashtag_usage_count']} uses)")
    print()
    
    # 5. Check champions
    champions = supabase.table('newsletter_champions').select('*').eq('newsletter_id', newsletter_id).execute()
    print(f"🏆 CHAMPIONS ({len(champions.data)} found):")
    for champ in champions.data:
        print(f"   {champ['category']}: {champ['element_name']}")
        print(f"      Video: @{champ['author_username']} ({champ['views']:,} views, {champ['engagement_rate']:.2f}% eng)")
        print(f"      Reason: {champ['champion_reason']}")
        print()
    
    # 6. Check rankings
    rankings = supabase.table('newsletter_top_rankings').select('*').eq('newsletter_id', newsletter_id).execute()
    print(f"📊 TOP RANKINGS ({len(rankings.data)} found):")
    ranking_categories = {}
    for rank in rankings.data:
        category = rank['category']
        if category not in ranking_categories:
            ranking_categories[category] = []
        ranking_categories[category].append(rank)
    
    for category, items in ranking_categories.items():
        print(f"   {category.title()}:")
        for item in sorted(items, key=lambda x: x['rank_position'])[:3]:
            print(f"      #{item['rank_position']}: {item['element_name']} ({item['avg_views']:,} avg views, {item['usage_count']} uses)")
        print()
    
    # 7. Check recommendations
    recs = supabase.table('newsletter_recommendations').select('*').eq('newsletter_id', newsletter_id).execute()
    print(f"💡 RECOMMENDATIONS ({len(recs.data)} found):")
    for rec in recs.data:
        print(f"   {rec['recommendation_type']}: {rec['recommendation_title']}")
        print(f"      Target: {rec['target_audience']}")
        print(f"      Confidence: {rec['confidence_level']}")
        print(f"      Text: {rec['recommendation_text'][:100]}...")
        print()
    
    # 8. Check statistical findings
    findings = supabase.table('newsletter_statistical_findings').select('*').eq('newsletter_id', newsletter_id).execute()
    print(f"📈 STATISTICAL FINDINGS ({len(findings.data)} found):")
    for finding in findings.data:
        print(f"   {finding['finding_type']}: {finding['variable_tested']}")
        print(f"      P-value: {finding['p_value']:.6f}")
        print(f"      Effect size: {finding['effect_size']:.3f} ({finding['effect_magnitude']})")
        print(f"      Description: {finding['finding_description']}")
        print()
    
    # 9. Data quality summary
    print(f"📋 DATA QUALITY SUMMARY:")
    total_records = 1 + len(champions.data) + len(rankings.data) + len(recs.data) + len(findings.data)
    print(f"   Total database records: {total_records}")
    print(f"   Newsletter main: 1 record ✅")
    print(f"   Champions: {len(champions.data)} records {'✅' if len(champions.data) > 0 else '⚠️'}")
    print(f"   Rankings: {len(rankings.data)} records {'✅' if len(rankings.data) > 0 else '⚠️'}")
    print(f"   Recommendations: {len(recs.data)} records {'✅' if len(recs.data) > 0 else '⚠️'}")
    print(f"   Statistical findings: {len(findings.data)} records {'✅' if len(findings.data) > 0 else '⚠️'}")
    
    # 10. Check for data anomalies
    print(f"\n🔍 ANOMALY DETECTION:")
    anomalies = []
    
    # Check for impossible values
    if newsletter['avg_engagement_rate'] > 100:
        anomalies.append(f"Engagement rate too high: {newsletter['avg_engagement_rate']}%")
    if newsletter['viral_success_rate'] > 100:
        anomalies.append(f"Viral success rate too high: {newsletter['viral_success_rate']}%")
    
    # Check champion data
    for champ in champions.data:
        if champ['engagement_rate'] > 100:
            anomalies.append(f"Champion engagement rate too high: {champ['engagement_rate']}% for {champ['element_name']}")
        if champ['viral_score'] > 100:
            anomalies.append(f"Champion viral score too high: {champ['viral_score']} for {champ['element_name']}")
    
    if anomalies:
        for anomaly in anomalies:
            print(f"   ❌ {anomaly}")
    else:
        print(f"   ✅ No anomalies detected")
    
    print(f"\n🎯 OVERALL DATA QUALITY: {'✅ EXCELLENT' if not anomalies and total_records > 20 else '⚠️ NEEDS REVIEW'}")

if __name__ == "__main__":
    validate_newsletter_data()