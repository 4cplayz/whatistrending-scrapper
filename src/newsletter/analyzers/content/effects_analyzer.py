"""
Analyze individual visual effects for viral performance impact.
Single responsibility: Effects-specific performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_individual_effects_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance for each individual visual effect.
    
    Args:
        df (pd.DataFrame): Video data with effects features and viral metrics
        
    Returns:
        Dict[str, Any]: Individual effects performance analysis
        
    Raises:
        ValueError: If required columns are missing
    """
    required_cols = ['effects_list', 'views', 'engagement_rate', 'viral_score']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    effects_performance = {}
    
    # Analyze each individual effect across all videos
    for _, row in df.iterrows():
        effects = row.get('effects_list', [])
        if not isinstance(effects, list):
            continue
            
        for effect in effects:
            if effect and effect.strip():  # Skip empty effects
                if effect not in effects_performance:
                    effects_performance[effect] = {
                        'views': [], 
                        'engagement': [], 
                        'viral_scores': [],
                        'video_ids': []
                    }
                
                effects_performance[effect]['views'].append(row['views'])
                effects_performance[effect]['engagement'].append(row['engagement_rate'])
                effects_performance[effect]['viral_scores'].append(row['viral_score'])
                effects_performance[effect]['video_ids'].append(row.get('video_id', ''))
    
    # Calculate performance metrics for each effect
    analyzed_effects = {}
    viral_threshold = df['views'].quantile(0.8) if 'views' in df.columns else 0
    
    for effect, data in effects_performance.items():
        if len(data['views']) > 0:
            analyzed_effects[effect] = {
                'avg_views': float(np.mean(data['views'])),
                'avg_engagement': float(np.mean(data['engagement'])),
                'viral_impact_score': float(np.mean(data['viral_scores'])),
                'usage_count': len(data['views']),
                'max_views_achieved': int(max(data['views'])),
                'viral_videos': len([v for v in data['views'] if v >= viral_threshold]),
                'viral_success_rate': float(len([v for v in data['views'] if v >= viral_threshold]) / len(data['views'])),
                'performance_tier': _classify_effect_performance(np.mean(data['views']), np.mean(data['engagement'])),
                'effect_category': _categorize_effect_type(effect)
            }
    
    logger.info(f"Analyzed {len(analyzed_effects)} individual visual effects")
    return analyzed_effects


def analyze_effects_by_category(effects_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Group effects analysis by effect category.
    
    Args:
        effects_analysis (Dict[str, Any]): Individual effects performance data
        
    Returns:
        Dict[str, Any]: Effects grouped by category with aggregate performance
    """
    categories = {}
    
    for effect, data in effects_analysis.items():
        category = data.get('effect_category', 'Other')
        
        if category not in categories:
            categories[category] = {
                'effects': [],
                'total_usage': 0,
                'avg_views': [],
                'avg_engagement': [],
                'viral_scores': []
            }
        
        categories[category]['effects'].append(effect)
        categories[category]['total_usage'] += data['usage_count']
        categories[category]['avg_views'].append(data['avg_views'])
        categories[category]['avg_engagement'].append(data['avg_engagement'])
        categories[category]['viral_scores'].append(data['viral_impact_score'])
    
    # Calculate category aggregates
    category_performance = {}
    for category, data in categories.items():
        if data['avg_views']:
            category_performance[category] = {
                'effect_count': len(data['effects']),
                'total_usage': data['total_usage'],
                'avg_views': float(np.mean(data['avg_views'])),
                'avg_engagement': float(np.mean(data['avg_engagement'])),
                'avg_viral_score': float(np.mean(data['viral_scores'])),
                'top_effects': sorted(data['effects'], key=lambda x: effects_analysis[x]['avg_views'], reverse=True)[:3]
            }
    
    logger.info(f"Grouped effects into {len(category_performance)} categories")
    return category_performance


def analyze_effects_combinations(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze performance of videos with multiple effects.
    
    Args:
        df (pd.DataFrame): Video data with effects count and performance metrics
        
    Returns:
        Dict[str, Any]: Multi-effects combination analysis
    """
    if 'effects_count' not in df.columns:
        logger.warning("effects_count column missing - cannot analyze combinations")
        return {}
    
    combination_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Analyze by effects count
    for effects_count in df['effects_count'].unique():
        if pd.isna(effects_count) or effects_count == 0:
            continue
            
        effects_data = df[df['effects_count'] == effects_count]
        if len(effects_data) == 0:
            continue
            
        combination_analysis[f"effects_{int(effects_count)}"] = {
            'avg_views': float(effects_data['views'].mean()),
            'avg_engagement': float(effects_data['engagement_rate'].mean()),
            'viral_impact_score': float(effects_data['viral_score'].mean()),
            'video_count': len(effects_data),
            'viral_success_rate': float((effects_data['views'] >= viral_threshold).mean()),
            'complexity_tier': _classify_effects_complexity(int(effects_count))
        }
    
    # Analyze optimal effects count
    if len(combination_analysis) > 1:
        best_count = max(combination_analysis.items(), key=lambda x: x[1]['avg_views'])
        combination_analysis['optimal_effects_count'] = {
            'count': int(best_count[0].split('_')[1]),
            'avg_views': best_count[1]['avg_views'],
            'performance_advantage': f"{((best_count[1]['avg_views'] / min(x[1]['avg_views'] for x in combination_analysis.items() if x[0] != 'optimal_effects_count')) - 1) * 100:.1f}%"
        }
    
    logger.info(f"Analyzed effects combinations: {len(combination_analysis)} patterns found")
    return combination_analysis


def get_top_performing_effects(effects_analysis: Dict[str, Any], top_n: int = 5) -> Dict[str, Any]:
    """
    Get top performing effects by different metrics.
    
    Args:
        effects_analysis (Dict[str, Any]): Individual effects performance analysis
        top_n (int): Number of top performers to return
        
    Returns:
        Dict[str, Any]: Top performers by different metrics
    """
    if not effects_analysis:
        return {}
    
    # Sort by different metrics
    by_views = sorted(effects_analysis.items(), key=lambda x: x[1]['avg_views'], reverse=True)
    by_engagement = sorted(effects_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)
    by_viral_rate = sorted(effects_analysis.items(), key=lambda x: x[1]['viral_success_rate'], reverse=True)
    by_usage = sorted(effects_analysis.items(), key=lambda x: x[1]['usage_count'], reverse=True)
    
    return {
        'top_by_views': [(effect, data['avg_views']) for effect, data in by_views[:top_n]],
        'top_by_engagement': [(effect, data['avg_engagement']) for effect, data in by_engagement[:top_n]],
        'top_by_viral_rate': [(effect, data['viral_success_rate']) for effect, data in by_viral_rate[:top_n]],
        'most_used': [(effect, data['usage_count']) for effect, data in by_usage[:top_n]]
    }


def _categorize_effect_type(effect: str) -> str:
    """
    Categorize effect into logical groups.
    
    Args:
        effect (str): Effect name
        
    Returns:
        str: Effect category
    """
    effect_lower = effect.lower()
    
    if any(word in effect_lower for word in ['slow', 'motion', 'speed', 'time']):
        return "Temporal"
    elif any(word in effect_lower for word in ['zoom', 'pan', 'tilt', 'rotate']):
        return "Camera_Movement"
    elif any(word in effect_lower for word in ['blur', 'focus', 'depth', 'bokeh']):
        return "Focus_Effects"
    elif any(word in effect_lower for word in ['color', 'grade', 'filter', 'tone']):
        return "Color_Grading"
    elif any(word in effect_lower for word in ['transition', 'cut', 'fade', 'wipe']):
        return "Transitions"
    elif any(word in effect_lower for word in ['text', 'graphic', 'overlay', 'title']):
        return "Graphics"
    else:
        return "Other"


def _classify_effect_performance(avg_views: float, avg_engagement: float) -> str:
    """
    Classify effect performance into tiers.
    
    Args:
        avg_views (float): Average views for the effect
        avg_engagement (float): Average engagement rate for the effect
        
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


def _classify_effects_complexity(effects_count: int) -> str:
    """
    Classify video effects complexity based on count.
    
    Args:
        effects_count (int): Number of effects in video
        
    Returns:
        str: Complexity tier
    """
    if effects_count >= 5:
        return "Very_High"
    elif effects_count >= 3:
        return "High"
    elif effects_count >= 2:
        return "Medium"
    else:
        return "Low"


def get_effects_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of effects analysis results.
    
    Args:
        df (pd.DataFrame): Video data with effects features
        
    Returns:
        Dict[str, Any]: Effects analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'videos_with_effects': (df['effects_count'] > 0).sum() if 'effects_count' in df.columns else 0,
        'avg_effects_per_video': df['effects_count'].mean() if 'effects_count' in df.columns else 0,
        'max_effects_in_video': df['effects_count'].max() if 'effects_count' in df.columns else 0,
        'total_unique_effects': len(set([effect for effects_list in df['effects_list'] if isinstance(effects_list, list) for effect in effects_list]))
    }