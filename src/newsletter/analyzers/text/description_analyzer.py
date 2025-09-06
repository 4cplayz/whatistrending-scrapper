"""
Analyze video descriptions for viral performance impact.
Single responsibility: Description-specific performance analysis.
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_description_length_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance by video description length.
    
    Args:
        df (pd.DataFrame): Video data with description and viral metrics
        
    Returns:
        Dict[str, Any]: Description length performance analysis
    """
    if 'description' not in df.columns:
        logger.warning("description column missing")
        return {}
    
    # Calculate description lengths
    df['description_length'] = df['description'].str.len().fillna(0)
    
    # Categorize by length
    df['description_length_category'] = pd.cut(
        df['description_length'], 
        bins=[0, 50, 150, 300, float('inf')],
        labels=['Very_Short', 'Short', 'Medium', 'Long']
    )
    
    length_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for category in df['description_length_category'].dropna().unique():
        category_data = df[df['description_length_category'] == category]
        if len(category_data) == 0:
            continue
            
        length_analysis[category] = {
            'avg_views': float(category_data['views'].mean()),
            'avg_engagement': float(category_data['engagement_rate'].mean()),
            'viral_impact_score': float(category_data['viral_score'].mean()),
            'video_count': len(category_data),
            'viral_success_rate': float((category_data['views'] >= viral_threshold).mean()),
            'avg_length': float(category_data['description_length'].mean()),
            'length_range': (int(category_data['description_length'].min()), int(category_data['description_length'].max()))
        }
    
    # Find optimal length
    if length_analysis:
        optimal_category = max(length_analysis.items(), key=lambda x: x[1]['avg_views'])
        length_analysis['optimal_length'] = {
            'category': optimal_category[0],
            'avg_views': optimal_category[1]['avg_views'],
            'avg_length': optimal_category[1]['avg_length']
        }
    
    logger.info(f"Analyzed description length impact: {len(length_analysis)} categories")
    return length_analysis


def analyze_mention_usage_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze impact of @mentions in video descriptions.
    
    Args:
        df (pd.DataFrame): Video data with descriptions
        
    Returns:
        Dict[str, Any]: Mention usage impact analysis
    """
    if 'description' not in df.columns:
        logger.warning("description column missing")
        return {}
    
    # Count mentions in descriptions
    df['mention_count'] = df['description'].str.count(r'@\w+').fillna(0)
    df['has_mentions'] = df['mention_count'] > 0
    
    mention_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Analyze by mention count categories
    mention_categories = {
        'no_mentions': 0,
        'few_mentions': (1, 2),
        'many_mentions': (3, float('inf'))
    }
    
    for category, count_range in mention_categories.items():
        if isinstance(count_range, tuple):
            category_data = df[
                (df['mention_count'] >= count_range[0]) & 
                (df['mention_count'] < count_range[1])
            ]
        else:
            category_data = df[df['mention_count'] == count_range]
        
        if len(category_data) == 0:
            continue
            
        mention_analysis[category] = {
            'avg_views': float(category_data['views'].mean()),
            'avg_engagement': float(category_data['engagement_rate'].mean()),
            'viral_impact_score': float(category_data['viral_score'].mean()),
            'video_count': len(category_data),
            'viral_success_rate': float((category_data['views'] >= viral_threshold).mean()),
            'avg_mention_count': float(category_data['mention_count'].mean())
        }
    
    # Compare videos with vs without mentions
    with_mentions = df[df['has_mentions']]
    without_mentions = df[~df['has_mentions']]
    
    if len(with_mentions) > 0 and len(without_mentions) > 0:
        mention_analysis['mention_impact'] = {
            'with_mentions_avg_views': float(with_mentions['views'].mean()),
            'without_mentions_avg_views': float(without_mentions['views'].mean()),
            'mention_advantage': float(with_mentions['views'].mean() / without_mentions['views'].mean()) if without_mentions['views'].mean() > 0 else 0
        }
    
    logger.info("Analyzed @mention usage impact")
    return mention_analysis


def analyze_emoji_usage_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze impact of emoji usage in video descriptions.
    
    Args:
        df (pd.DataFrame): Video data with descriptions
        
    Returns:
        Dict[str, Any]: Emoji usage impact analysis
    """
    if 'description' not in df.columns:
        logger.warning("description column missing")
        return {}
    
    # Count emojis (simplified - counts common emoji patterns)
    emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]'
    df['emoji_count'] = df['description'].str.count(emoji_pattern).fillna(0)
    df['has_emojis'] = df['emoji_count'] > 0
    
    emoji_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Analyze emoji usage categories
    emoji_categories = {
        'no_emojis': 0,
        'few_emojis': (1, 3),
        'many_emojis': (4, float('inf'))
    }
    
    for category, count_range in emoji_categories.items():
        if isinstance(count_range, tuple):
            category_data = df[
                (df['emoji_count'] >= count_range[0]) & 
                (df['emoji_count'] < count_range[1])
            ]
        else:
            category_data = df[df['emoji_count'] == count_range]
        
        if len(category_data) == 0:
            continue
            
        emoji_analysis[category] = {
            'avg_views': float(category_data['views'].mean()),
            'avg_engagement': float(category_data['engagement_rate'].mean()),
            'video_count': len(category_data),
            'viral_success_rate': float((category_data['views'] >= viral_threshold).mean()),
            'avg_emoji_count': float(category_data['emoji_count'].mean())
        }
    
    logger.info("Analyzed emoji usage impact")
    return emoji_analysis


def analyze_description_content_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze content patterns in descriptions that correlate with performance.
    
    Args:
        df (pd.DataFrame): Video data with descriptions
        
    Returns:
        Dict[str, Any]: Description content pattern analysis
    """
    if 'description' not in df.columns:
        logger.warning("description column missing")
        return {}
    
    pattern_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Define patterns to analyze
    content_patterns = {
        'questions': r'\?',
        'exclamations': r'!',
        'car_words': r'\b(car|auto|vehicle|drive|speed|fast|race|engine)\b',
        'action_words': r'\b(check|watch|see|look|follow|like|subscribe)\b',
        'numbers': r'\b\d+\b',
        'capital_words': r'\b[A-Z]{2,}\b'
    }
    
    for pattern_name, pattern_regex in content_patterns.items():
        df[f'has_{pattern_name}'] = df['description'].str.contains(pattern_regex, case=False, regex=True, na=False)
        df[f'{pattern_name}_count'] = df['description'].str.count(pattern_regex, flags=re.IGNORECASE).fillna(0)
        
        # Analyze videos with vs without this pattern
        with_pattern = df[df[f'has_{pattern_name}']]
        without_pattern = df[~df[f'has_{pattern_name}']]
        
        if len(with_pattern) > 0 and len(without_pattern) > 0:
            pattern_analysis[pattern_name] = {
                'with_pattern': {
                    'avg_views': float(with_pattern['views'].mean()),
                    'avg_engagement': float(with_pattern['engagement_rate'].mean()),
                    'video_count': len(with_pattern),
                    'viral_success_rate': float((with_pattern['views'] >= viral_threshold).mean())
                },
                'without_pattern': {
                    'avg_views': float(without_pattern['views'].mean()),
                    'avg_engagement': float(without_pattern['engagement_rate'].mean()),
                    'video_count': len(without_pattern),
                    'viral_success_rate': float((without_pattern['views'] >= viral_threshold).mean())
                },
                'pattern_advantage': float(with_pattern['views'].mean() / without_pattern['views'].mean()) if without_pattern['views'].mean() > 0 else 0,
                'avg_pattern_count': float(with_pattern[f'{pattern_name}_count'].mean()) if len(with_pattern) > 0 else 0
            }
    
    logger.info(f"Analyzed description content patterns: {len(pattern_analysis)} patterns")
    return pattern_analysis


def analyze_call_to_action_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze impact of call-to-action phrases in descriptions.
    
    Args:
        df (pd.DataFrame): Video data with descriptions
        
    Returns:
        Dict[str, Any]: Call-to-action impact analysis
    """
    if 'description' not in df.columns:
        logger.warning("description column missing")
        return {}
    
    # Define CTA patterns
    cta_patterns = [
        r'\blike\b', r'\bfollow\b', r'\bsubscribe\b', r'\bshare\b',
        r'\bcomment\b', r'\btag\b', r'\bcheck out\b', r'\bwatch\b'
    ]
    
    cta_pattern = '|'.join(cta_patterns)
    df['has_cta'] = df['description'].str.contains(cta_pattern, case=False, regex=True, na=False)
    df['cta_count'] = df['description'].str.count(cta_pattern, flags=re.IGNORECASE).fillna(0)
    
    cta_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Compare videos with vs without CTAs
    with_cta = df[df['has_cta']]
    without_cta = df[~df['has_cta']]
    
    if len(with_cta) > 0:
        cta_analysis['with_cta'] = {
            'avg_views': float(with_cta['views'].mean()),
            'avg_engagement': float(with_cta['engagement_rate'].mean()),
            'video_count': len(with_cta),
            'viral_success_rate': float((with_cta['views'] >= viral_threshold).mean()),
            'avg_cta_count': float(with_cta['cta_count'].mean())
        }
    
    if len(without_cta) > 0:
        cta_analysis['without_cta'] = {
            'avg_views': float(without_cta['views'].mean()),
            'avg_engagement': float(without_cta['engagement_rate'].mean()),
            'video_count': len(without_cta),
            'viral_success_rate': float((without_cta['views'] >= viral_threshold).mean())
        }
    
    # Calculate CTA impact
    if len(with_cta) > 0 and len(without_cta) > 0:
        cta_analysis['cta_impact'] = {
            'views_advantage': float(with_cta['views'].mean() / without_cta['views'].mean()) if without_cta['views'].mean() > 0 else 0,
            'engagement_difference': float(with_cta['engagement_rate'].mean() - without_cta['engagement_rate'].mean())
        }
    
    logger.info("Analyzed call-to-action impact")
    return cta_analysis


def get_optimal_description_strategy(description_analyses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate optimal description strategy based on all analyses.
    
    Args:
        description_analyses (Dict[str, Any]): Combined description analysis results
        
    Returns:
        Dict[str, Any]: Optimal description strategy recommendations
    """
    recommendations = {}
    
    # Length recommendations
    if 'length_analysis' in description_analyses and 'optimal_length' in description_analyses['length_analysis']:
        optimal_data = description_analyses['length_analysis']['optimal_length']
        recommendations['optimal_length'] = {
            'category': optimal_data['category'],
            'target_length': f"{int(optimal_data['avg_length'])} characters",
            'expected_performance': f"{optimal_data['avg_views']:,.0f} avg views"
        }
    
    # Mention recommendations
    if 'mention_analysis' in description_analyses and 'mention_impact' in description_analyses['mention_analysis']:
        mention_impact = description_analyses['mention_analysis']['mention_impact']
        if mention_impact['mention_advantage'] > 1.1:  # 10% advantage
            recommendations['use_mentions'] = {
                'recommendation': 'Include @mentions in descriptions',
                'performance_advantage': f"{((mention_impact['mention_advantage'] - 1) * 100):.1f}%"
            }
    
    # Pattern recommendations
    if 'pattern_analysis' in description_analyses:
        pattern_data = description_analyses['pattern_analysis']
        beneficial_patterns = []
        
        for pattern, data in pattern_data.items():
            if data['pattern_advantage'] > 1.15:  # 15% advantage
                beneficial_patterns.append({
                    'pattern': pattern.replace('_', ' ').title(),
                    'advantage': f"{((data['pattern_advantage'] - 1) * 100):.1f}%"
                })
        
        if beneficial_patterns:
            recommendations['beneficial_patterns'] = beneficial_patterns
    
    # CTA recommendations
    if 'cta_analysis' in description_analyses and 'cta_impact' in description_analyses['cta_analysis']:
        cta_impact = description_analyses['cta_analysis']['cta_impact']
        if cta_impact['views_advantage'] > 1.1:  # 10% advantage
            recommendations['include_cta'] = {
                'recommendation': 'Include call-to-action phrases',
                'performance_advantage': f"{((cta_impact['views_advantage'] - 1) * 100):.1f}%"
            }
    
    logger.info("Generated optimal description strategy")
    return recommendations


def get_description_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of description analysis results.
    
    Args:
        df (pd.DataFrame): Video data with description features
        
    Returns:
        Dict[str, Any]: Description analysis summary
    """
    if df.empty or 'description' not in df.columns:
        return {'status': 'no_data'}
    
    # Calculate basic description stats
    df['description_length'] = df['description'].str.len().fillna(0)
    df['mention_count'] = df['description'].str.count(r'@\w+').fillna(0)
    
    return {
        'total_videos': len(df),
        'videos_with_descriptions': df['description'].notna().sum(),
        'avg_description_length': float(df['description_length'].mean()),
        'max_description_length': int(df['description_length'].max()),
        'videos_with_mentions': int((df['mention_count'] > 0).sum()),
        'avg_mentions_per_video': float(df['mention_count'].mean()),
        'most_common_words': ' '.join(df['description'].fillna('').str.lower().str.split().explode().value_counts().head(5).index.tolist())
    }