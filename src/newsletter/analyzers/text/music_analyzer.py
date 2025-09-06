"""
Analyze music tracks for viral performance impact.
Single responsibility: Music-specific performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_individual_music_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance for each individual music track.
    
    Args:
        df (pd.DataFrame): Video data with music and viral metrics
        
    Returns:
        Dict[str, Any]: Individual music track performance analysis
    """
    if 'music_title' not in df.columns:
        logger.warning("music_title column missing")
        return {}
    
    music_performance = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for music_title in df['music_title'].dropna().unique():
        music_data = df[df['music_title'] == music_title]
        if len(music_data) == 0:
            continue
            
        music_performance[music_title] = {
            'avg_views': float(music_data['views'].mean()),
            'avg_engagement': float(music_data['engagement_rate'].mean()),
            'total_views': int(music_data['views'].sum()),
            'viral_impact_score': float(music_data['viral_score'].mean()),
            'usage_count': len(music_data),
            'max_views': int(music_data['views'].max()),
            'viral_videos': int((music_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((music_data['views'] >= viral_threshold).mean()),
            'music_author': music_data['music_author'].iloc[0] if 'music_author' in music_data.columns else 'Unknown',
            'music_type': _classify_music_type(music_title),
            'performance_tier': _classify_music_performance(music_data['views'].mean(), music_data['engagement_rate'].mean())
        }
    
    logger.info(f"Analyzed {len(music_performance)} individual music tracks")
    return music_performance


def analyze_original_vs_licensed_music(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze performance difference between original sounds and licensed music.
    
    Args:
        df (pd.DataFrame): Video data with music type classification
        
    Returns:
        Dict[str, Any]: Original vs licensed music analysis
    """
    if 'music_type' not in df.columns:
        logger.warning("music_type column missing")
        return {}
    
    music_type_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for music_type in df['music_type'].dropna().unique():
        type_data = df[df['music_type'] == music_type]
        if len(type_data) == 0:
            continue
            
        music_type_analysis[music_type] = {
            'video_count': len(type_data),
            'avg_views': float(type_data['views'].mean()),
            'avg_engagement': float(type_data['engagement_rate'].mean()),
            'viral_impact_score': float(type_data['viral_score'].mean()),
            'viral_videos': int((type_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((type_data['views'] >= viral_threshold).mean()),
            'unique_tracks': type_data['music_title'].nunique() if 'music_title' in type_data.columns else 0
        }
    
    # Calculate advantage of one type over another
    if 'Original' in music_type_analysis and 'Licensed' in music_type_analysis:
        original = music_type_analysis['Original']
        licensed = music_type_analysis['Licensed']
        
        music_type_analysis['type_comparison'] = {
            'original_advantage': float(original['avg_views'] / licensed['avg_views']) if licensed['avg_views'] > 0 else 0,
            'engagement_difference': float(original['avg_engagement'] - licensed['avg_engagement']),
            'viral_rate_difference': float(original['viral_success_rate'] - licensed['viral_success_rate'])
        }
    
    logger.info(f"Analyzed music type performance: {len(music_type_analysis)} types")
    return music_type_analysis


def analyze_music_author_performance(df: pd.DataFrame, min_tracks: int = 2) -> Dict[str, Any]:
    """
    Analyze performance of music authors/artists with multiple tracks.
    
    Args:
        df (pd.DataFrame): Video data with music author information
        min_tracks (int): Minimum tracks required to include author
        
    Returns:
        Dict[str, Any]: Music author performance analysis
    """
    if 'music_author' not in df.columns:
        logger.warning("music_author column missing")
        return {}
    
    author_performance = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Group by music author
    author_groups = df.groupby('music_author')
    
    for author, author_data in author_groups:
        if len(author_data) < min_tracks or pd.isna(author):
            continue
            
        author_performance[author] = {
            'track_count': len(author_data),
            'unique_tracks': author_data['music_title'].nunique(),
            'avg_views': float(author_data['views'].mean()),
            'avg_engagement': float(author_data['engagement_rate'].mean()),
            'total_views': int(author_data['views'].sum()),
            'viral_impact_score': float(author_data['viral_score'].mean()),
            'viral_videos': int((author_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((author_data['views'] >= viral_threshold).mean()),
            'best_track_views': int(author_data['views'].max()),
            'consistency_score': float(1 - (author_data['views'].std() / author_data['views'].mean())) if author_data['views'].mean() > 0 else 0
        }
    
    logger.info(f"Analyzed {len(author_performance)} music authors with {min_tracks}+ tracks")
    return author_performance


def analyze_music_car_brand_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze correlation between music choices and car brands featured.
    
    Args:
        df (pd.DataFrame): Video data with music and car brand information
        
    Returns:
        Dict[str, Any]: Music-car brand correlation analysis
    """
    if 'music_title' not in df.columns or 'car_brand' not in df.columns:
        logger.warning("Missing music_title or car_brand columns")
        return {}
    
    correlation_analysis = {}
    
    # Find music tracks that frequently pair with specific car brands
    music_brand_pairs = df.groupby(['music_title', 'car_brand']).agg({
        'views': ['mean', 'count'],
        'engagement_rate': 'mean'
    }).round(2)
    
    # Flatten column names
    music_brand_pairs.columns = ['avg_views', 'video_count', 'avg_engagement']
    music_brand_pairs = music_brand_pairs.reset_index()
    
    # Filter pairs with multiple occurrences
    frequent_pairs = music_brand_pairs[music_brand_pairs['video_count'] >= 2]
    
    if len(frequent_pairs) > 0:
        correlation_analysis['successful_combinations'] = {}
        
        # Sort by performance
        top_combinations = frequent_pairs.nlargest(10, 'avg_views')
        
        for _, row in top_combinations.iterrows():
            combo_key = f"{row['music_title']} × {row['car_brand']}"
            correlation_analysis['successful_combinations'][combo_key] = {
                'avg_views': float(row['avg_views']),
                'avg_engagement': float(row['avg_engagement']),
                'usage_count': int(row['video_count'])
            }
    
    # Analyze genre preferences by car brand
    if 'car_brand' in df.columns:
        correlation_analysis['brand_music_preferences'] = {}
        
        for brand in df['car_brand'].dropna().unique()[:10]:  # Top 10 brands
            brand_data = df[df['car_brand'] == brand]
            if len(brand_data) > 0:
                top_music = brand_data['music_title'].value_counts().head(5)
                correlation_analysis['brand_music_preferences'][brand] = {
                    'top_tracks': top_music.to_dict(),
                    'original_sound_rate': float((brand_data['music_type'] == 'Original').mean()) if 'music_type' in brand_data.columns else 0
                }
    
    logger.info("Analyzed music-car brand correlations")
    return correlation_analysis


def get_top_performing_music(music_analysis: Dict[str, Any], top_n: int = 15) -> Dict[str, Any]:
    """
    Get top performing music tracks by different metrics.
    
    Args:
        music_analysis (Dict[str, Any]): Individual music performance analysis
        top_n (int): Number of top performers to return
        
    Returns:
        Dict[str, Any]: Top performers by different metrics
    """
    if not music_analysis:
        return {}
    
    # Sort by different metrics
    by_views = sorted(music_analysis.items(), key=lambda x: x[1]['avg_views'], reverse=True)
    by_total_views = sorted(music_analysis.items(), key=lambda x: x[1]['total_views'], reverse=True)
    by_viral_rate = sorted(music_analysis.items(), key=lambda x: x[1]['viral_success_rate'], reverse=True)
    by_usage = sorted(music_analysis.items(), key=lambda x: x[1]['usage_count'], reverse=True)
    
    return {
        'top_by_avg_views': [(track, data['avg_views']) for track, data in by_views[:top_n]],
        'top_by_total_views': [(track, data['total_views']) for track, data in by_total_views[:top_n]],
        'top_by_viral_rate': [(track, data['viral_success_rate']) for track, data in by_viral_rate[:top_n]],
        'most_used': [(track, data['usage_count']) for track, data in by_usage[:top_n]]
    }


def _classify_music_type(music_title: str) -> str:
    """
    Classify music as original sound or licensed.
    
    Args:
        music_title (str): Music track title
        
    Returns:
        str: Music type classification
    """
    if pd.isna(music_title):
        return 'Unknown'
    
    title_lower = str(music_title).lower()
    if 'original sound' in title_lower:
        return 'Original'
    else:
        return 'Licensed'


def _classify_music_performance(avg_views: float, avg_engagement: float) -> str:
    """
    Classify music track performance into tiers.
    
    Args:
        avg_views (float): Average views for the track
        avg_engagement (float): Average engagement rate for the track
        
    Returns:
        str: Performance tier classification
    """
    if avg_views > 100000 and avg_engagement > 0.15:
        return "Viral"
    elif avg_views > 50000 and avg_engagement > 0.12:
        return "High"  
    elif avg_views > 20000 and avg_engagement > 0.08:
        return "Medium"
    else:
        return "Low"


def get_music_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of music analysis results.
    
    Args:
        df (pd.DataFrame): Video data with music features
        
    Returns:
        Dict[str, Any]: Music analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'unique_music_tracks': df['music_title'].nunique() if 'music_title' in df.columns else 0,
        'unique_music_authors': df['music_author'].nunique() if 'music_author' in df.columns else 0,
        'original_sound_videos': int((df['music_type'] == 'Original').sum()) if 'music_type' in df.columns else 0,
        'licensed_music_videos': int((df['music_type'] == 'Licensed').sum()) if 'music_type' in df.columns else 0,
        'most_popular_track': df['music_title'].mode().iloc[0] if 'music_title' in df.columns and len(df['music_title'].mode()) > 0 else None
    }