"""
Analyze individual car types and topics for viral performance impact.
Single responsibility: Car type and topic-specific performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_car_type_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance for each car type (supercar, sports, etc.).
    
    Args:
        df (pd.DataFrame): Video data with car type features and viral metrics
        
    Returns:
        Dict[str, Any]: Car type performance analysis
        
    Raises:
        ValueError: If required columns are missing
    """
    if 'car_type' not in df.columns:
        logger.warning("car_type column missing")
        return {}
    
    type_performance = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for car_type in df['car_type'].dropna().unique():
        type_data = df[df['car_type'] == car_type]
        if len(type_data) == 0:
            continue
            
        type_performance[car_type] = {
            'avg_views': float(type_data['views'].mean()),
            'avg_engagement': float(type_data['engagement_rate'].mean()),
            'total_views': int(type_data['views'].sum()),
            'viral_impact_score': float(type_data['viral_score'].mean()),
            'video_count': len(type_data),
            'max_views': int(type_data['views'].max()),
            'viral_videos': int((type_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((type_data['views'] >= viral_threshold).mean()),
            'performance_tier': _classify_type_performance(type_data['views'].mean(), type_data['engagement_rate'].mean())
        }
    
    logger.info(f"Analyzed {len(type_performance)} car types")
    return type_performance


def analyze_car_topics_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance for car topics from Twelve Labs analysis.
    
    Args:
        df (pd.DataFrame): Video data with car topics and viral metrics
        
    Returns:
        Dict[str, Any]: Car topics performance analysis
    """
    if 'car_topics_list' not in df.columns:
        logger.warning("car_topics_list column missing")
        return {}
    
    topics_performance = {}
    
    # Analyze each individual car topic across all videos
    for _, row in df.iterrows():
        topics = row.get('car_topics_list', [])
        if not isinstance(topics, list):
            continue
            
        for topic in topics:
            if topic and topic.strip():  # Skip empty topics
                if topic not in topics_performance:
                    topics_performance[topic] = {
                        'views': [], 
                        'engagement': [], 
                        'viral_scores': [],
                        'video_ids': []
                    }
                
                topics_performance[topic]['views'].append(row['views'])
                topics_performance[topic]['engagement'].append(row['engagement_rate'])
                topics_performance[topic]['viral_scores'].append(row['viral_score'])
                topics_performance[topic]['video_ids'].append(row.get('video_id', ''))
    
    # Calculate performance metrics for each topic
    analyzed_topics = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for topic, data in topics_performance.items():
        if len(data['views']) > 0:
            analyzed_topics[topic] = {
                'avg_views': float(np.mean(data['views'])),
                'avg_engagement': float(np.mean(data['engagement'])),
                'viral_impact_score': float(np.mean(data['viral_scores'])),
                'usage_count': len(data['views']),
                'max_views_achieved': int(max(data['views'])),
                'viral_videos': len([v for v in data['views'] if v >= viral_threshold]),
                'viral_success_rate': float(len([v for v in data['views'] if v >= viral_threshold]) / len(data['views'])),
                'topic_category': _categorize_car_topic(topic)
            }
    
    logger.info(f"Analyzed {len(analyzed_topics)} car topics")
    return analyzed_topics


def analyze_type_vs_brand_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze correlation between car types and brands for performance insights.
    
    Args:
        df (pd.DataFrame): Video data with both car types and brands
        
    Returns:
        Dict[str, Any]: Type vs brand correlation analysis
    """
    if 'car_type' not in df.columns or 'car_brand' not in df.columns:
        logger.warning("Missing car_type or car_brand columns")
        return {}
    
    correlation_analysis = {}
    
    # Create crosstab of type vs brand performance
    valid_data = df.dropna(subset=['car_type', 'car_brand'])
    if len(valid_data) == 0:
        return {}
    
    # Group by type and brand combinations
    type_brand_combinations = valid_data.groupby(['car_type', 'car_brand']).agg({
        'views': ['mean', 'count'],
        'engagement_rate': 'mean',
        'viral_score': 'mean'
    }).round(2)
    
    # Flatten column names
    type_brand_combinations.columns = ['avg_views', 'video_count', 'avg_engagement', 'viral_score']
    type_brand_combinations = type_brand_combinations.reset_index()
    
    # Convert to nested dictionary structure
    for _, row in type_brand_combinations.iterrows():
        car_type = row['car_type']
        car_brand = row['car_brand']
        
        if car_type not in correlation_analysis:
            correlation_analysis[car_type] = {}
        
        correlation_analysis[car_type][car_brand] = {
            'avg_views': float(row['avg_views']),
            'avg_engagement': float(row['avg_engagement']),
            'viral_score': float(row['viral_score']),
            'video_count': int(row['video_count'])
        }
    
    logger.info(f"Analyzed type-brand correlations for {len(correlation_analysis)} types")
    return correlation_analysis


def get_trending_car_content(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Identify trending car content based on recent performance.
    
    Args:
        df (pd.DataFrame): Video data with timestamps and car features
        
    Returns:
        Dict[str, Any]: Trending car content analysis
    """
    if 'created_at' not in df.columns:
        logger.warning("created_at column missing - cannot analyze trends")
        return {}
    
    trending_analysis = {}
    
    # Convert created_at to datetime if not already
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    
    # Analyze recent vs older content performance
    recent_cutoff = df['created_at'].max() - pd.Timedelta(days=3)  # Last 3 days
    recent_data = df[df['created_at'] >= recent_cutoff]
    older_data = df[df['created_at'] < recent_cutoff]
    
    if len(recent_data) > 0 and len(older_data) > 0:
        # Compare car types in recent vs older content
        if 'car_type' in df.columns:
            recent_types = recent_data['car_type'].value_counts()
            older_types = older_data['car_type'].value_counts()
            
            trending_analysis['trending_types'] = {}
            for car_type in recent_types.index:
                recent_count = recent_types.get(car_type, 0)
                older_count = older_types.get(car_type, 0)
                
                # Calculate trend momentum
                if older_count > 0:
                    momentum = (recent_count - older_count) / older_count
                else:
                    momentum = 1.0 if recent_count > 0 else 0.0
                
                trending_analysis['trending_types'][car_type] = {
                    'recent_videos': int(recent_count),
                    'older_videos': int(older_count),
                    'momentum': float(momentum),
                    'trend_status': 'Rising' if momentum > 0.2 else 'Declining' if momentum < -0.2 else 'Stable'
                }
        
        # Compare car brands in recent vs older content
        if 'car_brand' in df.columns:
            recent_brands = recent_data['car_brand'].value_counts()
            older_brands = older_data['car_brand'].value_counts()
            
            trending_analysis['trending_brands'] = {}
            for brand in recent_brands.index[:5]:  # Top 5 recent brands
                recent_count = recent_brands.get(brand, 0)
                older_count = older_brands.get(brand, 0)
                
                if older_count > 0:
                    momentum = (recent_count - older_count) / older_count
                else:
                    momentum = 1.0 if recent_count > 0 else 0.0
                
                trending_analysis['trending_brands'][brand] = {
                    'recent_videos': int(recent_count),
                    'momentum': float(momentum),
                    'trend_status': 'Rising' if momentum > 0.2 else 'Stable'
                }
    
    logger.info("Analyzed trending car content")
    return trending_analysis


def _categorize_car_topic(topic: str) -> str:
    """
    Categorize car topic into logical groups.
    
    Args:
        topic (str): Car topic from Twelve Labs analysis
        
    Returns:
        str: Topic category
    """
    topic_lower = topic.lower()
    
    if any(word in topic_lower for word in ['exhaust', 'sound', 'engine', 'rev']):
        return "Audio"
    elif any(word in topic_lower for word in ['acceleration', 'speed', 'fast', 'launch']):
        return "Performance"
    elif any(word in topic_lower for word in ['interior', 'dashboard', 'seats', 'cabin']):
        return "Interior"
    elif any(word in topic_lower for word in ['exterior', 'body', 'paint', 'wheels']):
        return "Exterior"
    elif any(word in topic_lower for word in ['driving', 'road', 'track', 'racing']):
        return "Driving"
    else:
        return "Other"


def _classify_type_performance(avg_views: float, avg_engagement: float) -> str:
    """
    Classify car type performance into tiers.
    
    Args:
        avg_views (float): Average views for the type
        avg_engagement (float): Average engagement rate for the type
        
    Returns:
        str: Performance tier classification
    """
    if avg_views > 50000 and avg_engagement > 0.15:
        return "Elite"
    elif avg_views > 20000 and avg_engagement > 0.12:
        return "High"  
    elif avg_views > 10000 and avg_engagement > 0.08:
        return "Medium"
    else:
        return "Low"


def get_car_type_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of car type analysis results.
    
    Args:
        df (pd.DataFrame): Video data with car type features
        
    Returns:
        Dict[str, Any]: Car type analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'videos_with_car_types': df['car_type'].notna().sum() if 'car_type' in df.columns else 0,
        'unique_car_types': df['car_type'].nunique() if 'car_type' in df.columns else 0,
        'unique_car_topics': len(set([topic for topics_list in df['car_topics_list'] if isinstance(topics_list, list) for topic in topics_list])) if 'car_topics_list' in df.columns else 0,
        'avg_topics_per_video': df['car_topics_list'].apply(lambda x: len(x) if isinstance(x, list) else 0).mean() if 'car_topics_list' in df.columns else 0
    }