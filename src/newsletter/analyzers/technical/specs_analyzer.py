"""
Analyze video technical specifications for viral performance impact.
Single responsibility: Technical specs performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_duration_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance by video duration.
    
    Args:
        df (pd.DataFrame): Video data with duration and viral metrics
        
    Returns:
        Dict[str, Any]: Duration performance analysis
        
    Raises:
        ValueError: If required columns are missing
    """
    if 'duration' not in df.columns:
        raise ValueError("duration column is required")
    
    duration_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Create duration categories
    df['duration_category'] = pd.cut(
        df['duration'], 
        bins=[0, 10, 15, 20, 30, float('inf')],
        labels=['Very_Short', 'Short', 'Medium', 'Long', 'Extended']
    )
    
    # Analyze each duration category
    for category in df['duration_category'].dropna().unique():
        category_data = df[df['duration_category'] == category]
        if len(category_data) == 0:
            continue
            
        duration_analysis[category] = {
            'avg_views': float(category_data['views'].mean()),
            'avg_engagement': float(category_data['engagement_rate'].mean()),
            'viral_impact_score': float(category_data['viral_score'].mean()),
            'video_count': len(category_data),
            'viral_videos': int((category_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((category_data['views'] >= viral_threshold).mean()),
            'avg_duration': float(category_data['duration'].mean()),
            'duration_range': (float(category_data['duration'].min()), float(category_data['duration'].max()))
        }
    
    # Find optimal duration
    if duration_analysis:
        best_category = max(duration_analysis.items(), key=lambda x: x[1]['avg_views'])
        duration_analysis['optimal_duration'] = {
            'category': best_category[0],
            'avg_views': best_category[1]['avg_views'],
            'avg_duration': best_category[1]['avg_duration']
        }
    
    logger.info(f"Analyzed duration performance: {len(duration_analysis)} categories")
    return duration_analysis


def analyze_resolution_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance by video resolution.
    
    Args:
        df (pd.DataFrame): Video data with width, height, and viral metrics
        
    Returns:
        Dict[str, Any]: Resolution performance analysis
    """
    if 'width' not in df.columns or 'height' not in df.columns:
        logger.warning("width or height columns missing")
        return {}
    
    resolution_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Create resolution categories
    df['video_resolution'] = df['width'].astype(str) + 'x' + df['height'].astype(str)
    
    # Analyze each resolution
    for resolution in df['video_resolution'].value_counts().head(10).index:  # Top 10 resolutions
        resolution_data = df[df['video_resolution'] == resolution]
        if len(resolution_data) == 0:
            continue
            
        resolution_analysis[resolution] = {
            'avg_views': float(resolution_data['views'].mean()),
            'avg_engagement': float(resolution_data['engagement_rate'].mean()),
            'viral_impact_score': float(resolution_data['viral_score'].mean()),
            'video_count': len(resolution_data),
            'viral_success_rate': float((resolution_data['views'] >= viral_threshold).mean()),
            'aspect_ratio': float(resolution_data['width'].iloc[0] / resolution_data['height'].iloc[0])
        }
    
    logger.info(f"Analyzed resolution performance: {len(resolution_analysis)} resolutions")
    return resolution_analysis


def analyze_aspect_ratio_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance by video aspect ratio.
    
    Args:
        df (pd.DataFrame): Video data with aspect ratio and viral metrics
        
    Returns:
        Dict[str, Any]: Aspect ratio performance analysis
    """
    if 'width' not in df.columns or 'height' not in df.columns:
        logger.warning("width or height columns missing")
        return {}
    
    aspect_ratio_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Calculate aspect ratios
    df['aspect_ratio'] = df['width'] / df['height']
    df['is_square'] = (df['aspect_ratio'] == 1.0)
    df['is_vertical'] = (df['aspect_ratio'] < 1.0)
    df['is_horizontal'] = (df['aspect_ratio'] > 1.0)
    
    # Categorize aspect ratios
    aspect_categories = {
        'square': df['is_square'],
        'vertical': df['is_vertical'], 
        'horizontal': df['is_horizontal']
    }
    
    for category, mask in aspect_categories.items():
        category_data = df[mask]
        if len(category_data) == 0:
            continue
            
        aspect_ratio_analysis[category] = {
            'avg_views': float(category_data['views'].mean()),
            'avg_engagement': float(category_data['engagement_rate'].mean()),
            'viral_impact_score': float(category_data['viral_score'].mean()),
            'video_count': len(category_data),
            'viral_success_rate': float((category_data['views'] >= viral_threshold).mean()),
            'avg_aspect_ratio': float(category_data['aspect_ratio'].mean())
        }
    
    logger.info(f"Analyzed aspect ratio performance: {len(aspect_ratio_analysis)} categories")
    return aspect_ratio_analysis


def analyze_video_quality_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze correlation between video quality and performance.
    
    Args:
        df (pd.DataFrame): Video data with quality metrics
        
    Returns:
        Dict[str, Any]: Video quality correlation analysis
    """
    quality_analysis = {}
    
    # Analyze resolution vs performance correlation
    if 'width' in df.columns and 'height' in df.columns:
        df['total_pixels'] = df['width'] * df['height']
        
        # Calculate correlation between resolution and views
        resolution_corr = df['total_pixels'].corr(df['views'])
        quality_analysis['resolution_views_correlation'] = float(resolution_corr)
        
        # Categorize by resolution quality
        df['resolution_tier'] = pd.qcut(
            df['total_pixels'], 
            q=4, 
            labels=['Low', 'Medium', 'High', 'Ultra'],
            duplicates='drop'
        )
        
        quality_analysis['by_resolution_tier'] = {}
        for tier in df['resolution_tier'].dropna().unique():
            tier_data = df[df['resolution_tier'] == tier]
            if len(tier_data) > 0:
                quality_analysis['by_resolution_tier'][tier] = {
                    'avg_views': float(tier_data['views'].mean()),
                    'avg_engagement': float(tier_data['engagement_rate'].mean()),
                    'video_count': len(tier_data),
                    'avg_pixels': int(tier_data['total_pixels'].mean())
                }
    
    # Analyze duration consistency
    if 'duration' in df.columns:
        # Videos with "standard" durations might perform differently
        df['is_standard_duration'] = df['duration'].isin([15, 30, 60])  # Common TikTok durations
        
        standard_duration = df[df['is_standard_duration']]
        custom_duration = df[~df['is_standard_duration']]
        
        if len(standard_duration) > 0 and len(custom_duration) > 0:
            quality_analysis['duration_standardization'] = {
                'standard_duration': {
                    'avg_views': float(standard_duration['views'].mean()),
                    'video_count': len(standard_duration)
                },
                'custom_duration': {
                    'avg_views': float(custom_duration['views'].mean()),
                    'video_count': len(custom_duration)
                }
            }
    
    logger.info("Analyzed video quality correlations")
    return quality_analysis


def get_optimal_video_specs(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Determine optimal video specifications based on performance data.
    
    Args:
        df (pd.DataFrame): Video data with technical specifications
        
    Returns:
        Dict[str, Any]: Optimal video specifications recommendations
    """
    if df.empty:
        return {'status': 'no_data'}
    
    optimal_specs = {}
    
    # Find optimal duration
    if 'duration' in df.columns:
        high_performers = df[df['views'] >= df['views'].quantile(0.8)]
        optimal_specs['duration'] = {
            'optimal_range': (float(high_performers['duration'].quantile(0.25)), 
                            float(high_performers['duration'].quantile(0.75))),
            'average_optimal': float(high_performers['duration'].mean()),
            'median_optimal': float(high_performers['duration'].median())
        }
    
    # Find optimal aspect ratio
    if 'width' in df.columns and 'height' in df.columns:
        df['aspect_ratio'] = df['width'] / df['height']
        high_performers = df[df['views'] >= df['views'].quantile(0.8)]
        
        optimal_specs['aspect_ratio'] = {
            'optimal_average': float(high_performers['aspect_ratio'].mean()),
            'optimal_median': float(high_performers['aspect_ratio'].median()),
            'vertical_performance': float(df[df['aspect_ratio'] < 1.0]['views'].mean()) if len(df[df['aspect_ratio'] < 1.0]) > 0 else 0,
            'square_performance': float(df[df['aspect_ratio'] == 1.0]['views'].mean()) if len(df[df['aspect_ratio'] == 1.0]) > 0 else 0,
            'horizontal_performance': float(df[df['aspect_ratio'] > 1.0]['views'].mean()) if len(df[df['aspect_ratio'] > 1.0]) > 0 else 0
        }
    
    # Find optimal resolution
    if 'width' in df.columns and 'height' in df.columns:
        high_performers = df[df['views'] >= df['views'].quantile(0.8)]
        most_common_res = high_performers.groupby(['width', 'height']).size().idxmax()
        
        optimal_specs['resolution'] = {
            'most_successful_resolution': f"{most_common_res[0]}x{most_common_res[1]}",
            'avg_width': float(high_performers['width'].mean()),
            'avg_height': float(high_performers['height'].mean())
        }
    
    logger.info("Determined optimal video specifications")
    return optimal_specs


def get_specs_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of technical specifications analysis.
    
    Args:
        df (pd.DataFrame): Video data with technical specs
        
    Returns:
        Dict[str, Any]: Technical specs analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'duration_range': (float(df['duration'].min()), float(df['duration'].max())) if 'duration' in df.columns else (0, 0),
        'avg_duration': float(df['duration'].mean()) if 'duration' in df.columns else 0,
        'unique_resolutions': len(df[['width', 'height']].drop_duplicates()) if 'width' in df.columns and 'height' in df.columns else 0,
        'most_common_resolution': df.groupby(['width', 'height']).size().idxmax() if 'width' in df.columns and 'height' in df.columns else None,
        'vertical_videos': int((df['width'] < df['height']).sum()) if 'width' in df.columns and 'height' in df.columns else 0,
        'square_videos': int((df['width'] == df['height']).sum()) if 'width' in df.columns and 'height' in df.columns else 0
    }