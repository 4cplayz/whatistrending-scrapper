"""
Analyze video quality metrics for viral performance impact.
Single responsibility: Quality-based performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_viral_score_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance by viral score tiers.

    Args:
        df (pd.DataFrame): Video data with viral_score and engagement metrics

    Returns:
        Dict[str, Any]: Viral score performance analysis
    """
    if 'viral_score' not in df.columns:
        logger.warning("viral_score column missing")
        return {}

    quality_analysis = {}
    viral_threshold = df['views'].quantile(0.8)

    # Create viral score tiers
    df['viral_tier'] = pd.cut(
        df['viral_score'].fillna(0),
        bins=[0, 0.3, 0.6, 0.8, 1.0],
        labels=['Low', 'Medium', 'High', 'Premium']
    )
    
    for tier in df['viral_tier'].dropna().unique():
        tier_data = df[df['viral_tier'] == tier]
        if len(tier_data) == 0:
            continue

        quality_analysis[tier] = {
            'avg_views': float(tier_data['views'].mean()),
            'avg_engagement': float(tier_data['engagement_rate'].mean()),
            'viral_impact_score': float(tier_data['viral_score'].mean()),
            'video_count': len(tier_data),
            'viral_videos': int((tier_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((tier_data['views'] >= viral_threshold).mean()),
            'avg_viral_score': float(tier_data['viral_score'].mean()),
            'viral_range': (float(tier_data['viral_score'].min()), float(tier_data['viral_score'].max()))
        }

    # Calculate viral-performance correlation
    viral_correlation = df['viral_score'].corr(df['views'])
    quality_analysis['viral_views_correlation'] = float(viral_correlation) if not np.isnan(viral_correlation) else 0.0
    
    logger.info(f"Analyzed viral score performance: {len(quality_analysis)} tiers")
    return quality_analysis


def analyze_engagement_viral_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze correlation between engagement metrics and viral score.

    Args:
        df (pd.DataFrame): Video data with viral_score and engagement metrics

    Returns:
        Dict[str, Any]: Engagement-viral correlation analysis
    """
    correlation_analysis = {}

    if 'viral_score' not in df.columns:
        logger.warning("viral_score column missing")
        return correlation_analysis

    # Calculate correlations with different engagement metrics
    engagement_metrics = ['views', 'likes', 'comments', 'shares', 'engagement_rate']

    for metric in engagement_metrics:
        if metric in df.columns:
            correlation = df['viral_score'].corr(df[metric])
            correlation_analysis[f"viral_{metric}_correlation"] = float(correlation) if not np.isnan(correlation) else 0.0

    # Analyze high-viral content performance
    high_viral = df[df['viral_score'] >= 0.8] if 'viral_score' in df.columns else pd.DataFrame()
    low_viral = df[df['viral_score'] < 0.4] if 'viral_score' in df.columns else pd.DataFrame()

    if len(high_viral) > 0 and len(low_viral) > 0:
        correlation_analysis['viral_impact'] = {
            'high_viral_avg_views': float(high_viral['views'].mean()),
            'low_viral_avg_views': float(low_viral['views'].mean()),
            'viral_advantage': float(high_viral['views'].mean() / low_viral['views'].mean()) if low_viral['views'].mean() > 0 else 0,
            'high_viral_engagement': float(high_viral['engagement_rate'].mean()),
            'low_viral_engagement': float(low_viral['engagement_rate'].mean())
        }
    
    logger.info("Analyzed engagement-viral correlations")
    return correlation_analysis


def analyze_technical_quality_factors(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze technical factors that might indicate quality.
    
    Args:
        df (pd.DataFrame): Video data with technical specifications
        
    Returns:
        Dict[str, Any]: Technical quality factors analysis
    """
    technical_analysis = {}
    
    # Resolution as quality indicator
    if 'width' in df.columns and 'height' in df.columns:
        df['total_pixels'] = df['width'] * df['height']
        df['resolution_tier'] = pd.qcut(
            df['total_pixels'], 
            q=4, 
            labels=['Low_Res', 'Medium_Res', 'High_Res', 'Ultra_Res'],
            duplicates='drop'
        )
        
        technical_analysis['resolution_quality'] = {}
        for tier in df['resolution_tier'].dropna().unique():
            tier_data = df[df['resolution_tier'] == tier]
            if len(tier_data) > 0:
                technical_analysis['resolution_quality'][tier] = {
                    'avg_views': float(tier_data['views'].mean()),
                    'avg_engagement': float(tier_data['engagement_rate'].mean()),
                    'video_count': len(tier_data),
                    'avg_pixels': int(tier_data['total_pixels'].mean())
                }
    
    # Duration optimization as quality indicator
    if 'duration' in df.columns:
        # Videos with "optimal" durations might be better produced
        optimal_durations = [15, 30, 60]  # Common optimal TikTok durations
        df['has_optimal_duration'] = df['duration'].isin(optimal_durations)
        
        optimal_duration = df[df['has_optimal_duration']]
        suboptimal_duration = df[~df['has_optimal_duration']]
        
        if len(optimal_duration) > 0 and len(suboptimal_duration) > 0:
            technical_analysis['duration_optimization'] = {
                'optimal_duration': {
                    'avg_views': float(optimal_duration['views'].mean()),
                    'avg_engagement': float(optimal_duration['engagement_rate'].mean()),
                    'video_count': len(optimal_duration)
                },
                'suboptimal_duration': {
                    'avg_views': float(suboptimal_duration['views'].mean()),
                    'avg_engagement': float(suboptimal_duration['engagement_rate'].mean()),
                    'video_count': len(suboptimal_duration)
                }
            }
    
    # Aspect ratio standardization as quality indicator
    if 'width' in df.columns and 'height' in df.columns:
        df['aspect_ratio'] = df['width'] / df['height']
        standard_ratios = [16/9, 9/16, 1/1]  # Common standard ratios
        df['has_standard_ratio'] = df['aspect_ratio'].apply(
            lambda x: any(abs(x - ratio) < 0.1 for ratio in standard_ratios)
        )
        
        standard_ratio = df[df['has_standard_ratio']]
        custom_ratio = df[~df['has_standard_ratio']]
        
        if len(standard_ratio) > 0 and len(custom_ratio) > 0:
            technical_analysis['aspect_ratio_standardization'] = {
                'standard_ratio': {
                    'avg_views': float(standard_ratio['views'].mean()),
                    'video_count': len(standard_ratio)
                },
                'custom_ratio': {
                    'avg_views': float(custom_ratio['views'].mean()),
                    'video_count': len(custom_ratio)
                }
            }
    
    logger.info(f"Analyzed technical quality factors: {len(technical_analysis)} factors")
    return technical_analysis


def analyze_content_complexity_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze how content complexity relates to quality and performance.
    
    Args:
        df (pd.DataFrame): Video data with content complexity metrics
        
    Returns:
        Dict[str, Any]: Content complexity-quality analysis
    """
    complexity_analysis = {}
    
    # Multi-element complexity analysis
    complexity_indicators = {
        'multi_brand': 'multi_brand_video',
        'multi_hook': 'multi_hook_video',
        'effects_count': 'effects_count',
        'transition_count': 'transition_count'
    }
    
    for indicator_name, column in complexity_indicators.items():
        if column in df.columns:
            if column in ['multi_brand_video', 'multi_hook_video']:
                # Boolean indicators
                complex_videos = df[df[column] == True]
                simple_videos = df[df[column] == False]
            else:
                # Count indicators - consider high count as complex
                median_count = df[column].median()
                complex_videos = df[df[column] > median_count]
                simple_videos = df[df[column] <= median_count]
            
            if len(complex_videos) > 0 and len(simple_videos) > 0:
                complexity_analysis[indicator_name] = {
                    'complex_videos': {
                        'avg_views': float(complex_videos['views'].mean()),
                        'avg_engagement': float(complex_videos['engagement_rate'].mean()),
                        'video_count': len(complex_videos)
                    },
                    'simple_videos': {
                        'avg_views': float(simple_videos['views'].mean()),
                        'avg_engagement': float(simple_videos['engagement_rate'].mean()),
                        'video_count': len(simple_videos)
                    },
                    'complexity_advantage': float(complex_videos['views'].mean() / simple_videos['views'].mean()) if simple_videos['views'].mean() > 0 else 0
                }
    
    logger.info(f"Analyzed content complexity-quality: {len(complexity_analysis)} indicators")
    return complexity_analysis


def get_quality_recommendations(quality_analyses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate quality improvement recommendations based on analyses.
    
    Args:
        quality_analyses (Dict[str, Any]): Combined quality analysis results
        
    Returns:
        Dict[str, Any]: Quality improvement recommendations
    """
    recommendations = {}
    
    # Viral score recommendations
    if 'viral_score_analysis' in quality_analyses:
        viral_data = quality_analyses['viral_score_analysis']
        if viral_data:
            best_tier = max(
                [(tier, data) for tier, data in viral_data.items() if tier != 'viral_views_correlation'],
                key=lambda x: x[1].get('avg_views', 0)
            )
            recommendations['target_viral_tier'] = {
                'tier': best_tier[0],
                'min_score': best_tier[1]['viral_range'][0],
                'expected_views': best_tier[1]['avg_views']
            }
    
    # Technical recommendations
    if 'technical_analysis' in quality_analyses:
        tech_data = quality_analyses['technical_analysis']
        
        if 'resolution_quality' in tech_data:
            best_res = max(
                tech_data['resolution_quality'].items(),
                key=lambda x: x[1]['avg_views']
            )
            recommendations['optimal_resolution'] = {
                'tier': best_res[0],
                'avg_pixels': best_res[1]['avg_pixels'],
                'expected_views': best_res[1]['avg_views']
            }
        
        if 'duration_optimization' in tech_data:
            duration_data = tech_data['duration_optimization']
            if duration_data['optimal_duration']['avg_views'] > duration_data['suboptimal_duration']['avg_views']:
                recommendations['use_standard_durations'] = {
                    'recommendation': 'Use standard durations (15s, 30s, 60s)',
                    'performance_advantage': f"{((duration_data['optimal_duration']['avg_views'] / duration_data['suboptimal_duration']['avg_views']) - 1) * 100:.1f}%"
                }
    
    # Complexity recommendations
    if 'complexity_analysis' in quality_analyses:
        complexity_data = quality_analyses['complexity_analysis']
        for complexity_type, data in complexity_data.items():
            if data['complexity_advantage'] > 1.2:  # 20% advantage
                recommendations[f"increase_{complexity_type}"] = {
                    'recommendation': f"Consider increasing {complexity_type.replace('_', ' ')}",
                    'performance_advantage': f"{((data['complexity_advantage'] - 1) * 100):.1f}%"
                }
    
    logger.info("Generated quality improvement recommendations")
    return recommendations


def get_quality_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of quality analysis results.
    
    Args:
        df (pd.DataFrame): Video data with quality metrics
        
    Returns:
        Dict[str, Any]: Quality analysis summary
    """
    if df.empty:
        return {'status': 'no_data'}
    
    summary = {
        'total_videos': len(df)
    }
    
    if 'viral_score' in df.columns:
        summary.update({
            'avg_viral_score': float(df['viral_score'].mean()),
            'viral_score_range': (float(df['viral_score'].min()), float(df['viral_score'].max())),
            'high_viral_videos': int((df['viral_score'] >= 0.8).sum()),
            'low_viral_videos': int((df['viral_score'] < 0.4).sum())
        })
    
    if 'width' in df.columns and 'height' in df.columns:
        summary.update({
            'avg_resolution': f"{int(df['width'].mean())}x{int(df['height'].mean())}",
            'resolution_variety': len(df[['width', 'height']].drop_duplicates())
        })
    
    return summary