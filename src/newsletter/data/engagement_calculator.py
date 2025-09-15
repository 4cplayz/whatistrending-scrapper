"""
Calculate engagement metrics and viral performance scores.
Single responsibility: Pure engagement calculations with no side effects.
"""
import pandas as pd
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_engagement_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate engagement rate for each video.
    
    Args:
        df (pd.DataFrame): Video data with likes, comments, shares, views
        
    Returns:
        pd.DataFrame: Data with engagement_rate column added
    """
    df = df.copy()
    
    # Avoid division by zero
    df['engagement_rate'] = np.where(
        df['views'] > 0,
        (df['likes'] + df['comments'] + df['shares']) / df['views'],
        0.0
    )
    
    logger.info(f"Calculated engagement rates: min={df['engagement_rate'].min():.4f}, max={df['engagement_rate'].max():.4f}")
    return df


def calculate_performance_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate overall performance score combining views and engagement.
    
    Args:
        df (pd.DataFrame): Video data with views and engagement_rate
        
    Returns:
        pd.DataFrame: Data with performance_score column added
    """
    df = df.copy()
    
    df['performance_score'] = df['views'] * df['engagement_rate']
    
    logger.info(f"Calculated performance scores: min={df['performance_score'].min():.0f}, max={df['performance_score'].max():.0f}")
    return df


def calculate_viral_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate viral impact scores and thresholds.
    
    Args:
        df (pd.DataFrame): Video data with engagement metrics
        
    Returns:
        pd.DataFrame: Data with viral metrics added
    """
    df = df.copy()
    
    # Viral score as percentage (0-100%) using normalized factors
    max_views = df['views'].max() if len(df) > 0 else 1
    max_engagement = df['engagement_rate'].max() if len(df) > 0 else 1
    max_interactions = (df['likes'] + df['comments'] + df['shares']).max() if len(df) > 0 else 1
    
    df['viral_score'] = (
        (df['views'] / max_views) * 40 +  # 40% weight for views
        (df['engagement_rate'] / max_engagement) * 35 +  # 35% weight for engagement rate  
        ((df['likes'] + df['comments'] + df['shares']) / max_interactions) * 25  # 25% weight for interactions
    )
    
    # Views per follower ratio (when follower data available)
    if 'author_followers' in df.columns:
        df['views_per_follower'] = np.where(
            df['author_followers'] > 0,
            df['views'] / df['author_followers'],
            0.0
        )
    
    # Engagement velocity (engagement per second)
    if 'duration' in df.columns:
        df['engagement_velocity'] = np.where(
            df['duration'] > 0,
            df['engagement_rate'] / df['duration'],
            0.0
        )
    
    # Social proof score (weighted engagement)
    df['social_proof_score'] = (
        df['likes'] * 1 + 
        df['comments'] * 2 + 
        df['shares'] * 3
    )
    
    logger.info(f"Calculated viral metrics for {len(df)} videos")
    return df


def determine_viral_threshold(df: pd.DataFrame, percentile: float = 0.8) -> Tuple[pd.DataFrame, float]:
    """
    Determine viral threshold and classify videos.
    
    Args:
        df (pd.DataFrame): Video data with viral metrics
        percentile (float): Percentile for viral threshold (default 80th)
        
    Returns:
        Tuple[pd.DataFrame, float]: Data with viral classification and threshold value
    """
    df = df.copy()
    
    viral_threshold = df['views'].quantile(percentile)
    df['viral_threshold'] = viral_threshold
    df['is_viral'] = df['views'] >= viral_threshold
    
    viral_count = df['is_viral'].sum()
    logger.info(f"Viral threshold set at {viral_threshold:,.0f} views ({viral_count}/{len(df)} videos are viral)")
    
    return df, viral_threshold


def calculate_engagement_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Categorize videos into engagement performance tiers.
    
    Args:
        df (pd.DataFrame): Video data with engagement metrics
        
    Returns:
        pd.DataFrame: Data with tier classifications added
    """
    df = df.copy()
    
    # Engagement rate tiers
    df['engagement_tier'] = pd.qcut(
        df['engagement_rate'], 
        q=4, 
        labels=['Low', 'Medium', 'High', 'Viral'],
        duplicates='drop'
    )
    
    # View count tiers  
    df['view_tier'] = pd.qcut(
        df['views'], 
        q=4, 
        labels=['Low', 'Medium', 'High', 'Viral'],
        duplicates='drop'
    )
    
    logger.info("Calculated engagement and view tiers")
    return df


def get_engagement_summary(df: pd.DataFrame) -> dict:
    """
    Generate engagement metrics summary.
    
    Args:
        df (pd.DataFrame): Video data with engagement metrics
        
    Returns:
        dict: Summary of engagement statistics
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'avg_engagement_rate': float(df['engagement_rate'].mean()),
        'median_engagement_rate': float(df['engagement_rate'].median()),
        'total_views': int(df['views'].sum()),
        'total_likes': int(df['likes'].sum()),
        'total_comments': int(df['comments'].sum()),
        'total_shares': int(df['shares'].sum()),
        'viral_videos': int(df['is_viral'].sum()) if 'is_viral' in df.columns else 0,
        'viral_threshold': float(df['viral_threshold'].iloc[0]) if 'viral_threshold' in df.columns else 0
    }