"""
Analyze individual hashtags for viral performance impact.
Single responsibility: Hashtag-specific performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def analyze_individual_hashtag_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance for each individual hashtag.
    
    Args:
        df (pd.DataFrame): Video data with hashtags and viral metrics
        
    Returns:
        Dict[str, Any]: Individual hashtag performance analysis
        
    Raises:
        ValueError: If required columns are missing
    """
    required_cols = ['hashtags', 'views', 'engagement_rate', 'viral_score']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    hashtag_performance = {}
    
    # Extract all hashtags across all videos
    for _, row in df.iterrows():
        hashtags = row.get('hashtags', [])
        if not isinstance(hashtags, list):
            continue
            
        for hashtag in hashtags:
            tag_name = hashtag.get('name', '').strip() if isinstance(hashtag, dict) else str(hashtag).strip()
            if tag_name and len(tag_name) > 1:  # Skip empty or single-char tags
                if tag_name not in hashtag_performance:
                    hashtag_performance[tag_name] = {
                        'views': [], 
                        'engagement': [], 
                        'viral_scores': [],
                        'video_ids': []
                    }
                
                hashtag_performance[tag_name]['views'].append(row['views'])
                hashtag_performance[tag_name]['engagement'].append(row['engagement_rate'])
                hashtag_performance[tag_name]['viral_scores'].append(row['viral_score'])
                hashtag_performance[tag_name]['video_ids'].append(row.get('video_id', ''))
    
    # Calculate performance metrics for each hashtag
    analyzed_hashtags = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for hashtag, data in hashtag_performance.items():
        if len(data['views']) > 0:
            analyzed_hashtags[hashtag] = {
                'avg_views': float(np.mean(data['views'])),
                'avg_engagement': float(np.mean(data['engagement'])),
                'viral_impact_score': float(np.mean(data['viral_scores'])),
                'usage_count': len(data['views']),
                'max_views_achieved': int(max(data['views'])),
                'viral_videos': len([v for v in data['views'] if v >= viral_threshold]),
                'viral_success_rate': float(len([v for v in data['views'] if v >= viral_threshold]) / len(data['views'])),
                'hashtag_category': _categorize_hashtag(hashtag),
                'performance_tier': _classify_hashtag_performance(np.mean(data['views']), np.mean(data['engagement']))
            }
    
    logger.info(f"Analyzed {len(analyzed_hashtags)} individual hashtags")
    return analyzed_hashtags


def analyze_hashtag_count_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze optimal number of hashtags for viral performance.
    
    Args:
        df (pd.DataFrame): Video data with hashtag count metrics
        
    Returns:
        Dict[str, Any]: Hashtag count impact analysis
    """
    if 'hashtag_count' not in df.columns:
        logger.warning("hashtag_count column missing")
        return {}
    
    count_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Analyze by hashtag count
    for count in sorted(df['hashtag_count'].unique()):
        if pd.isna(count):
            continue
            
        count_data = df[df['hashtag_count'] == count]
        if len(count_data) == 0:
            continue
            
        count_analysis[f"hashtags_{int(count)}"] = {
            'avg_views': float(count_data['views'].mean()),
            'avg_engagement': float(count_data['engagement_rate'].mean()),
            'viral_impact_score': float(count_data['viral_score'].mean()),
            'video_count': len(count_data),
            'viral_success_rate': float((count_data['views'] >= viral_threshold).mean()),
            'hashtag_density': f"{int(count)} hashtags per video"
        }
    
    # Find optimal hashtag count
    if count_analysis:
        optimal_count = max(count_analysis.items(), key=lambda x: x[1]['avg_views'])
        count_analysis['optimal_hashtag_count'] = {
            'count': int(optimal_count[0].split('_')[1]),
            'avg_views': optimal_count[1]['avg_views'],
            'performance_advantage': f"{((optimal_count[1]['avg_views'] / min(x[1]['avg_views'] for x in count_analysis.items() if x[0] != 'optimal_hashtag_count')) - 1) * 100:.1f}%" if len(count_analysis) > 1 else "N/A"
        }
    
    logger.info(f"Analyzed hashtag count impact: {len(count_analysis)} count patterns")
    return count_analysis


def analyze_car_specific_hashtags(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze car-specific hashtags vs general hashtags performance.
    
    Args:
        df (pd.DataFrame): Video data with hashtags and car features
        
    Returns:
        Dict[str, Any]: Car-specific hashtag analysis
    """
    if 'has_car_hashtags' not in df.columns:
        logger.warning("has_car_hashtags column missing")
        return {}
    
    car_hashtag_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Compare videos with vs without car hashtags
    with_car_hashtags = df[df['has_car_hashtags'] == True]
    without_car_hashtags = df[df['has_car_hashtags'] == False]
    
    if len(with_car_hashtags) > 0:
        car_hashtag_analysis['with_car_hashtags'] = {
            'video_count': len(with_car_hashtags),
            'avg_views': float(with_car_hashtags['views'].mean()),
            'avg_engagement': float(with_car_hashtags['engagement_rate'].mean()),
            'viral_success_rate': float((with_car_hashtags['views'] >= viral_threshold).mean())
        }
    
    if len(without_car_hashtags) > 0:
        car_hashtag_analysis['without_car_hashtags'] = {
            'video_count': len(without_car_hashtags),
            'avg_views': float(without_car_hashtags['views'].mean()),
            'avg_engagement': float(without_car_hashtags['engagement_rate'].mean()),
            'viral_success_rate': float((without_car_hashtags['views'] >= viral_threshold).mean())
        }
    
    # Calculate car hashtag advantage
    if len(with_car_hashtags) > 0 and len(without_car_hashtags) > 0:
        car_hashtag_analysis['car_hashtag_advantage'] = {
            'views_multiplier': float(with_car_hashtags['views'].mean() / without_car_hashtags['views'].mean()) if without_car_hashtags['views'].mean() > 0 else 0,
            'engagement_difference': float(with_car_hashtags['engagement_rate'].mean() - without_car_hashtags['engagement_rate'].mean())
        }
    
    logger.info("Analyzed car-specific hashtag performance")
    return car_hashtag_analysis


def analyze_hashtag_combinations(df: pd.DataFrame, min_combination_count: int = 3) -> Dict[str, Any]:
    """
    Analyze performance of hashtag combinations that appear together frequently.
    
    Args:
        df (pd.DataFrame): Video data with hashtags
        min_combination_count (int): Minimum times combination must appear
        
    Returns:
        Dict[str, Any]: Hashtag combination analysis
    """
    combination_analysis = {}
    
    # Find frequently co-occurring hashtag pairs
    hashtag_pairs = {}
    for _, row in df.iterrows():
        hashtags = row.get('hashtags', [])
        if not isinstance(hashtags, list) or len(hashtags) < 2:
            continue
            
        tag_names = [hashtag.get('name', '') if isinstance(hashtag, dict) else str(hashtag) for hashtag in hashtags]
        tag_names = [tag.strip() for tag in tag_names if tag.strip() and len(tag.strip()) > 1]
        
        # Generate all pairs
        for i in range(len(tag_names)):
            for j in range(i + 1, len(tag_names)):
                pair = tuple(sorted([tag_names[i], tag_names[j]]))
                if pair not in hashtag_pairs:
                    hashtag_pairs[pair] = {
                        'views': [],
                        'engagement': [],
                        'video_count': 0
                    }
                hashtag_pairs[pair]['views'].append(row['views'])
                hashtag_pairs[pair]['engagement'].append(row['engagement_rate'])
                hashtag_pairs[pair]['video_count'] += 1
    
    # Analyze pairs that meet minimum threshold
    for pair, data in hashtag_pairs.items():
        if data['video_count'] >= min_combination_count:
            combination_key = f"{pair[0]} + {pair[1]}"
            combination_analysis[combination_key] = {
                'avg_views': float(np.mean(data['views'])),
                'avg_engagement': float(np.mean(data['engagement'])),
                'usage_count': data['video_count'],
                'max_views': int(max(data['views'])),
                'hashtag_synergy': _calculate_hashtag_synergy(pair, df)
            }
    
    # Sort by performance
    if combination_analysis:
        top_combinations = sorted(
            combination_analysis.items(), 
            key=lambda x: x[1]['avg_views'], 
            reverse=True
        )[:10]
        combination_analysis['top_combinations'] = [
            {'combination': combo, 'avg_views': data['avg_views']} 
            for combo, data in top_combinations
        ]
    
    logger.info(f"Analyzed hashtag combinations: {len(combination_analysis)} patterns found")
    return combination_analysis


def get_top_performing_hashtags(hashtag_analysis: Dict[str, Any], top_n: int = 20) -> Dict[str, Any]:
    """
    Get top performing hashtags by different metrics.
    
    Args:
        hashtag_analysis (Dict[str, Any]): Individual hashtag performance analysis
        top_n (int): Number of top performers to return
        
    Returns:
        Dict[str, Any]: Top performers by different metrics
    """
    if not hashtag_analysis:
        return {}
    
    # Sort by different metrics
    by_views = sorted(hashtag_analysis.items(), key=lambda x: x[1]['avg_views'], reverse=True)
    by_engagement = sorted(hashtag_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)
    by_viral_rate = sorted(hashtag_analysis.items(), key=lambda x: x[1]['viral_success_rate'], reverse=True)
    by_usage = sorted(hashtag_analysis.items(), key=lambda x: x[1]['usage_count'], reverse=True)
    
    return {
        'top_by_views': [(hashtag, data['avg_views']) for hashtag, data in by_views[:top_n]],
        'top_by_engagement': [(hashtag, data['avg_engagement']) for hashtag, data in by_engagement[:top_n]],
        'top_by_viral_rate': [(hashtag, data['viral_success_rate']) for hashtag, data in by_viral_rate[:top_n]],
        'most_used': [(hashtag, data['usage_count']) for hashtag, data in by_usage[:top_n]]
    }


def _categorize_hashtag(hashtag: str) -> str:
    """
    Categorize hashtag into logical groups.
    
    Args:
        hashtag (str): Hashtag text
        
    Returns:
        str: Hashtag category
    """
    hashtag_lower = hashtag.lower()
    
    car_brands = ['ferrari', 'lamborghini', 'mclaren', 'porsche', 'bmw', 'mercedes', 'audi']
    car_types = ['supercar', 'hypercar', 'sportcar', 'luxury', 'exotic']
    car_features = ['exhaust', 'engine', 'sound', 'acceleration', 'speed']
    general_viral = ['fyp', 'viral', 'trending', 'explore', 'foryou']
    
    if any(brand in hashtag_lower for brand in car_brands):
        return "Car_Brand"
    elif any(car_type in hashtag_lower for car_type in car_types):
        return "Car_Type"
    elif any(feature in hashtag_lower for feature in car_features):
        return "Car_Feature"
    elif any(viral in hashtag_lower for viral in general_viral):
        return "Viral_General"
    elif 'car' in hashtag_lower:
        return "Car_General"
    else:
        return "Other"


def _classify_hashtag_performance(avg_views: float, avg_engagement: float) -> str:
    """
    Classify hashtag performance into tiers.
    
    Args:
        avg_views (float): Average views for the hashtag
        avg_engagement (float): Average engagement rate for the hashtag
        
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


def _calculate_hashtag_synergy(pair: tuple, df: pd.DataFrame) -> float:
    """
    Calculate synergy score for hashtag pair vs individual performance.
    
    Args:
        pair (tuple): Hashtag pair
        df (pd.DataFrame): Video data
        
    Returns:
        float: Synergy score
    """
    # This is a simplified synergy calculation
    # In practice, you'd compare combined performance vs individual performance
    return 1.0  # Placeholder


def get_hashtag_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of hashtag analysis results.
    
    Args:
        df (pd.DataFrame): Video data with hashtag features
        
    Returns:
        Dict[str, Any]: Hashtag analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    # Count all unique hashtags
    all_hashtags = set()
    for _, row in df.iterrows():
        hashtags = row.get('hashtags', [])
        if isinstance(hashtags, list):
            for hashtag in hashtags:
                tag_name = hashtag.get('name', '') if isinstance(hashtag, dict) else str(hashtag)
                if tag_name.strip():
                    all_hashtags.add(tag_name.strip())
    
    return {
        'total_videos': len(df),
        'videos_with_hashtags': (df['hashtag_count'] > 0).sum() if 'hashtag_count' in df.columns else 0,
        'unique_hashtags': len(all_hashtags),
        'avg_hashtags_per_video': df['hashtag_count'].mean() if 'hashtag_count' in df.columns else 0,
        'max_hashtags_in_video': df['hashtag_count'].max() if 'hashtag_count' in df.columns else 0,
        'videos_with_car_hashtags': df['has_car_hashtags'].sum() if 'has_car_hashtags' in df.columns else 0
    }