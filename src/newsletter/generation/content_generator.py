"""
Generate database-ready newsletter content for CRM dashboard consumption.
Single responsibility: Create structured JSON data for database storage and TypeScript interfaces.
"""
import pandas as pd
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


def generate_database_newsletter_structure(df: pd.DataFrame, 
                                         all_analysis_results: Dict[str, Any],
                                         champion_portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate database-ready newsletter structure for CRM dashboard.
    
    Args:
        df (pd.DataFrame): Video data for the week
        all_analysis_results (Dict[str, Any]): Combined results from all analysis layers
        champion_portfolio (Dict[str, Any]): Selected champion videos and examples
        
    Returns:
        Dict[str, Any]: Database-ready newsletter structure
        
    Raises:
        ValueError: If insufficient data for newsletter generation
    """
    if len(df) < 1:
        raise ValueError("No video data available for newsletter generation")
    
    # Extract week date range
    week_start = df['created_at'].min().date() if 'created_at' in df.columns else datetime.now().date()
    week_end = df['created_at'].max().date() if 'created_at' in df.columns else datetime.now().date()
    
    newsletter_structure = {
        'newsletter_main': _generate_newsletter_main_table_data(df, all_analysis_results, week_start, week_end),
        'newsletter_champions': _generate_champions_table_data(champion_portfolio),
        'newsletter_top_rankings': _generate_top_rankings_table_data(all_analysis_results),
        'newsletter_recommendations': _generate_recommendations_table_data(all_analysis_results),
        'newsletter_statistical_findings': _generate_statistical_findings_table_data(all_analysis_results)
    }
    
    logger.info("Database newsletter structure generation complete")
    return newsletter_structure


def _generate_newsletter_main_table_data(df: pd.DataFrame, 
                                       all_analysis_results: Dict[str, Any],
                                       week_start: datetime.date,
                                       week_end: datetime.date) -> Dict[str, Any]:
    """
    Generate main newsletter table data for database insertion.
    
    Args:
        df (pd.DataFrame): Video data
        all_analysis_results (Dict[str, Any]): All analysis results
        week_start (datetime.date): Week start date
        week_end (datetime.date): Week end date
        
    Returns:
        Dict[str, Any]: Newsletter main table data
    """
    # Extract top performers from analysis results
    analyzer_results = all_analysis_results.get('analyzer_results', {})
    
    # Get top performers for each category
    top_performers = _extract_top_performers_from_analysis(analyzer_results)
    
    # Calculate optimal specs
    optimal_specs = _calculate_optimal_specs_from_data(df, analyzer_results)
    
    # Generate newsletter main table data - only include columns that exist in database
    main_data = {
        # IDENTIFIERS
        'week_start_date': week_start.isoformat(),
        'week_end_date': week_end.isoformat(), 
        'newsletter_id': f"car-trends-{week_start.strftime('%Y%m%d')}",
        
        # OVERVIEW METRICS (match database schema exactly)
        'total_videos_tracked': len(df),
        'total_views': int(df['views'].sum()) if 'views' in df.columns else 0,
        'total_creators': int(df['author_username'].nunique()) if 'author_username' in df.columns else 0,
        'avg_engagement_rate': float(df['engagement_rate'].mean() * 100) if 'engagement_rate' in df.columns else 0.0,
        'viral_videos_count': int(len(df[df['is_viral'] == True])) if 'is_viral' in df.columns else 0,
        'viral_success_rate': float((len(df[df['is_viral'] == True]) / len(df)) * 100) if 'is_viral' in df.columns and len(df) > 0 else 0.0,
        
        # TOP PERFORMERS (only fields that exist in database)
        'top_car_brand': top_performers.get('car_brand', {}).get('name', 'Unknown'),
        'top_car_brand_views': int(top_performers.get('car_brand', {}).get('views', 0)),
        'top_car_brand_engagement': float(top_performers.get('car_brand', {}).get('engagement', 0.0)) * 100,
        
        'top_hook_type': top_performers.get('hook', {}).get('name', 'Unknown'),
        'top_hook_views': int(top_performers.get('hook', {}).get('views', 0)),
        'top_hook_engagement': float(top_performers.get('hook', {}).get('engagement', 0.0)) * 100,
        
        'top_transition_type': top_performers.get('transition', {}).get('name', 'Unknown'),
        'top_transition_views': int(top_performers.get('transition', {}).get('views', 0)),
        'top_transition_engagement': float(top_performers.get('transition', {}).get('engagement', 0.0)) * 100,
        
        'top_music_track': top_performers.get('music_track', {}).get('name', 'Unknown'),
        'top_music_track_views': int(top_performers.get('music_track', {}).get('views', 0)),
        'top_music_track_url': top_performers.get('music_track', {}).get('url', ''),
        
        'top_hashtag': top_performers.get('hashtag', {}).get('name', 'Unknown'),
        'top_hashtag_usage_count': int(top_performers.get('hashtag', {}).get('usage_count', 0)),
        'top_hashtag_avg_views': int(top_performers.get('hashtag', {}).get('avg_views', 0)),
        
        # OPTIMAL SPECS (only fields that exist in database)
        'optimal_duration_seconds': optimal_specs.get('duration_seconds', 15),
        'optimal_posting_hour': optimal_specs.get('posting_hour', 19),
        'optimal_posting_day': optimal_specs.get('posting_day', 'Friday'),
        'best_hashtag_count': optimal_specs.get('hashtag_count', 5),
        
        # BENCHMARKS
        'viral_threshold': int(df['viral_threshold'].iloc[0]) if 'viral_threshold' in df.columns and len(df) > 0 else 1000000,
        'avg_views_benchmark': int(df['views'].mean()) if 'views' in df.columns else 100000
    }
    
    return main_data


def _generate_champions_table_data(champion_portfolio: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate champion videos table data for database insertion.
    
    Args:
        champion_portfolio (Dict[str, Any]): Champion video selections
        
    Returns:
        List[Dict[str, Any]]: Champion videos data for database
    """
    champions_data = []
    
    # Process each champion category
    champion_categories = {
        'hook_champions': 'hook_type',
        'car_brand_champions': 'car_brand', 
        'transition_champions': 'transition',
        'creator_tier_champions': 'creator_tier',
        'performance_champions': 'performance',
        'overall_performance_champion': 'overall'
    }
    
    for portfolio_key, db_category in champion_categories.items():
        champions = champion_portfolio.get(portfolio_key, [])
        
        if isinstance(champions, list):
            for champion in champions:
                if isinstance(champion, dict):
                    champion_data = {
                        'category': db_category,
                        'element_name': champion.get('element', 'Unknown'),
                        'video_id': champion.get('video_id', ''),
                        'author_username': champion.get('author_username', ''),
                        'video_url': f"https://tiktok.com/@{champion.get('author_username', '')}/video/{champion.get('video_id', '')}",
                        'views': int(champion.get('views', 0)),
                        'engagement_rate': float(champion.get('engagement_rate', 0.0)) * 100,  # Convert to percentage
                        'viral_score': float(champion.get('viral_score', 0.0)),
                        'champion_reason': champion.get('champion_reason', 'Top performer')
                    }
                    champions_data.append(champion_data)
        elif champions is not None:  # Single champion (overall_performance_champion)
            champion_data = {
                'category': 'overall_champion',
                'element_name': 'Week\'s Best Performance',
                'video_id': champions.get('video_id', ''),
                'author_username': champions.get('author_username', ''),
                'video_url': f"https://tiktok.com/@{champions.get('author_username', '')}/video/{champions.get('video_id', '')}",
                'views': int(champions.get('views', 0)),
                'engagement_rate': float(champions.get('engagement_rate', 0.0)) * 100,  # Convert to percentage
                'viral_score': float(champions.get('viral_score', 0.0)),
                'champion_reason': champions.get('champion_reason', 'Overall best performance')
            }
            champions_data.append(champion_data)
    
    return champions_data


def _generate_top_rankings_table_data(all_analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate top 5 rankings table data for each category.
    
    Args:
        all_analysis_results (Dict[str, Any]): All analysis results
        
    Returns:
        List[Dict[str, Any]]: Top rankings data for database
    """
    rankings_data = []
    analyzer_results = all_analysis_results.get('analyzer_results', {})
    
    # Categories to generate rankings for
    ranking_categories = {
        'hashtag_analysis': 'hashtags',
        'effects_analysis': 'effects',
        'brand_analysis': 'car_brands',
        'music_analysis': 'music_tracks'
    }
    
    for analysis_key, category_name in ranking_categories.items():
        analysis_data = analyzer_results.get(analysis_key, {})
        
        if isinstance(analysis_data, dict) and analysis_data:
            # Convert to list and sort by performance
            sorted_items = sorted(
                analysis_data.items(), 
                key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0, 
                reverse=True
            )[:5]  # Top 5
            
            for rank, (element_name, data) in enumerate(sorted_items, 1):
                if isinstance(data, dict):
                    ranking_entry = {
                        'category': category_name,
                        'rank_position': rank,
                        'element_name': element_name,
                        'usage_count': int(data.get('video_count', 0)),
                        'avg_views': int(data.get('avg_views', 0)),
                        'avg_engagement': float(data.get('avg_engagement_rate', 0.0)) * 100
                    }
                    rankings_data.append(ranking_entry)
    
    return rankings_data


def _generate_recommendations_table_data(all_analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate AI recommendations table data for database.
    
    Args:
        all_analysis_results (Dict[str, Any]): All analysis results with GPT insights
        
    Returns:
        List[Dict[str, Any]]: Recommendations data for database
    """
    recommendations_data = []
    gpt_insights = all_analysis_results.get('gpt_insights', {})
    
    # Process creator recommendations
    creator_recs = gpt_insights.get('creator_recommendations', {})
    for audience_type, recs in creator_recs.items():
        if isinstance(recs, list):
            for rec in recs[:3]:  # Top 3 per audience
                if isinstance(rec, dict):
                    recommendation_entry = {
                        'recommendation_type': 'creator_strategy',
                        'target_audience': audience_type,
                        'recommendation_title': rec.get('recommendation', 'Strategy Recommendation'),
                        'recommendation_text': rec.get('recommendation', ''),
                        'confidence_level': 'High',
                        'expected_impact': rec.get('expected_impact', '')
                    }
                    recommendations_data.append(recommendation_entry)
    
    # Process content gap opportunities
    gap_analysis = gpt_insights.get('content_gap_analysis', {})
    underexplored = gap_analysis.get('underexplored_combinations', [])
    for gap in underexplored[:3]:  # Top 3 gaps
        if isinstance(gap, dict):
            recommendation_entry = {
                'recommendation_type': 'content_gap',
                'target_audience': 'all_creators',
                'recommendation_title': f"Explore {gap.get('combination', 'New Combination')}",
                'recommendation_text': gap.get('combination', ''),
                'confidence_level': 'Medium',
                'expected_impact': gap.get('viral_probability', '')
            }
            recommendations_data.append(recommendation_entry)
    
    # Process trend predictions
    trend_predictions = gpt_insights.get('trend_predictions', {})
    content_predictions = trend_predictions.get('content_trend_predictions', [])
    for prediction in content_predictions[:3]:  # Top 3 predictions
        if isinstance(prediction, dict):
            recommendation_entry = {
                'recommendation_type': 'trend_prediction',
                'target_audience': 'all_creators',
                'recommendation_title': f"Prepare for {prediction.get('trend', 'Upcoming Trend')}",
                'recommendation_text': prediction.get('trend', ''),
                'confidence_level': prediction.get('confidence', 'Medium'),
                'expected_impact': prediction.get('impact_assessment', '')
            }
            recommendations_data.append(recommendation_entry)
    
    return recommendations_data


def _generate_statistical_findings_table_data(all_analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate statistical findings table data for database.
    
    Args:
        all_analysis_results (Dict[str, Any]): All analysis results with statistical validation
        
    Returns:
        List[Dict[str, Any]]: Statistical findings data for database
    """
    findings_data = []
    stats = all_analysis_results.get('statistical_results', {})
    
    # Process significant differences (main statistical findings)
    significant_differences = stats.get('significant_differences', [])
    for diff in significant_differences[:5]:  # Top 5 findings
        if isinstance(diff, dict):
            finding_entry = {
                'finding_type': diff.get('finding_type', 'performance_difference'),
                'variable_tested': diff.get('element', diff.get('category', 'Unknown')),
                'p_value': float(diff.get('p_value', 1.0)),
                'effect_size': float(diff.get('effect_size', diff.get('value', 0.0))),
                'effect_magnitude': diff.get('significance', 'Unknown'),
                'finding_description': diff.get('sample_note', f"Performance finding for {diff.get('element', 'Unknown')}")
            }
            findings_data.append(finding_entry)
    
    # Process significance tests
    sig_tests = stats.get('significance_results', {}).get('significant_tests', [])
    for test in sig_tests[:5]:  # Top 5 significant tests
        if isinstance(test, dict):
            finding_entry = {
                'finding_type': 'significance_test',
                'variable_tested': test.get('variable', ''),
                'p_value': float(test.get('p_value', 1.0)),
                'effect_size': float(test.get('cramers_v', test.get('cohens_d', test.get('eta_squared', 0.0)))),
                'effect_magnitude': test.get('effect_magnitude', 'Unknown'),
                'finding_description': f"Significant difference in {test.get('variable', '')} performance"
            }
            findings_data.append(finding_entry)
    
    return findings_data


def _extract_top_performers_from_analysis(analyzer_results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extract top performers from all analyzer results."""
    top_performers = {}
    
    # Extract top car brand
    brand_analysis = analyzer_results.get('brand_analysis', {})
    if brand_analysis:
        top_brand = max(brand_analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
        if len(top_brand) == 2 and isinstance(top_brand[1], dict):
            top_performers['car_brand'] = {
                'name': top_brand[0],
                'views': top_brand[1].get('avg_views', 0),
                'engagement': top_brand[1].get('avg_engagement_rate', 0.0),
                'usage_count': top_brand[1].get('video_count', 0)
            }
    
    # Extract top hook
    hook_analysis = analyzer_results.get('hook_analysis', {})
    if hook_analysis:
        top_hook = max(hook_analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
        if len(top_hook) == 2 and isinstance(top_hook[1], dict):
            top_performers['hook'] = {
                'name': top_hook[0],
                'views': top_hook[1].get('avg_views', 0),
                'engagement': top_hook[1].get('avg_engagement_rate', 0.0),
                'usage_count': top_hook[1].get('video_count', 0)
            }
    
    # Extract top transition
    transition_analysis = analyzer_results.get('transition_analysis', {})
    if transition_analysis:
        top_transition = max(transition_analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
        if len(top_transition) == 2 and isinstance(top_transition[1], dict):
            top_performers['transition'] = {
                'name': top_transition[0],
                'views': top_transition[1].get('avg_views', 0),
                'engagement': top_transition[1].get('avg_engagement_rate', 0.0),
                'usage_count': top_transition[1].get('video_count', 0)
            }
    
    # Extract top effect
    effects_analysis = analyzer_results.get('effects_analysis', {})
    if effects_analysis:
        top_effect = max(effects_analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
        if len(top_effect) == 2 and isinstance(top_effect[1], dict):
            top_performers['effect'] = {
                'name': top_effect[0],
                'views': top_effect[1].get('avg_views', 0),
                'engagement': top_effect[1].get('avg_engagement_rate', 0.0),
                'usage_count': top_effect[1].get('video_count', 0)
            }
    
    # Extract top music track
    music_analysis = analyzer_results.get('music_analysis', {})
    if music_analysis:
        top_music = max(music_analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
        if len(top_music) == 2 and isinstance(top_music[1], dict):
            top_performers['music_track'] = {
                'name': top_music[0],
                'views': top_music[1].get('avg_views', 0),
                'engagement': top_music[1].get('avg_engagement_rate', 0.0),
                'url': f"https://tiktok.com/music/{top_music[0].replace(' ', '-')}"
            }
    
    # Extract top hashtag
    hashtag_analysis = analyzer_results.get('hashtag_analysis', {})
    if hashtag_analysis:
        top_hashtag = max(hashtag_analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
        if len(top_hashtag) == 2 and isinstance(top_hashtag[1], dict):
            top_performers['hashtag'] = {
                'name': top_hashtag[0],
                'usage_count': top_hashtag[1].get('video_count', 0),
                'avg_views': top_hashtag[1].get('avg_views', 0)
            }
    
    # Add default values for missing categories
    default_categories = ['car_type', 'music_genre', 'edit_style', 'creator_tier']
    for category in default_categories:
        if category not in top_performers:
            top_performers[category] = {
                'name': 'Unknown',
                'views': 0,
                'engagement': 0.0,
                'usage_count': 0
            }
    
    return top_performers


def _calculate_optimal_specs_from_data(df: pd.DataFrame, analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate optimal specs from data and analysis results."""
    optimal_specs = {}
    
    # Extract optimal duration
    specs_analysis = analyzer_results.get('specs_analysis', {})
    if specs_analysis:
        # Find best performing duration
        best_duration = max(specs_analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
        if len(best_duration) == 2:
            optimal_specs['duration_seconds'] = 15  # Default
            optimal_specs['duration_range'] = best_duration[0] if isinstance(best_duration[0], str) else '15-18 seconds'
    
    # Extract optimal timing
    timing_analysis = analyzer_results.get('timing_analysis', {})
    if timing_analysis:
        # Find best performing hour
        best_hour = max(timing_analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
        if len(best_hour) == 2:
            try:
                optimal_specs['posting_hour'] = int(best_hour[0]) if str(best_hour[0]).isdigit() else 19
            except:
                optimal_specs['posting_hour'] = 19
            optimal_specs['posting_day'] = 'Friday'  # Default
            optimal_specs['day_performance'] = best_hour[1].get('avg_views', 0) if isinstance(best_hour[1], dict) else 0
    
    # Set other optimal specs with defaults
    optimal_specs.update({
        'engagement_timeframe': '7-9 PM EST',
        'hashtag_count': 5,
        'aspect_ratio': '9:16',
        'resolution': '1080x1920',
        'quality_range': '8.5-10',
        'description_length': 150
    })
    
    return optimal_specs



def generate_typescript_interfaces() -> str:
    """Generate TypeScript interfaces for the newsletter data structure."""
    typescript_interfaces = '''
// Newsletter Database TypeScript Interfaces

interface NewsletterMain {
  id?: number;
  week_start_date: string;
  week_end_date: string;
  newsletter_id: string;
  
  // Overview metrics
  total_videos_tracked: number;
  total_views: number;
  total_creators: number;
  avg_engagement_rate: number;
  viral_videos_count: number;
  viral_success_rate: number;
  average_time_to_viral: number;
  
  // Top performers
  top_car_brand: string;
  top_car_brand_views: number;
  top_car_brand_engagement: number;
  top_car_brand_usage_count: number;
  
  top_car_type: string;
  top_car_type_views: number;
  top_car_type_engagement: number;
  
  top_hook_type: string;
  top_hook_views: number;
  top_hook_engagement: number;
  top_hook_usage_count: number;
  
  top_transition_type: string;
  top_transition_views: number;
  top_transition_engagement: number;
  top_transition_usage_count: number;
  
  top_effect_used: string;
  top_effect_views: number;
  top_effect_engagement: number;
  top_effect_usage_count: number;
  
  top_music_track: string;
  top_music_track_views: number;
  top_music_track_engagement: number;
  top_music_track_url: string;
  
  top_music_genre: string;
  top_music_genre_views: number;
  top_music_genre_engagement: number;
  
  top_hashtag: string;
  top_hashtag_usage_count: number;
  top_hashtag_avg_views: number;
  
  top_edit_style: string;
  top_edit_views: number;
  top_edit_engagement: number;
  
  top_creator_tier: string;
  top_creator_tier_performance: number;
  top_creator_tier_engagement: number;
  
  // Optimal specs
  optimal_duration_seconds: number;
  best_video_duration_range: string;
  optimal_posting_hour: number;
  optimal_posting_day: string;
  best_upload_day_performance: number;
  peak_engagement_timeframe: string;
  
  best_hashtag_count: number;
  optimal_aspect_ratio: string;
  optimal_resolution: string;
  best_quality_score_range: string;
  optimal_description_length: number;
  
  // Benchmarks
  viral_threshold: number;
  high_performance_threshold: number;
  avg_views_benchmark: number;
  
  analysis_completeness: string;
  data_quality_score: string;
  created_at?: string;
}

interface NewsletterChampion {
  id?: number;
  newsletter_id?: number;
  category: string;
  element_name: string;
  video_id: string;
  author_username: string;
  video_url: string;
  video_description: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  engagement_rate: number;
  viral_score: number;
  champion_reason: string;
  performance_advantage: string;
  statistical_backing: string;
  created_at?: string;
}

interface NewsletterTopRanking {
  id?: number;
  newsletter_id?: number;
  category: string;
  rank_position: number;
  element_name: string;
  usage_count: number;
  avg_views: number;
  avg_engagement: number;
  total_views: number;
  element_url?: string;
  trend_direction: "Rising" | "Stable" | "Declining";
  week_over_week_change: number;
  created_at?: string;
}

interface NewsletterRecommendation {
  id?: number;
  newsletter_id?: number;
  recommendation_type: string;
  target_audience: string;
  recommendation_title: string;
  recommendation_text: string;
  implementation_steps: string[];
  statistical_backing: string;
  confidence_level: "High" | "Medium" | "Low";
  implementation_difficulty: "Easy" | "Medium" | "Hard";
  expected_impact: string;
  example_video_url?: string;
  success_probability: string;
  timeline: string;
  created_at?: string;
}

interface NewsletterStatisticalFinding {
  id?: number;
  newsletter_id?: number;
  finding_type: string;
  test_name: string;
  variable_tested: string;
  p_value: number;
  test_statistic: number;
  effect_size: number;
  effect_magnitude: string;
  finding_description: string;
  practical_significance: boolean;
  confidence_interval_lower: number;
  confidence_interval_upper: number;
  sample_size: number;
  statistical_power: number;
  created_at?: string;
}

// Complete newsletter structure for API responses
interface NewsletterDatabaseStructure {
  newsletter_main: NewsletterMain;
  newsletter_champions: NewsletterChampion[];
  newsletter_top_rankings: NewsletterTopRanking[];
  newsletter_recommendations: NewsletterRecommendation[];
  newsletter_statistical_findings: NewsletterStatisticalFinding[];
}

// Dashboard display interfaces
interface DashboardOverview {
  totalVideos: number;
  totalViews: number;
  totalCreators: number;
  avgEngagement: number;
  viralSuccessRate: number;
  topPerformers: {
    carBrand: { name: string; views: number; };
    hookType: { name: string; views: number; };
    musicTrack: { name: string; url: string; };
  };
}

export type {
  NewsletterMain,
  NewsletterChampion,
  NewsletterTopRanking,
  NewsletterRecommendation,
  NewsletterStatisticalFinding,
  NewsletterDatabaseStructure,
  DashboardOverview
};
'''
    return typescript_interfaces


def get_database_content_generation_summary(newsletter_structure: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary of database content generation results."""
    return {
        'database_tables_generated': len(newsletter_structure),
        'champions_records': len(newsletter_structure.get('newsletter_champions', [])),
        'rankings_records': len(newsletter_structure.get('newsletter_top_rankings', [])),
        'recommendations_records': len(newsletter_structure.get('newsletter_recommendations', [])),
        'statistical_findings_records': len(newsletter_structure.get('newsletter_statistical_findings', [])),
        'main_newsletter_record': 1 if newsletter_structure.get('newsletter_main') else 0,
        'total_database_records': (
            1 + 
            len(newsletter_structure.get('newsletter_champions', [])) +
            len(newsletter_structure.get('newsletter_top_rankings', [])) +
            len(newsletter_structure.get('newsletter_recommendations', [])) +
            len(newsletter_structure.get('newsletter_statistical_findings', []))
        ),
        'data_format': 'Database-ready JSON',
        'typescript_interfaces_available': True,
        'generation_status': 'complete'
    }


# End of content_generator.py - Database-ready newsletter generation complete