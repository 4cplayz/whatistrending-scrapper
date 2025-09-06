"""
Analyze individual hook types for viral performance impact.
Single responsibility: Hook-specific performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_individual_hook_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance for each individual hook type.
    
    Args:
        df (pd.DataFrame): Video data with hook features and viral metrics
        
    Returns:
        Dict[str, Any]: Individual hook performance analysis
        
    Raises:
        ValueError: If required columns are missing
    """
    required_cols = ['hooks_list', 'views', 'engagement_rate', 'viral_score']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    hook_performance = {}
    
    # Analyze each individual hook across all videos
    for _, row in df.iterrows():
        hooks = row.get('hooks_list', [])
        if not isinstance(hooks, list):
            continue
            
        for hook in hooks:
            if hook and hook.strip():  # Skip empty hooks
                if hook not in hook_performance:
                    hook_performance[hook] = {
                        'views': [], 
                        'engagement': [], 
                        'viral_scores': [],
                        'video_ids': []
                    }
                
                hook_performance[hook]['views'].append(row['views'])
                hook_performance[hook]['engagement'].append(row['engagement_rate'])
                hook_performance[hook]['viral_scores'].append(row['viral_score'])
                hook_performance[hook]['video_ids'].append(row.get('video_id', ''))
    
    # Calculate performance metrics for each hook
    analyzed_hooks = {}
    viral_threshold = df['views'].quantile(0.8) if 'views' in df.columns else 0
    
    for hook, data in hook_performance.items():
        if len(data['views']) > 0:
            analyzed_hooks[hook] = {
                'avg_views': float(np.mean(data['views'])),
                'avg_engagement': float(np.mean(data['engagement'])),
                'viral_impact_score': float(np.mean(data['viral_scores'])),
                'usage_count': len(data['views']),
                'max_views_achieved': int(max(data['views'])),
                'viral_videos': len([v for v in data['views'] if v >= viral_threshold]),
                'viral_success_rate': float(len([v for v in data['views'] if v >= viral_threshold]) / len(data['views'])),
                'performance_tier': _classify_hook_performance(np.mean(data['views']), np.mean(data['engagement']))
            }
    
    logger.info(f"Analyzed {len(analyzed_hooks)} individual hook types")
    return analyzed_hooks


def analyze_hook_combinations(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze performance of videos with multiple hooks.
    
    Args:
        df (pd.DataFrame): Video data with hook count and performance metrics
        
    Returns:
        Dict[str, Any]: Multi-hook combination analysis
    """
    if 'hook_count' not in df.columns:
        logger.warning("hook_count column missing - cannot analyze combinations")
        return {}
    
    combination_analysis = {}
    
    # Analyze by hook count
    for hook_count in df['hook_count'].unique():
        if pd.isna(hook_count) or hook_count == 0:
            continue
            
        hook_data = df[df['hook_count'] == hook_count]
        if len(hook_data) == 0:
            continue
            
        combination_analysis[f"hooks_{int(hook_count)}"] = {
            'avg_views': float(hook_data['views'].mean()),
            'avg_engagement': float(hook_data['engagement_rate'].mean()),
            'viral_impact_score': float(hook_data['viral_score'].mean()),
            'video_count': len(hook_data),
            'viral_success_rate': float((hook_data['views'] >= df['views'].quantile(0.8)).mean())
        }
    
    # Compare single vs multi-hook performance
    if 'multi_hook_video' in df.columns:
        single_hook = df[df['multi_hook_video'] == False]
        multi_hook = df[df['multi_hook_video'] == True]
        
        if len(single_hook) > 0 and len(multi_hook) > 0:
            combination_analysis['comparison'] = {
                'single_hook_avg_views': float(single_hook['views'].mean()),
                'multi_hook_avg_views': float(multi_hook['views'].mean()),
                'multi_hook_advantage': float(multi_hook['views'].mean() / single_hook['views'].mean())
            }
    
    logger.info(f"Analyzed hook combinations: {len(combination_analysis)} patterns found")
    return combination_analysis


def get_top_performing_hooks(hook_analysis: Dict[str, Any], top_n: int = 5) -> Dict[str, Any]:
    """
    Get top performing hooks by different metrics.
    
    Args:
        hook_analysis (Dict[str, Any]): Individual hook performance analysis
        top_n (int): Number of top performers to return
        
    Returns:
        Dict[str, Any]: Top performers by different metrics
    """
    if not hook_analysis:
        return {}
    
    # Sort by different metrics
    by_views = sorted(hook_analysis.items(), key=lambda x: x[1]['avg_views'], reverse=True)
    by_engagement = sorted(hook_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)
    by_viral_rate = sorted(hook_analysis.items(), key=lambda x: x[1]['viral_success_rate'], reverse=True)
    by_usage = sorted(hook_analysis.items(), key=lambda x: x[1]['usage_count'], reverse=True)
    
    return {
        'top_by_views': [(hook, data['avg_views']) for hook, data in by_views[:top_n]],
        'top_by_engagement': [(hook, data['avg_engagement']) for hook, data in by_engagement[:top_n]],
        'top_by_viral_rate': [(hook, data['viral_success_rate']) for hook, data in by_viral_rate[:top_n]],
        'most_used': [(hook, data['usage_count']) for hook, data in by_usage[:top_n]]
    }


def _classify_hook_performance(avg_views: float, avg_engagement: float) -> str:
    """
    Classify hook performance into tiers.
    
    Args:
        avg_views (float): Average views for the hook
        avg_engagement (float): Average engagement rate for the hook
        
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


def get_hook_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of hook analysis results.
    
    Args:
        df (pd.DataFrame): Video data with hook features
        
    Returns:
        Dict[str, Any]: Hook analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'videos_with_hooks': df['hook_type'].notna().sum() if 'hook_type' in df.columns else 0,
        'unique_hook_types': df['hook_type'].nunique() if 'hook_type' in df.columns else 0,
        'multi_hook_videos': df['multi_hook_video'].sum() if 'multi_hook_video' in df.columns else 0,
        'avg_hooks_per_video': df['hook_count'].mean() if 'hook_count' in df.columns else 0,
        'max_hooks_in_video': df['hook_count'].max() if 'hook_count' in df.columns else 0
    }