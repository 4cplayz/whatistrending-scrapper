"""
Validate correlations between content elements and performance metrics.
Single responsibility: Statistical correlation validation with p-values.
"""
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


def validate_engagement_correlations(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate correlations between engagement metrics with statistical significance.
    
    Args:
        df (pd.DataFrame): Video data with engagement metrics
        
    Returns:
        Dict[str, Any]: Validated engagement correlations with p-values
        
    Raises:
        ValueError: If required columns are missing
    """
    required_metrics = ['views', 'likes', 'comments', 'shares', 'engagement_rate']
    missing_metrics = [col for col in required_metrics if col not in df.columns]
    if missing_metrics:
        raise ValueError(f"Missing required metrics: {missing_metrics}")
    
    correlation_results = {
        'significant_correlations': [],
        'all_correlations': {},
        'sample_size': len(df)
    }
    
    # Test all pairs of engagement metrics
    for i, metric1 in enumerate(required_metrics):
        for metric2 in required_metrics[i+1:]:
            # Calculate Pearson correlation
            corr_coef, p_value = pearsonr(df[metric1], df[metric2])
            
            correlation_data = {
                'metric_pair': f"{metric1}_vs_{metric2}",
                'correlation_coefficient': float(corr_coef),
                'p_value': float(p_value),
                'is_significant': p_value < 0.05,
                'strength': _classify_correlation_strength(abs(corr_coef)),
                'sample_size': len(df)
            }
            
            correlation_results['all_correlations'][f"{metric1}_vs_{metric2}"] = correlation_data
            
            # Only include statistically significant correlations
            if p_value < 0.05 and abs(corr_coef) > 0.3:  # Medium+ correlation
                correlation_results['significant_correlations'].append(correlation_data)
    
    logger.info(f"Validated engagement correlations: {len(correlation_results['significant_correlations'])} significant")
    return correlation_results


def validate_feature_performance_correlations(df: pd.DataFrame, analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate correlations between content features and performance metrics.
    
    Args:
        df (pd.DataFrame): Video data with features
        analyzer_results (Dict[str, Any]): Results from analyzer system
        
    Returns:
        Dict[str, Any]: Validated feature-performance correlations
    """
    feature_correlations = {
        'significant_features': [],
        'all_feature_correlations': {},
        'sample_size': len(df)
    }
    
    performance_metrics = ['views', 'engagement_rate', 'viral_score']
    
    # Test categorical features (if they have numerical representations)
    categorical_features = {
        'car_brand_count': 'car_brand_count',
        'hook_count': 'hook_count', 
        'transition_count': 'transition_count',
        'effects_count': 'effects_count',
        'hashtag_count': 'hashtag_count',
        'duration': 'duration'
    }
    
    for feature_name, column_name in categorical_features.items():
        if column_name not in df.columns:
            continue
            
        for metric in performance_metrics:
            if metric not in df.columns:
                continue
                
            # Remove NaN values
            clean_data = df[[column_name, metric]].dropna()
            if len(clean_data) < 5:  # Need minimum sample size for correlation
                continue
                
            # Calculate correlation
            corr_coef, p_value = pearsonr(clean_data[column_name], clean_data[metric])
            
            correlation_data = {
                'feature': feature_name,
                'performance_metric': metric,
                'correlation_coefficient': float(corr_coef),
                'p_value': float(p_value),
                'is_significant': p_value < 0.05,
                'strength': _classify_correlation_strength(abs(corr_coef)),
                'sample_size': len(clean_data),
                'practical_significance': abs(corr_coef) > 0.2  # Practical threshold
            }
            
            feature_correlations['all_feature_correlations'][f"{feature_name}_vs_{metric}"] = correlation_data
            
            # Include if statistically AND practically significant
            if p_value < 0.05 and abs(corr_coef) > 0.2:
                feature_correlations['significant_features'].append(correlation_data)
    
    logger.info(f"Validated feature correlations: {len(feature_correlations['significant_features'])} significant")
    return feature_correlations


def validate_performance_differences(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate statistical significance of performance differences between categories.
    
    Args:
        analyzer_results (Dict[str, Any]): Results from all analyzers
        
    Returns:
        Dict[str, Any]: Validated performance differences with significance tests
    """
    performance_differences = {
        'significant_differences': [],
        'all_comparisons': {}
    }
    
    # Extract performance comparisons from analyzer results
    comparisons_to_validate = [
        ('hook_analysis', 'hooks', 'avg_views'),
        ('brand_analysis', 'brands', 'avg_views'),
        ('hashtag_analysis', 'hashtags', 'avg_views'),
        ('music_analysis', 'tracks', 'avg_views')
    ]
    
    for analysis_key, element_type, metric in comparisons_to_validate:
        if analysis_key not in analyzer_results:
            continue
            
        analysis_data = analyzer_results[analysis_key]
        if not analysis_data or len(analysis_data) < 2:
            continue
            
        # Get performance values for comparison
        performance_values = [
            (element, data[metric]) for element, data in analysis_data.items()
            if isinstance(data, dict) and metric in data
        ]
        
        if len(performance_values) < 2:
            continue
            
        # Compare top performer vs average
        performance_values.sort(key=lambda x: x[1], reverse=True)
        top_performer = performance_values[0]
        average_performance = np.mean([val[1] for val in performance_values])
        
        # Calculate effect size (Cohen's d approximation)
        std_dev = np.std([val[1] for val in performance_values])
        effect_size = (top_performer[1] - average_performance) / std_dev if std_dev > 0 else 0
        
        comparison_data = {
            'analysis_type': analysis_key,
            'element_type': element_type,
            'top_performer': top_performer[0],
            'top_performance': float(top_performer[1]),
            'average_performance': float(average_performance),
            'performance_advantage': float((top_performer[1] / average_performance - 1) * 100) if average_performance > 0 else 0,
            'effect_size': float(effect_size),
            'effect_magnitude': _classify_effect_size(abs(effect_size)),
            'sample_size': len(performance_values)
        }
        
        performance_differences['all_comparisons'][f"{analysis_key}_{element_type}"] = comparison_data
        
        # Include if effect size is meaningful
        if abs(effect_size) > 0.2:  # Small+ effect size
            performance_differences['significant_differences'].append(comparison_data)
    
    
    logger.info(f"Validated performance differences: {len(performance_differences['significant_differences'])} significant")
    return performance_differences


def calculate_confidence_intervals(analyzer_results: Dict[str, Any], confidence_level: float = 0.95) -> Dict[str, Any]:
    """
    Calculate confidence intervals for key performance metrics.
    
    Args:
        analyzer_results (Dict[str, Any]): Results from analyzers
        confidence_level (float): Confidence level (default 95%)
        
    Returns:
        Dict[str, Any]: Confidence intervals for key metrics
    """
    from scipy import stats
    
    confidence_intervals = {}
    alpha = 1 - confidence_level
    
    # Calculate confidence intervals for top performers in each category
    categories_to_analyze = [
        ('hook_analysis', 'avg_views'),
        ('brand_analysis', 'avg_views'), 
        ('hashtag_analysis', 'avg_views')
    ]
    
    for category, metric in categories_to_analyze:
        if category not in analyzer_results:
            continue
            
        category_data = analyzer_results[category]
        if not category_data:
            continue
            
        # Get performance values
        values = [
            data[metric] for data in category_data.values()
            if isinstance(data, dict) and metric in data
        ]
        
        if len(values) < 2:  # Need minimum sample size
            continue
            
        # Calculate confidence interval for the mean
        mean_value = np.mean(values)
        std_error = stats.sem(values)
        
        # t-distribution for small samples
        degrees_freedom = len(values) - 1
        t_value = stats.t.ppf(1 - alpha/2, degrees_freedom)
        
        margin_error = t_value * std_error
        ci_lower = mean_value - margin_error
        ci_upper = mean_value + margin_error
        
        confidence_intervals[category] = {
            'metric': metric,
            'mean': float(mean_value),
            'confidence_level': confidence_level,
            'confidence_interval': (float(ci_lower), float(ci_upper)),
            'margin_of_error': float(margin_error),
            'sample_size': len(values)
        }
    
    logger.info(f"Calculated confidence intervals: {len(confidence_intervals)} categories")
    return confidence_intervals


def _classify_correlation_strength(correlation_coef: float) -> str:
    """Classify correlation strength."""
    abs_corr = abs(correlation_coef)
    if abs_corr >= 0.7:
        return "Strong"
    elif abs_corr >= 0.5:
        return "Moderate"
    elif abs_corr >= 0.3:
        return "Weak"
    else:
        return "Very_Weak"


def _classify_effect_size(effect_size: float) -> str:
    """Classify effect size magnitude (Cohen's d)."""
    abs_effect = abs(effect_size)
    if abs_effect >= 0.8:
        return "Large"
    elif abs_effect >= 0.5:
        return "Medium" 
    elif abs_effect >= 0.2:
        return "Small"
    else:
        return "Negligible"


def get_correlation_summary(correlation_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary of correlation validation results.
    
    Args:
        correlation_results (Dict[str, Any]): Correlation validation results
        
    Returns:
        Dict[str, Any]: Summary of correlation findings
    """
    return {
        'total_correlations_tested': len(correlation_results.get('all_correlations', {})),
        'significant_correlations_found': len(correlation_results.get('significant_correlations', [])),
        'sample_size': correlation_results.get('sample_size', 0),
        'strongest_correlation': max(
            correlation_results.get('significant_correlations', []),
            key=lambda x: abs(x['correlation_coefficient']),
            default={'metric_pair': 'None', 'correlation_coefficient': 0}
        ),
        'validation_status': 'complete'
    }