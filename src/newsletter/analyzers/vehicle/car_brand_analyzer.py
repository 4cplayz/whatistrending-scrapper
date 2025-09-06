"""
Analyze individual car brands for viral performance impact.
Single responsibility: Car brand-specific performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_individual_brand_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance for each individual car brand.
    
    Args:
        df (pd.DataFrame): Video data with car brand features and viral metrics
        
    Returns:
        Dict[str, Any]: Individual car brand performance analysis
        
    Raises:
        ValueError: If required columns are missing
    """
    required_cols = ['car_brands_list', 'views', 'engagement_rate', 'viral_score']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    brand_performance = {}
    
    # Analyze each individual car brand across all videos
    for _, row in df.iterrows():
        brands = row.get('car_brands_list', [])
        if not isinstance(brands, list):
            continue
            
        for brand in brands:
            if brand and brand.strip():  # Skip empty brands
                if brand not in brand_performance:
                    brand_performance[brand] = {
                        'views': [], 
                        'engagement': [], 
                        'viral_scores': [],
                        'video_ids': []
                    }
                
                brand_performance[brand]['views'].append(row['views'])
                brand_performance[brand]['engagement'].append(row['engagement_rate'])
                brand_performance[brand]['viral_scores'].append(row['viral_score'])
                brand_performance[brand]['video_ids'].append(row.get('video_id', ''))
    
    # Calculate performance metrics for each brand
    analyzed_brands = {}
    viral_threshold = df['views'].quantile(0.8) if 'views' in df.columns else 0
    
    for brand, data in brand_performance.items():
        if len(data['views']) > 0:
            analyzed_brands[brand] = {
                'avg_views': float(np.mean(data['views'])),
                'avg_engagement': float(np.mean(data['engagement'])),
                'total_views': int(np.sum(data['views'])),
                'viral_impact_score': float(np.mean(data['viral_scores'])),
                'video_count': len(data['views']),
                'max_views_achieved': int(max(data['views'])),
                'viral_videos': len([v for v in data['views'] if v >= viral_threshold]),
                'viral_success_rate': float(len([v for v in data['views'] if v >= viral_threshold]) / len(data['views'])),
                'performance_tier': _classify_brand_performance(np.mean(data['views']), np.mean(data['engagement'])),
                'brand_category': _categorize_car_brand(brand)
            }
    
    logger.info(f"Analyzed {len(analyzed_brands)} individual car brands")
    return analyzed_brands


def analyze_brand_momentum(df: pd.DataFrame, historical_data: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Analyze week-over-week momentum for car brands.
    
    Args:
        df (pd.DataFrame): Current week video data
        historical_data (pd.DataFrame, optional): Historical data for comparison
        
    Returns:
        Dict[str, Any]: Brand momentum analysis
    """
    current_week_brands = {}
    
    # Calculate current week brand performance
    for _, row in df.iterrows():
        brands = row.get('car_brands_list', [])
        if isinstance(brands, list):
            for brand in brands:
                if brand and brand.strip():
                    if brand not in current_week_brands:
                        current_week_brands[brand] = {'views': [], 'videos': 0}
                    current_week_brands[brand]['views'].append(row['views'])
                    current_week_brands[brand]['videos'] += 1
    
    # Calculate averages for current week
    current_performance = {}
    for brand, data in current_week_brands.items():
        current_performance[brand] = {
            'avg_views': np.mean(data['views']),
            'video_count': data['videos'],
            'total_views': np.sum(data['views'])
        }
    
    momentum_analysis = {
        'current_week': current_performance,
        'trend_status': {}
    }
    
    # If historical data is available, calculate momentum
    if historical_data is not None:
        # This would compare with previous week's data
        # For now, classify based on current performance relative to others
        avg_views_list = [data['avg_views'] for data in current_performance.values()]
        if avg_views_list:
            median_views = np.median(avg_views_list)
            
            for brand, data in current_performance.items():
                if data['avg_views'] > median_views * 1.2:
                    momentum_analysis['trend_status'][brand] = 'Rising'
                elif data['avg_views'] < median_views * 0.8:
                    momentum_analysis['trend_status'][brand] = 'Declining'
                else:
                    momentum_analysis['trend_status'][brand] = 'Stable'
    
    logger.info(f"Analyzed momentum for {len(current_performance)} brands")
    return momentum_analysis


def analyze_multi_brand_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze performance impact of multi-brand videos.
    
    Args:
        df (pd.DataFrame): Video data with multi-brand features
        
    Returns:
        Dict[str, Any]: Multi-brand performance analysis
    """
    if 'multi_brand_video' not in df.columns or 'car_brand_count' not in df.columns:
        logger.warning("Multi-brand columns missing")
        return {}
    
    multi_brand_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    # Compare single vs multi-brand performance
    single_brand = df[df['multi_brand_video'] == False]
    multi_brand = df[df['multi_brand_video'] == True]
    
    if len(single_brand) > 0:
        multi_brand_analysis['single_brand'] = {
            'video_count': len(single_brand),
            'avg_views': float(single_brand['views'].mean()),
            'avg_engagement': float(single_brand['engagement_rate'].mean()),
            'viral_success_rate': float((single_brand['views'] >= viral_threshold).mean())
        }
    
    if len(multi_brand) > 0:
        multi_brand_analysis['multi_brand'] = {
            'video_count': len(multi_brand),
            'avg_views': float(multi_brand['views'].mean()),
            'avg_engagement': float(multi_brand['engagement_rate'].mean()),
            'viral_success_rate': float((multi_brand['views'] >= viral_threshold).mean())
        }
    
    # Analyze by brand count
    for brand_count in df['car_brand_count'].unique():
        if pd.isna(brand_count) or brand_count == 0:
            continue
            
        brand_count_data = df[df['car_brand_count'] == brand_count]
        if len(brand_count_data) == 0:
            continue
            
        multi_brand_analysis[f"brands_{int(brand_count)}"] = {
            'video_count': len(brand_count_data),
            'avg_views': float(brand_count_data['views'].mean()),
            'avg_engagement': float(brand_count_data['engagement_rate'].mean()),
            'viral_success_rate': float((brand_count_data['views'] >= viral_threshold).mean())
        }
    
    logger.info("Analyzed multi-brand video impact")
    return multi_brand_analysis


def get_top_performing_brands(brand_analysis: Dict[str, Any], top_n: int = 10) -> Dict[str, Any]:
    """
    Get top performing car brands by different metrics.
    
    Args:
        brand_analysis (Dict[str, Any]): Individual brand performance analysis
        top_n (int): Number of top performers to return
        
    Returns:
        Dict[str, Any]: Top performers by different metrics
    """
    if not brand_analysis:
        return {}
    
    # Sort by different metrics
    by_views = sorted(brand_analysis.items(), key=lambda x: x[1]['avg_views'], reverse=True)
    by_engagement = sorted(brand_analysis.items(), key=lambda x: x[1]['avg_engagement'], reverse=True)
    by_total_views = sorted(brand_analysis.items(), key=lambda x: x[1]['total_views'], reverse=True)
    by_viral_rate = sorted(brand_analysis.items(), key=lambda x: x[1]['viral_success_rate'], reverse=True)
    by_video_count = sorted(brand_analysis.items(), key=lambda x: x[1]['video_count'], reverse=True)
    
    return {
        'top_by_avg_views': [(brand, data['avg_views']) for brand, data in by_views[:top_n]],
        'top_by_engagement': [(brand, data['avg_engagement']) for brand, data in by_engagement[:top_n]],
        'top_by_total_views': [(brand, data['total_views']) for brand, data in by_total_views[:top_n]],
        'top_by_viral_rate': [(brand, data['viral_success_rate']) for brand, data in by_viral_rate[:top_n]],
        'most_featured': [(brand, data['video_count']) for brand, data in by_video_count[:top_n]]
    }


def _categorize_car_brand(brand: str) -> str:
    """
    Categorize car brand into luxury/performance segments.
    
    Args:
        brand (str): Car brand name
        
    Returns:
        str: Brand category
    """
    brand_lower = brand.lower()
    
    luxury_brands = ['ferrari', 'lamborghini', 'mclaren', 'bugatti', 'koenigsegg', 'pagani']
    premium_brands = ['porsche', 'mercedes', 'bmw', 'audi', 'lexus', 'acura']
    sports_brands = ['corvette', 'mustang', 'challenger', 'camaro', 'nissan', 'subaru']
    
    if any(lux in brand_lower for lux in luxury_brands):
        return "Supercar"
    elif any(prem in brand_lower for prem in premium_brands):
        return "Premium"
    elif any(sport in brand_lower for sport in sports_brands):
        return "Sports"
    else:
        return "Other"


def _classify_brand_performance(avg_views: float, avg_engagement: float) -> str:
    """
    Classify brand performance into tiers.
    
    Args:
        avg_views (float): Average views for the brand
        avg_engagement (float): Average engagement rate for the brand
        
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


def get_brand_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of car brand analysis results.
    
    Args:
        df (pd.DataFrame): Video data with car brand features
        
    Returns:
        Dict[str, Any]: Brand analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'videos_with_car_brands': df['car_brand'].notna().sum() if 'car_brand' in df.columns else 0,
        'unique_car_brands': df['car_brand'].nunique() if 'car_brand' in df.columns else 0,
        'multi_brand_videos': df['multi_brand_video'].sum() if 'multi_brand_video' in df.columns else 0,
        'avg_brands_per_video': df['car_brand_count'].mean() if 'car_brand_count' in df.columns else 0,
        'max_brands_in_video': df['car_brand_count'].max() if 'car_brand_count' in df.columns else 0
    }