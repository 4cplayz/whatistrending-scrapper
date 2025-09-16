"""
Statistical significance testing for content performance differences.
Single responsibility: Chi-square tests, t-tests, and significance validation.
"""
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, ttest_ind, mannwhitneyu, kruskal
from scipy.stats import chi2
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


def test_categorical_performance_differences(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Test performance differences between categorical variables using chi-square tests.
    
    Args:
        df (pd.DataFrame): Video data with categorical features and performance metrics
        
    Returns:
        Dict[str, Any]: Chi-square test results with significance levels
        
    Raises:
        ValueError: If required columns are missing
    """
    if 'views' not in df.columns or 'engagement_rate' not in df.columns:
        raise ValueError("Performance metrics (views, engagement_rate) required")
    
    significance_results = {
        'significant_tests': [],
        'all_tests': {},
        'sample_size': len(df)
    }
    
    # Create performance quartiles for testing
    df['performance_quartile'] = pd.qcut(
        df['views'], 
        q=4, 
        labels=['Low', 'Medium_Low', 'Medium_High', 'High'],
        duplicates='drop'
    )
    
    # Test categorical variables against performance
    categorical_variables = [
        'car_brand', 'hook_type', 'transition_type', 'edit_style',
        'music_type', 'engagement_tier'
    ]
    
    for variable in categorical_variables:
        if variable not in df.columns:
            continue
            
        # Filter out rows with missing values
        test_data = df.dropna(subset=[variable, 'performance_quartile'])
        if len(test_data) < 3:  # Lower threshold for small datasets
            continue
            
        # Create contingency table
        contingency_table = pd.crosstab(test_data[variable], test_data['performance_quartile'])
        
        # Skip if table is too sparse - relaxed for small datasets
        if contingency_table.size < 2 or (contingency_table < 2).sum().sum() > contingency_table.size * 0.5:
            continue
            
        try:
            # Perform chi-square test
            chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)
            
            # Calculate effect size (Cramer's V)
            n = contingency_table.sum().sum()
            cramers_v = np.sqrt(chi2_stat / (n * (min(contingency_table.shape) - 1)))
            
            test_result = {
                'variable': variable,
                'test_type': 'chi_square',
                'chi2_statistic': float(chi2_stat),
                'p_value': float(p_value),
                'degrees_of_freedom': int(dof),
                'is_significant': p_value < 0.05,
                'effect_size_cramers_v': float(cramers_v),
                'effect_magnitude': _classify_cramers_v(cramers_v),
                'sample_size': int(n),
                'contingency_table': contingency_table.to_dict()
            }
            
            significance_results['all_tests'][variable] = test_result
            
            # Include if statistically significant
            if p_value < 0.05:
                significance_results['significant_tests'].append(test_result)
                
        except Exception as e:
            logger.warning(f"Chi-square test failed for {variable}: {e}")
            continue
    
    logger.info(f"Completed categorical significance tests: {len(significance_results['significant_tests'])} significant")
    return significance_results


def test_numerical_performance_differences(df: pd.DataFrame, analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test performance differences between numerical variables using t-tests.
    
    Args:
        df (pd.DataFrame): Video data with numerical features
        analyzer_results (Dict[str, Any]): Results from analyzers for group comparisons
        
    Returns:
        Dict[str, Any]: T-test results with significance levels
    """
    numerical_tests = {
        'significant_tests': [],
        'all_tests': {},
        'sample_size': len(df)
    }
    
    # Test binary comparisons
    binary_comparisons = [
        ('multi_brand_video', 'Multi-brand vs Single-brand'),
        ('multi_hook_video', 'Multi-hook vs Single-hook'), 
        ('has_car_hashtags', 'Car hashtags vs No car hashtags'),
        ('author_verified', 'Verified vs Unverified creators')
    ]
    
    performance_metrics = ['views', 'engagement_rate', 'viral_score']
    
    for binary_column, comparison_name in binary_comparisons:
        if binary_column not in df.columns:
            continue
            
        for metric in performance_metrics:
            if metric not in df.columns:
                continue
                
            # Split into two groups
            group_true = df[df[binary_column] == True][metric].dropna()
            group_false = df[df[binary_column] == False][metric].dropna()
            
            if len(group_true) < 2 or len(group_false) < 2:  # Lower threshold for small datasets
                continue
                
            try:
                # Perform independent t-test
                t_stat, p_value = ttest_ind(group_true, group_false)
                
                # Calculate effect size (Cohen's d)
                pooled_std = np.sqrt(((len(group_true) - 1) * group_true.var() + 
                                    (len(group_false) - 1) * group_false.var()) / 
                                   (len(group_true) + len(group_false) - 2))
                cohens_d = (group_true.mean() - group_false.mean()) / pooled_std if pooled_std > 0 else 0
                
                test_result = {
                    'comparison': comparison_name,
                    'metric': metric,
                    'test_type': 't_test',
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'is_significant': p_value < 0.05,
                    'cohens_d': float(cohens_d),
                    'effect_magnitude': _classify_cohens_d(abs(cohens_d)),
                    'group_true_mean': float(group_true.mean()),
                    'group_false_mean': float(group_false.mean()),
                    'group_true_size': len(group_true),
                    'group_false_size': len(group_false),
                    'practical_significance': abs(cohens_d) > 0.2
                }
                
                numerical_tests['all_tests'][f"{binary_column}_{metric}"] = test_result
                
                # Include if statistically significant
                if p_value < 0.05:
                    numerical_tests['significant_tests'].append(test_result)
                    
            except Exception as e:
                logger.warning(f"T-test failed for {binary_column} vs {metric}: {e}")
                continue
    
    logger.info(f"Completed numerical significance tests: {len(numerical_tests['significant_tests'])} significant")
    return numerical_tests


def test_multi_group_differences(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Test performance differences between multiple groups using Kruskal-Wallis test.
    
    Args:
        df (pd.DataFrame): Video data with multi-category features
        
    Returns:
        Dict[str, Any]: Multi-group test results
    """
    multi_group_tests = {
        'significant_tests': [],
        'all_tests': {},
        'sample_size': len(df)
    }
    
    # Test multi-category variables
    multi_category_variables = [
        'car_brand', 'hook_type', 'transition_type', 'edit_style',
        'engagement_tier', 'duration_category'
    ]
    
    performance_metrics = ['views', 'engagement_rate']
    
    for variable in multi_category_variables:
        if variable not in df.columns:
            continue
            
        for metric in performance_metrics:
            if metric not in df.columns:
                continue
                
            # Get groups for this variable
            groups = []
            group_names = []
            
            for category in df[variable].dropna().unique():
                group_data = df[df[variable] == category][metric].dropna()
                if len(group_data) >= 2:  # Lower threshold for small datasets
                    groups.append(group_data)
                    group_names.append(category)
            
            if len(groups) < 2:  # Need at least 2 groups for comparison
                continue
                
            try:
                # Perform Kruskal-Wallis test (non-parametric ANOVA)
                h_stat, p_value = kruskal(*groups)
                
                # Calculate eta-squared (effect size for Kruskal-Wallis)
                n = sum(len(group) for group in groups)
                eta_squared = (h_stat - len(groups) + 1) / (n - len(groups)) if n > len(groups) else 0
                
                test_result = {
                    'variable': variable,
                    'metric': metric,
                    'test_type': 'kruskal_wallis',
                    'h_statistic': float(h_stat),
                    'p_value': float(p_value),
                    'is_significant': p_value < 0.05,
                    'eta_squared': float(eta_squared),
                    'effect_magnitude': _classify_eta_squared(eta_squared),
                    'num_groups': len(groups),
                    'total_sample_size': int(n),
                    'group_sizes': [len(group) for group in groups],
                    'group_means': [float(group.mean()) for group in groups],
                    'group_names': group_names
                }
                
                multi_group_tests['all_tests'][f"{variable}_{metric}"] = test_result
                
                # Include if statistically significant
                if p_value < 0.05:
                    multi_group_tests['significant_tests'].append(test_result)
                    
            except Exception as e:
                logger.warning(f"Kruskal-Wallis test failed for {variable} vs {metric}: {e}")
                continue
    
    logger.info(f"Completed multi-group tests: {len(multi_group_tests['significant_tests'])} significant")
    return multi_group_tests


def validate_statistical_power(test_results: Dict[str, Any], minimum_power: float = 0.8) -> Dict[str, Any]:
    """
    Validate statistical power of significant test results.
    
    Args:
        test_results (Dict[str, Any]): Combined test results from significance testing
        minimum_power (float): Minimum acceptable statistical power
        
    Returns:
        Dict[str, Any]: Power analysis results
    """
    power_analysis = {
        'high_power_tests': [],
        'low_power_warnings': [],
        'power_threshold': minimum_power
    }
    
    # Check sample sizes and effect sizes for adequate power
    all_tests = []
    
    # Collect all significant tests
    for test_category in ['significant_tests', 'all_tests']:
        if test_category in test_results:
            if isinstance(test_results[test_category], list):
                all_tests.extend(test_results[test_category])
            elif isinstance(test_results[test_category], dict):
                all_tests.extend(test_results[test_category].values())
    
    for test in all_tests:
        if not isinstance(test, dict):
            continue
            
        # Estimate power based on sample size and effect size
        sample_size = test.get('sample_size', test.get('total_sample_size', 0))
        
        # Get effect size (different for different tests)
        if 'cohens_d' in test:
            effect_size = abs(test['cohens_d'])
            power_estimate = _estimate_power_t_test(sample_size, effect_size)
        elif 'cramers_v' in test:
            effect_size = test['cramers_v']
            power_estimate = _estimate_power_chi_square(sample_size, effect_size)
        elif 'eta_squared' in test:
            effect_size = test['eta_squared']
            power_estimate = _estimate_power_kruskal(sample_size, effect_size)
        else:
            power_estimate = 0.5  # Conservative estimate
        
        power_result = {
            'test_info': test,
            'estimated_power': power_estimate,
            'adequate_power': power_estimate >= minimum_power
        }
        
        if power_estimate >= minimum_power:
            power_analysis['high_power_tests'].append(power_result)
        else:
            power_analysis['low_power_warnings'].append(power_result)
    
    logger.info(f"Power analysis: {len(power_analysis['high_power_tests'])} high power, {len(power_analysis['low_power_warnings'])} low power")
    return power_analysis


def _classify_cramers_v(cramers_v: float) -> str:
    """Classify Cramer's V effect size."""
    if cramers_v >= 0.3:
        return "Large"
    elif cramers_v >= 0.15:
        return "Medium"
    elif cramers_v >= 0.1:
        return "Small"
    else:
        return "Negligible"


def _classify_cohens_d(cohens_d: float) -> str:
    """Classify Cohen's d effect size."""
    abs_d = abs(cohens_d)
    if abs_d >= 0.8:
        return "Large"
    elif abs_d >= 0.5:
        return "Medium"
    elif abs_d >= 0.2:
        return "Small"
    else:
        return "Negligible"


def _classify_eta_squared(eta_squared: float) -> str:
    """Classify eta-squared effect size."""
    if eta_squared >= 0.14:
        return "Large"
    elif eta_squared >= 0.06:
        return "Medium"
    elif eta_squared >= 0.01:
        return "Small"
    else:
        return "Negligible"


def _estimate_power_t_test(sample_size: int, effect_size: float) -> float:
    """Rough power estimation for t-test."""
    if sample_size < 10:
        return 0.1
    elif effect_size > 0.8 and sample_size > 20:
        return 0.9
    elif effect_size > 0.5 and sample_size > 15:
        return 0.8
    elif effect_size > 0.2 and sample_size > 25:
        return 0.7
    else:
        return 0.4


def _estimate_power_chi_square(sample_size: int, effect_size: float) -> float:
    """Rough power estimation for chi-square test."""
    if sample_size < 20:
        return 0.3
    elif effect_size > 0.3 and sample_size > 50:
        return 0.9
    elif effect_size > 0.15 and sample_size > 100:
        return 0.8
    else:
        return 0.6


def _estimate_power_kruskal(sample_size: int, effect_size: float) -> float:
    """Rough power estimation for Kruskal-Wallis test."""
    if sample_size < 15:
        return 0.4
    elif effect_size > 0.14 and sample_size > 30:
        return 0.8
    elif effect_size > 0.06 and sample_size > 50:
        return 0.7
    else:
        return 0.5


def get_significance_summary(all_test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary of all significance testing results.
    
    Args:
        all_test_results (List[Dict[str, Any]]): All test results from significance testing
        
    Returns:
        Dict[str, Any]: Summary of significance findings
    """
    total_tests = sum(len(result.get('all_tests', {})) for result in all_test_results)
    total_significant = sum(len(result.get('significant_tests', [])) for result in all_test_results)
    
    return {
        'total_tests_performed': total_tests,
        'significant_results_found': total_significant,
        'significance_rate': total_significant / total_tests if total_tests > 0 else 0,
        'alpha_level': 0.05,
        'validation_status': 'complete'
    }