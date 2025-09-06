"""
Analyze creator performance by follower tiers and verification status.
Single responsibility: Creator-specific performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_creator_tier_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance by creator follower tier.
    
    Args:
        df (pd.DataFrame): Video data with creator features and viral metrics
        
    Returns:
        Dict[str, Any]: Creator tier performance analysis
        
    Raises:
        ValueError: If required columns are missing
    """
    if 'follower_tier' not in df.columns:
        logger.warning("follower_tier column missing - cannot analyze by tier")
        return {}
    
    tier_performance = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for tier in df['follower_tier'].dropna().unique():
        tier_data = df[df['follower_tier'] == tier]
        if len(tier_data) == 0:
            continue
            
        tier_performance[tier] = {
            'avg_views': float(tier_data['views'].mean()),
            'avg_engagement': float(tier_data['engagement_rate'].mean()),
            'viral_impact_score': float(tier_data['viral_score'].mean()),
            'video_count': len(tier_data),
            'unique_creators': tier_data['author_username'].nunique(),
            'viral_videos': int((tier_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((tier_data['views'] >= viral_threshold).mean()),
            'avg_followers': float(tier_data['author_followers'].mean()) if 'author_followers' in tier_data.columns else 0,
            'views_per_follower': float((tier_data['views'] / tier_data['author_followers']).mean()) if 'author_followers' in tier_data.columns else 0,
            'performance_tier': _classify_tier_performance(tier_data['views'].mean(), tier_data['engagement_rate'].mean())
        }
    
    logger.info(f"Analyzed {len(tier_performance)} creator tiers")
    return tier_performance


def analyze_verification_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze performance difference between verified and unverified creators.
    
    Args:
        df (pd.DataFrame): Video data with verification status
        
    Returns:
        Dict[str, Any]: Verification impact analysis
    """
    if 'author_verified' not in df.columns:
        logger.warning("author_verified column missing")
        return {}
    
    verification_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for verified_status in [True, False]:
        verified_data = df[df['author_verified'] == verified_status]
        if len(verified_data) == 0:
            continue
            
        status_key = 'verified' if verified_status else 'unverified'
        verification_analysis[status_key] = {
            'video_count': len(verified_data),
            'unique_creators': verified_data['author_username'].nunique(),
            'avg_views': float(verified_data['views'].mean()),
            'avg_engagement': float(verified_data['engagement_rate'].mean()),
            'viral_impact_score': float(verified_data['viral_score'].mean()),
            'viral_videos': int((verified_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((verified_data['views'] >= viral_threshold).mean()),
            'avg_followers': float(verified_data['author_followers'].mean()) if 'author_followers' in verified_data.columns else 0
        }
    
    # Calculate verification advantage
    if 'verified' in verification_analysis and 'unverified' in verification_analysis:
        verification_analysis['verification_advantage'] = {
            'views_multiplier': verification_analysis['verified']['avg_views'] / verification_analysis['unverified']['avg_views'] if verification_analysis['unverified']['avg_views'] > 0 else 0,
            'engagement_difference': verification_analysis['verified']['avg_engagement'] - verification_analysis['unverified']['avg_engagement'],
            'viral_rate_difference': verification_analysis['verified']['viral_success_rate'] - verification_analysis['unverified']['viral_success_rate']
        }
    
    logger.info("Analyzed verification impact on performance")
    return verification_analysis


def analyze_individual_creator_performance(df: pd.DataFrame, min_videos: int = 2) -> Dict[str, Any]:
    """
    Analyze performance of individual creators with multiple videos.
    
    Args:
        df (pd.DataFrame): Video data with creator information
        min_videos (int): Minimum videos required to include creator
        
    Returns:
        Dict[str, Any]: Individual creator performance analysis
    """
    if 'author_username' not in df.columns:
        logger.warning("author_username column missing")
        return {}
    
    creator_performance = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Group by creator and analyze
    creator_groups = df.groupby('author_username')
    
    for creator, creator_data in creator_groups:
        if len(creator_data) < min_videos:
            continue
            
        creator_performance[creator] = {
            'video_count': len(creator_data),
            'avg_views': float(creator_data['views'].mean()),
            'avg_engagement': float(creator_data['engagement_rate'].mean()),
            'total_views': int(creator_data['views'].sum()),
            'viral_impact_score': float(creator_data['viral_score'].mean()),
            'viral_videos': int((creator_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((creator_data['views'] >= viral_threshold).mean()),
            'best_video_views': int(creator_data['views'].max()),
            'consistency_score': float(1 - (creator_data['views'].std() / creator_data['views'].mean())) if creator_data['views'].mean() > 0 else 0,
            'follower_count': int(creator_data['author_followers'].iloc[0]) if 'author_followers' in creator_data.columns else 0,
            'is_verified': bool(creator_data['author_verified'].iloc[0]) if 'author_verified' in creator_data.columns else False,
            'performance_tier': _classify_creator_performance(creator_data['views'].mean(), creator_data['engagement_rate'].mean())
        }
    
    logger.info(f"Analyzed {len(creator_performance)} individual creators with {min_videos}+ videos")
    return creator_performance


def analyze_creator_content_preferences(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze what content types each creator tier prefers.
    
    Args:
        df (pd.DataFrame): Video data with creator and content features
        
    Returns:
        Dict[str, Any]: Creator content preferences analysis
    """
    preferences_analysis = {}
    
    if 'follower_tier' not in df.columns:
        logger.warning("follower_tier column missing")
        return {}
    
    for tier in df['follower_tier'].dropna().unique():
        tier_data = df[df['follower_tier'] == tier]
        if len(tier_data) == 0:
            continue
            
        preferences_analysis[tier] = {}
        
        # Analyze car brand preferences
        if 'car_brand' in tier_data.columns:
            brand_counts = tier_data['car_brand'].value_counts()
            preferences_analysis[tier]['top_car_brands'] = brand_counts.head(5).to_dict()
        
        # Analyze hook preferences
        if 'hook_type' in tier_data.columns:
            hook_counts = tier_data['hook_type'].value_counts()
            preferences_analysis[tier]['top_hooks'] = hook_counts.head(5).to_dict()
        
        # Analyze video duration preferences
        if 'duration' in tier_data.columns:
            preferences_analysis[tier]['avg_duration'] = float(tier_data['duration'].mean())
            preferences_analysis[tier]['duration_std'] = float(tier_data['duration'].std())
        
        # Analyze multi-element usage
        if 'multi_brand_video' in tier_data.columns:
            preferences_analysis[tier]['multi_brand_rate'] = float(tier_data['multi_brand_video'].mean())
        
        if 'multi_hook_video' in tier_data.columns:
            preferences_analysis[tier]['multi_hook_rate'] = float(tier_data['multi_hook_video'].mean())
    
    logger.info(f"Analyzed content preferences for {len(preferences_analysis)} creator tiers")
    return preferences_analysis


def get_top_performing_creators(creator_analysis: Dict[str, Any], top_n: int = 10) -> Dict[str, Any]:
    """
    Get top performing creators by different metrics.
    
    Args:
        creator_analysis (Dict[str, Any]): Individual creator performance analysis
        top_n (int): Number of top performers to return
        
    Returns:
        Dict[str, Any]: Top performers by different metrics
    """
    if not creator_analysis:
        return {}
    
    # Sort by different metrics
    by_avg_views = sorted(creator_analysis.items(), key=lambda x: x[1]['avg_views'], reverse=True)
    by_total_views = sorted(creator_analysis.items(), key=lambda x: x[1]['total_views'], reverse=True)
    by_viral_rate = sorted(creator_analysis.items(), key=lambda x: x[1]['viral_success_rate'], reverse=True)
    by_consistency = sorted(creator_analysis.items(), key=lambda x: x[1]['consistency_score'], reverse=True)
    by_video_count = sorted(creator_analysis.items(), key=lambda x: x[1]['video_count'], reverse=True)
    
    return {
        'top_by_avg_views': [(creator, data['avg_views']) for creator, data in by_avg_views[:top_n]],
        'top_by_total_views': [(creator, data['total_views']) for creator, data in by_total_views[:top_n]],
        'top_by_viral_rate': [(creator, data['viral_success_rate']) for creator, data in by_viral_rate[:top_n]],
        'most_consistent': [(creator, data['consistency_score']) for creator, data in by_consistency[:top_n]],
        'most_active': [(creator, data['video_count']) for creator, data in by_video_count[:top_n]]
    }


def analyze_follower_engagement_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze correlation between follower count and engagement metrics.
    
    Args:
        df (pd.DataFrame): Video data with follower and engagement data
        
    Returns:
        Dict[str, Any]: Follower-engagement correlation analysis
    """
    if 'author_followers' not in df.columns:
        logger.warning("author_followers column missing")
        return {}
    
    correlation_analysis = {}
    
    # Calculate correlations
    valid_data = df.dropna(subset=['author_followers', 'views', 'engagement_rate'])
    
    if len(valid_data) > 5:  # Need minimum data for correlation
        # Follower count vs views correlation
        views_corr = valid_data['author_followers'].corr(valid_data['views'])
        
        # Follower count vs engagement rate correlation
        engagement_corr = valid_data['author_followers'].corr(valid_data['engagement_rate'])
        
        # Views per follower analysis
        valid_data['views_per_follower'] = valid_data['views'] / valid_data['author_followers']
        
        correlation_analysis = {
            'followers_views_correlation': float(views_corr),
            'followers_engagement_correlation': float(engagement_corr),
            'avg_views_per_follower': float(valid_data['views_per_follower'].mean()),
            'median_views_per_follower': float(valid_data['views_per_follower'].median()),
            'sample_size': len(valid_data)
        }
        
        # Analyze by follower ranges
        follower_ranges = {
            'micro': (0, 100000),
            'mid': (100000, 500000), 
            'large': (500000, 1000000),
            'mega': (1000000, float('inf'))
        }
        
        correlation_analysis['by_follower_range'] = {}
        for range_name, (min_followers, max_followers) in follower_ranges.items():
            range_data = valid_data[
                (valid_data['author_followers'] >= min_followers) & 
                (valid_data['author_followers'] < max_followers)
            ]
            
            if len(range_data) > 0:
                correlation_analysis['by_follower_range'][range_name] = {
                    'creator_count': len(range_data),
                    'avg_views_per_follower': float(range_data['views_per_follower'].mean()),
                    'avg_engagement_rate': float(range_data['engagement_rate'].mean())
                }
    
    logger.info("Analyzed follower-engagement correlations")
    return correlation_analysis


def _classify_tier_performance(avg_views: float, avg_engagement: float) -> str:
    """
    Classify creator tier performance.
    
    Args:
        avg_views (float): Average views for the tier
        avg_engagement (float): Average engagement rate for the tier
        
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


def _classify_creator_performance(avg_views: float, avg_engagement: float) -> str:
    """
    Classify individual creator performance.
    
    Args:
        avg_views (float): Creator's average views
        avg_engagement (float): Creator's average engagement rate
        
    Returns:
        str: Performance tier classification
    """
    if avg_views > 100000 and avg_engagement > 0.15:
        return "Top_Performer"
    elif avg_views > 50000 and avg_engagement > 0.12:
        return "High_Performer"  
    elif avg_views > 20000 and avg_engagement > 0.08:
        return "Medium_Performer"
    else:
        return "Emerging"


def get_creator_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of creator analysis results.
    
    Args:
        df (pd.DataFrame): Video data with creator features
        
    Returns:
        Dict[str, Any]: Creator analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'unique_creators': df['author_username'].nunique() if 'author_username' in df.columns else 0,
        'verified_creators': df['author_verified'].sum() if 'author_verified' in df.columns else 0,
        'avg_followers_per_creator': df['author_followers'].mean() if 'author_followers' in df.columns else 0,
        'follower_tiers_represented': df['follower_tier'].nunique() if 'follower_tier' in df.columns else 0,
        'creators_with_multiple_videos': (df['author_username'].value_counts() > 1).sum() if 'author_username' in df.columns else 0
    }