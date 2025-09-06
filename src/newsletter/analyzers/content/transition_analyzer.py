"""
Analyze individual transition types for viral performance impact.
Single responsibility: Transition-specific performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_individual_transition_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance for each individual transition type.
    
    Args:
        df (pd.DataFrame): Video data with transition features and viral metrics
        
    Returns:
        Dict[str, Any]: Individual transition performance analysis
        
    Raises:
        ValueError: If required columns are missing
    """
    required_cols = ['transitions_list', 'views', 'engagement_rate', 'viral_score']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    transition_performance = {}
    
    # Analyze each individual transition across all videos
    for _, row in df.iterrows():
        transitions = row.get('transitions_list', [])
        if not isinstance(transitions, list):
            continue
            
        for transition in transitions:
            if transition and transition.strip():  # Skip empty transitions
                if transition not in transition_performance:
                    transition_performance[transition] = {
                        'views': [], 
                        'engagement': [], 
                        'viral_scores': [],
                        'video_ids': []
                    }
                
                transition_performance[transition]['views'].append(row['views'])
                transition_performance[transition]['engagement'].append(row['engagement_rate'])
                transition_performance[transition]['viral_scores'].append(row['viral_score'])
                transition_performance[transition]['video_ids'].append(row.get('video_id', ''))
    
    # Calculate performance metrics for each transition
    analyzed_transitions = {}
    viral_threshold = df['views'].quantile(0.8) if 'views' in df.columns else 0
    
    for transition, data in transition_performance.items():
        if len(data['views']) > 0:
            analyzed_transitions[transition] = {
                'avg_views': float(np.mean(data['views'])),
                'avg_engagement': float(np.mean(data['engagement'])),
                'viral_impact_score': float(np.mean(data['viral_scores'])),
                'usage_count': len(data['views']),
                'max_views_achieved': int(max(data['views'])),
                'viral_videos': len([v for v in data['views'] if v >= viral_threshold]),
                'viral_success_rate': float(len([v for v in data['views'] if v >= viral_threshold]) / len(data['views'])),
                'performance_tier': _classify_transition_performance(np.mean(data['views']), np.mean(data['engagement']))
            }
    
    logger.info(f"Analyzed {len(analyzed_transitions)} individual transition types")
    return analyzed_transitions


def analyze_transition_timing_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze transition performance by video timing characteristics.
    
    Args:
        df (pd.DataFrame): Video data with transition and duration data
        
    Returns:
        Dict[str, Any]: Transition timing pattern analysis
    """
    if 'duration' not in df.columns or 'transitions_list' not in df.columns:
        logger.warning("Duration or transitions_list missing - cannot analyze timing patterns")
        return {}
    
    timing_analysis = {}
    
    # Analyze by video duration categories
    if 'duration' in df.columns:
        df['duration_category'] = pd.cut(
            df['duration'], 
            bins=[0, 10, 15, 20, 30, float('inf')],
            labels=['Very_Short', 'Short', 'Medium', 'Long', 'Extended']
        )
        
        for category in df['duration_category'].dropna().unique():
            category_data = df[df['duration_category'] == category]
            if len(category_data) == 0:
                continue
                
            # Count transition usage in this duration category
            all_transitions_in_category = []
            for transitions in category_data['transitions_list']:
                if isinstance(transitions, list):
                    all_transitions_in_category.extend(transitions)
            
            if all_transitions_in_category:
                transition_counts = pd.Series(all_transitions_in_category).value_counts()
                timing_analysis[f"duration_{category}"] = {
                    'video_count': len(category_data),
                    'avg_views': float(category_data['views'].mean()),
                    'avg_engagement': float(category_data['engagement_rate'].mean()),
                    'top_transitions': transition_counts.head(3).to_dict(),
                    'avg_transition_count': float(category_data['transition_count'].mean()) if 'transition_count' in category_data.columns else 0
                }
    
    logger.info(f"Analyzed transition timing patterns: {len(timing_analysis)} duration categories")
    return timing_analysis


def analyze_edit_style_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze performance by overall edit style.
    
    Args:
        df (pd.DataFrame): Video data with edit_style column
        
    Returns:
        Dict[str, Any]: Edit style performance analysis
    """
    if 'edit_style' not in df.columns:
        logger.warning("edit_style column missing")
        return {}
    
    style_performance = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for style in df['edit_style'].dropna().unique():
        style_data = df[df['edit_style'] == style]
        if len(style_data) == 0:
            continue
            
        style_performance[style] = {
            'avg_views': float(style_data['views'].mean()),
            'avg_engagement': float(style_data['engagement_rate'].mean()),
            'viral_impact_score': float(style_data['viral_score'].mean()),
            'video_count': len(style_data),
            'max_views': int(style_data['views'].max()),
            'viral_videos': int((style_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((style_data['views'] >= viral_threshold).mean())
        }
    
    logger.info(f"Analyzed {len(style_performance)} edit styles")
    return style_performance


def get_top_performing_transitions(transition_analysis: Dict[str, Any], top_n: int = 5) -> Dict[str, Any]:
    """
    Get top performing transitions by different metrics.
    
    Args:
        transition_analysis (Dict[str, Any]): Individual transition performance analysis
        top_n (int): Number of top performers to return
        
    Returns:
        Dict[str, Any]: Top performers by different metrics
    """
    if not transition_analysis:
        return {}
    
    # Sort by different metrics
    by_views = sorted(transition_analysis.items(), key=lambda x: x[1]['avg_views'], reverse=True)
    by_engagement = sorted(transition_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)
    by_viral_rate = sorted(transition_analysis.items(), key=lambda x: x[1]['viral_success_rate'], reverse=True)
    by_usage = sorted(transition_analysis.items(), key=lambda x: x[1]['usage_count'], reverse=True)
    
    return {
        'top_by_views': [(transition, data['avg_views']) for transition, data in by_views[:top_n]],
        'top_by_engagement': [(transition, data['avg_engagement']) for transition, data in by_engagement[:top_n]],
        'top_by_viral_rate': [(transition, data['viral_success_rate']) for transition, data in by_viral_rate[:top_n]],
        'most_used': [(transition, data['usage_count']) for transition, data in by_usage[:top_n]]
    }


def _classify_transition_performance(avg_views: float, avg_engagement: float) -> str:
    """
    Classify transition performance into tiers.
    
    Args:
        avg_views (float): Average views for the transition
        avg_engagement (float): Average engagement rate for the transition
        
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


def get_transition_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of transition analysis results.
    
    Args:
        df (pd.DataFrame): Video data with transition features
        
    Returns:
        Dict[str, Any]: Transition analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'videos_with_transitions': df['transition_type'].notna().sum() if 'transition_type' in df.columns else 0,
        'unique_transition_types': df['transition_type'].nunique() if 'transition_type' in df.columns else 0,
        'avg_transitions_per_video': df['transition_count'].mean() if 'transition_count' in df.columns else 0,
        'max_transitions_in_video': df['transition_count'].max() if 'transition_count' in df.columns else 0,
        'unique_edit_styles': df['edit_style'].nunique() if 'edit_style' in df.columns else 0
    }