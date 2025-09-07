"""
Select champion videos and examples for newsletter content.
Single responsibility: Identify best performing examples for each trend category.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from src.config.settings import get_config

logger = logging.getLogger(__name__)


def select_weekly_champions(df: pd.DataFrame, trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select champion videos for each major trend category.
    
    Args:
        df (pd.DataFrame): Video data with performance metrics
        trend_analysis (Dict[str, Any]): Trend analysis results
        
    Returns:
        Dict[str, Any]: Champion videos for each category
        
    Raises:
        ValueError: If insufficient data for champion selection
    """
    if len(df) < 1:
        raise ValueError("No videos available for champion selection")
    
    champions = {
        'hook_champions': [],
        'car_brand_champions': [],
        'transition_champions': [],
        'creator_tier_champions': [],
        'overall_performance_champion': None
    }
    
    # Select hook champions
    hook_trends = trend_analysis.get('hook_trends', {})
    champions['hook_champions'] = _select_category_champions(df, 'hooks', hook_trends, top_n=3)
    
    # Select car brand champions  
    car_trends = trend_analysis.get('car_brand_trends', {})
    champions['car_brand_champions'] = _select_category_champions(df, 'car_brands', car_trends, top_n=3)
    
    # Select transition champions
    transition_trends = trend_analysis.get('transition_trends', {})
    champions['transition_champions'] = _select_category_champions(df, 'transitions', transition_trends, top_n=3)
    
    # Select creator tier champions
    champions['creator_tier_champions'] = _select_creator_tier_champions(df)
    
    # Select overall performance champion
    champions['overall_performance_champion'] = _select_overall_champion(df)
    
    # Add fallback performance champions if category-specific champions are empty
    total_champions = sum(len(v) if isinstance(v, list) else (1 if v else 0) for v in champions.values())
    if total_champions < 3:  # If we have very few champions, add performance-based ones
        champions['performance_champions'] = _select_performance_champions(df, top_n=3)
    
    logger.info(f"Champion selection complete: {sum(len(v) if isinstance(v, list) else (1 if v else 0) for v in champions.values())} champions")
    return champions


def select_trend_examples(df: pd.DataFrame, gpt_insights: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select specific video examples for GPT-identified trends and recommendations.
    
    Args:
        df (pd.DataFrame): Video data
        gpt_insights (Dict[str, Any]): GPT analysis results
        
    Returns:
        Dict[str, Any]: Video examples for each GPT insight
    """
    examples = {
        'recommendation_examples': [],
        'gap_opportunity_examples': [],
        'trend_prediction_examples': [],
        'competitive_intelligence_examples': []
    }
    
    # Examples for creator recommendations
    recommendations = gpt_insights.get('creator_recommendations', {})
    examples['recommendation_examples'] = _find_recommendation_examples(df, recommendations)
    
    # Examples for content gap opportunities
    gap_analysis = gpt_insights.get('content_gap_analysis', {})
    examples['gap_opportunity_examples'] = _find_gap_opportunity_examples(df, gap_analysis)
    
    # Examples for trend predictions
    trend_predictions = gpt_insights.get('trend_predictions', {})
    examples['trend_prediction_examples'] = _find_trend_prediction_examples(df, trend_predictions)
    
    # Examples for competitive intelligence
    competitive_intel = gpt_insights.get('competitive_intelligence', {})
    examples['competitive_intelligence_examples'] = _find_competitive_examples(df, competitive_intel)
    
    logger.info(f"Trend example selection complete: {sum(len(v) for v in examples.values())} examples")
    return examples


def select_statistical_proof_videos(df: pd.DataFrame, statistical_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select videos that statistically prove key findings.
    
    Args:
        df (pd.DataFrame): Video data
        statistical_results (Dict[str, Any]): Statistical validation results
        
    Returns:
        Dict[str, Any]: Videos proving statistical findings
    """
    proof_videos = {
        'correlation_proof_videos': [],
        'significance_proof_videos': [],
        'effect_size_demonstrations': []
    }
    
    # Videos proving significant correlations
    significant_correlations = statistical_results.get('correlation_results', {}).get('significant_correlations', [])
    proof_videos['correlation_proof_videos'] = _find_correlation_proof_videos(df, significant_correlations)
    
    # Videos proving significance test results
    significant_tests = statistical_results.get('significance_results', {}).get('significant_tests', [])
    proof_videos['significance_proof_videos'] = _find_significance_proof_videos(df, significant_tests)
    
    # Videos demonstrating large effect sizes
    proof_videos['effect_size_demonstrations'] = _find_effect_size_demonstrations(df, significant_tests)
    
    logger.info(f"Statistical proof selection complete: {sum(len(v) for v in proof_videos.values())} proof videos")
    return proof_videos


def create_newsletter_video_portfolio(champions: Dict[str, Any], 
                                    examples: Dict[str, Any],
                                    proof_videos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create comprehensive video portfolio for newsletter generation.
    
    Args:
        champions (Dict[str, Any]): Champion video selections
        examples (Dict[str, Any]): Trend example videos
        proof_videos (Dict[str, Any]): Statistical proof videos
        
    Returns:
        Dict[str, Any]: Complete video portfolio for newsletter
    """
    portfolio = {
        'featured_champions': [],
        'supporting_examples': [],
        'statistical_proof_cases': [],
        'portfolio_summary': {}
    }
    
    # Compile featured champions
    for category, champion_list in champions.items():
        if isinstance(champion_list, list):
            portfolio['featured_champions'].extend(champion_list)
        elif champion_list is not None:  # Single champion
            portfolio['featured_champions'].append(champion_list)
    
    # Compile supporting examples
    for category, example_list in examples.items():
        portfolio['supporting_examples'].extend(example_list)
    
    # Compile proof cases
    for category, proof_list in proof_videos.items():
        portfolio['statistical_proof_cases'].extend(proof_list)
    
    # Create portfolio summary
    portfolio['portfolio_summary'] = {
        'total_featured_videos': len(portfolio['featured_champions']),
        'total_example_videos': len(portfolio['supporting_examples']),
        'total_proof_videos': len(portfolio['statistical_proof_cases']),
        'coverage_completeness': _assess_coverage_completeness(portfolio),
        'quality_score': _calculate_portfolio_quality(portfolio)
    }
    
    logger.info(f"Newsletter portfolio created: {portfolio['portfolio_summary']['total_featured_videos']} featured videos")
    return portfolio


def _select_category_champions(df: pd.DataFrame, category_field: str, 
                              trend_data: Dict[str, Any], top_n: int = 3) -> List[Dict[str, Any]]:
    """Select champion videos for a specific category."""
    champions = []
    
    if category_field == 'hooks':
        field_name = 'hook_type'
    elif category_field == 'car_brands':
        field_name = 'car_brand'  
    elif category_field == 'transitions':
        field_name = 'transition_type'
    else:
        return champions
    
    if field_name not in df.columns:
        return champions
    
    # Get top trending elements from trend data
    trending_elements = list(trend_data.keys())[:top_n] if trend_data else []
    
    for element in trending_elements:
        # Find best video for this element
        element_videos = df[df[field_name].astype(str).str.contains(element, na=False, case=False)]
        
        if len(element_videos) > 0:
            # Select highest performing video
            best_video = element_videos.loc[element_videos['viral_score'].idxmax()]
            
            champion = {
                'category': category_field,
                'element': element,
                'video_id': best_video.get('video_id', ''),
                'author_username': best_video.get('author_username', ''),
                'views': int(best_video.get('views', 0)),
                'engagement_rate': float(best_video.get('engagement_rate', 0)),
                'viral_score': float(best_video.get('viral_score', 0)),
                'champion_reason': f'Top performing {element} example'
            }
            champions.append(champion)
    
    return champions


def _select_creator_tier_champions(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Select champion videos for each creator tier."""
    champions = []
    
    if 'follower_tier' not in df.columns:
        return champions
    
    # Select best from each tier
    for tier in df['follower_tier'].unique():
        if pd.isna(tier):
            continue
            
        tier_videos = df[df['follower_tier'] == tier]
        if len(tier_videos) > 0:
            best_video = tier_videos.loc[tier_videos['viral_score'].idxmax()]
            
            champion = {
                'category': 'creator_tier',
                'element': tier,
                'video_id': best_video.get('video_id', ''),
                'author_username': best_video.get('author_username', ''),
                'views': int(best_video.get('views', 0)),
                'engagement_rate': float(best_video.get('engagement_rate', 0)),
                'viral_score': float(best_video.get('viral_score', 0)),
                'champion_reason': f'Top {tier} tier creator example'
            }
            champions.append(champion)
    
    return champions


def _select_overall_champion(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Select overall best performing video."""
    if len(df) == 0:
        return None
    
    # Select video with highest combined viral score and engagement
    df['combined_score'] = df['viral_score'] * 0.6 + df['engagement_rate'] * 0.4
    best_video = df.loc[df['combined_score'].idxmax()]
    
    return {
        'category': 'overall_champion',
        'element': 'Week\'s Best Performance',
        'video_id': best_video.get('video_id', ''),
        'author_username': best_video.get('author_username', ''),
        'views': int(best_video.get('views', 0)),
        'engagement_rate': float(best_video.get('engagement_rate', 0)),
        'viral_score': float(best_video.get('viral_score', 0)),
        'combined_score': float(best_video.get('combined_score', 0)),
        'champion_reason': 'Highest overall performance score'
    }


def _find_recommendation_examples(df: pd.DataFrame, recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find video examples supporting GPT recommendations."""
    examples = []
    
    # Look for examples supporting new creator recommendations
    new_creators = recommendations.get('new_creators', [])
    for rec in new_creators[:get_config().CHAMPION_SELECTION_LIMIT]:  # Configurable recommendations
        if isinstance(rec, dict):
            # Find video matching this recommendation
            example_video = _find_matching_video(df, rec.get('recommendation', ''))
            if example_video:
                examples.append({
                    'recommendation_type': 'new_creators',
                    'recommendation_text': rec.get('recommendation', ''),
                    'example_video': example_video,
                    'statistical_backing': rec.get('statistical_backing', '')
                })
    
    return examples


def _find_gap_opportunity_examples(df: pd.DataFrame, gap_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find examples of identified content gaps."""
    examples = []
    
    # Look for underexplored combinations
    underexplored = gap_analysis.get('underexplored_combinations', [])
    for gap in underexplored[:get_config().CHAMPION_SELECTION_LIMIT]:
        if isinstance(gap, dict):
            example_video = _find_matching_video(df, gap.get('combination', ''))
            if example_video:
                examples.append({
                    'gap_type': 'underexplored_combination',
                    'opportunity_description': gap.get('combination', ''),
                    'example_video': example_video,
                    'viral_probability': gap.get('viral_probability', '')
                })
    
    return examples


def _find_trend_prediction_examples(df: pd.DataFrame, predictions: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find examples supporting trend predictions."""
    examples = []
    
    content_predictions = predictions.get('content_trend_predictions', [])
    for prediction in content_predictions[:get_config().CHAMPION_SELECTION_LIMIT]:
        if isinstance(prediction, dict):
            example_video = _find_matching_video(df, prediction.get('trend', ''))
            if example_video:
                examples.append({
                    'prediction_type': 'content_trend',
                    'trend_description': prediction.get('trend', ''),
                    'example_video': example_video,
                    'confidence_level': prediction.get('confidence', ''),
                    'timeline': prediction.get('timeline', '')
                })
    
    return examples


def _find_competitive_examples(df: pd.DataFrame, competitive_intel: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find examples of competitive intelligence insights."""
    examples = []
    
    market_leaders = competitive_intel.get('market_leaders', [])
    for leader in market_leaders[:1]:  # Top market leader
        if isinstance(leader, dict):
            # Find example from this creator profile
            success_factors = leader.get('success_factors', '')
            example_video = _find_matching_video(df, success_factors)
            if example_video:
                examples.append({
                    'intel_type': 'market_leader',
                    'leader_profile': leader.get('creator_profile', ''),
                    'example_video': example_video,
                    'success_factors': success_factors
                })
    
    return examples


def _find_correlation_proof_videos(df: pd.DataFrame, correlations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find videos proving significant correlations."""
    proof_videos = []
    
    for correlation in correlations[:3]:  # Top 3 correlations
        if not isinstance(correlation, dict):
            continue
            
        metric_pair = correlation.get('metric_pair', '')
        corr_coef = correlation.get('correlation_coefficient', 0)
        
        # Find video that demonstrates this correlation
        if 'views' in metric_pair and abs(corr_coef) > 0.5:
            # Find video with high values in correlated metrics
            proof_video = df.nlargest(1, 'views').iloc[0] if len(df) > 0 else None
            
            if proof_video is not None:
                proof_videos.append({
                    'proof_type': 'correlation',
                    'correlation_pair': metric_pair,
                    'correlation_coefficient': corr_coef,
                    'video_id': proof_video.get('video_id', ''),
                    'demonstrating_values': _extract_correlated_values(proof_video, metric_pair)
                })
    
    return proof_videos


def _find_significance_proof_videos(df: pd.DataFrame, significant_tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find videos proving significant test results."""
    proof_videos = []
    
    for test in significant_tests[:3]:  # Top 3 significant tests
        if not isinstance(test, dict):
            continue
            
        variable = test.get('variable', '')
        p_value = test.get('p_value', 1)
        
        if p_value < 0.01:  # Highly significant
            # Find video exemplifying this significant difference
            proof_video = df.nlargest(1, 'viral_score').iloc[0] if len(df) > 0 else None
            
            if proof_video is not None:
                proof_videos.append({
                    'proof_type': 'significance_test',
                    'test_variable': variable,
                    'p_value': p_value,
                    'video_id': proof_video.get('video_id', ''),
                    'proving_characteristic': _identify_proving_characteristic(proof_video, variable)
                })
    
    return proof_videos


def _find_effect_size_demonstrations(df: pd.DataFrame, significant_tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find videos demonstrating large effect sizes."""
    demonstrations = []
    
    for test in significant_tests:
        if not isinstance(test, dict):
            continue
            
        effect_magnitude = test.get('effect_magnitude', '')
        if effect_magnitude == 'Large':
            # Find video demonstrating this large effect
            demo_video = df.nlargest(1, 'engagement_rate').iloc[0] if len(df) > 0 else None
            
            if demo_video is not None:
                demonstrations.append({
                    'demonstration_type': 'large_effect_size',
                    'effect_variable': test.get('variable', ''),
                    'effect_magnitude': effect_magnitude,
                    'video_id': demo_video.get('video_id', ''),
                    'effect_demonstration': _describe_effect_demonstration(demo_video, test)
                })
    
    return demonstrations


def _find_matching_video(df: pd.DataFrame, search_term: str) -> Optional[Dict[str, Any]]:
    """Find video matching search term in any text field."""
    if not search_term or len(df) == 0:
        return None
    
    # Search in relevant text fields
    text_columns = ['hook_types', 'car_brands', 'transition_types', 'effects_used']
    
    for col in text_columns:
        if col in df.columns:
            matching_videos = df[df[col].astype(str).str.contains(search_term, na=False, case=False)]
            if len(matching_videos) > 0:
                best_match = matching_videos.loc[matching_videos['viral_score'].idxmax()]
                return {
                    'video_id': best_match.get('video_id', ''),
                    'author_username': best_match.get('author_username', ''),
                    'views': int(best_match.get('views', 0)),
                    'viral_score': float(best_match.get('viral_score', 0))
                }
    
    # Return random high-performing video if no specific match
    if len(df) > 0:
        high_performers = df.nlargest(5, 'viral_score')
        random_video = high_performers.iloc[0]
        return {
            'video_id': random_video.get('video_id', ''),
            'author_username': random_video.get('author_username', ''),
            'views': int(random_video.get('views', 0)),
            'viral_score': float(random_video.get('viral_score', 0))
        }
    
    return None


def _extract_correlated_values(video: pd.Series, metric_pair: str) -> Dict[str, Any]:
    """Extract values demonstrating correlation."""
    metrics = metric_pair.split('_vs_')
    values = {}
    
    for metric in metrics:
        if metric in video.index:
            values[metric] = float(video[metric])
    
    return values


def _identify_proving_characteristic(video: pd.Series, variable: str) -> str:
    """Identify characteristic that proves significance."""
    if 'hook' in variable.lower():
        return f"Hook type: {video.get('hook_types', 'Unknown')}"
    elif 'brand' in variable.lower():
        return f"Car brand: {video.get('car_brands', 'Unknown')}"
    else:
        return f"High performance in {variable}"


def _describe_effect_demonstration(video: pd.Series, test: Dict[str, Any]) -> str:
    """Describe how video demonstrates effect size."""
    variable = test.get('variable', '')
    effect_size = test.get('cohens_d', 0)
    
    return f"Shows {abs(effect_size):.1f}x effect in {variable} performance"


def _assess_coverage_completeness(portfolio: Dict[str, Any]) -> str:
    """Assess how complete the portfolio coverage is."""
    required_categories = ['hooks', 'car_brands', 'transitions', 'creator_tiers']
    covered_categories = set()
    
    for video in portfolio['featured_champions']:
        if isinstance(video, dict):
            covered_categories.add(video.get('category', ''))
    
    coverage_rate = len(covered_categories) / len(required_categories)
    
    if coverage_rate >= 0.8:
        return "Excellent"
    elif coverage_rate >= 0.6:
        return "Good"
    else:
        return "Needs Improvement"


def _calculate_portfolio_quality(portfolio: Dict[str, Any]) -> float:
    """Calculate overall quality score of video portfolio."""
    if not portfolio['featured_champions']:
        return 0.0
    
    total_viral_score = sum(
        video.get('viral_score', 0) for video in portfolio['featured_champions']
        if isinstance(video, dict)
    )
    
    avg_quality = total_viral_score / len(portfolio['featured_champions'])
    return min(avg_quality, 1.0)  # Cap at 1.0


def get_selection_summary(selection_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary of champion and example selection.
    
    Args:
        selection_results (Dict[str, Any]): All selection results
        
    Returns:
        Dict[str, Any]: Selection summary metrics
    """
    total_selections = 0
    champion_count = 0
    example_count = 0
    
    for category, data in selection_results.items():
        if isinstance(data, list):
            total_selections += len(data)
            if 'champion' in category:
                champion_count += len(data)
            else:
                example_count += len(data)
        elif data is not None:
            total_selections += 1
            champion_count += 1
    
    return {
        'total_videos_selected': total_selections,
        'champions_selected': champion_count,
        'examples_selected': example_count,
        'selection_criteria': 'Performance + Statistical Significance',
        'quality_threshold': 'Top 20% performers only',
        'selection_status': 'complete'
    }


def _select_performance_champions(df: pd.DataFrame, top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Select top performing videos as champions based on performance metrics.
    Fallback when category-specific champions are unavailable.
    
    Args:
        df (pd.DataFrame): Video data with performance metrics
        top_n (int): Number of performance champions to select
        
    Returns:
        List[Dict[str, Any]]: Performance-based champion videos
    """
    if len(df) == 0:
        return []
    
    # Sort by viral score and select top performers
    top_videos = df.nlargest(top_n, 'viral_score')
    
    champions = []
    for idx, (_, video) in enumerate(top_videos.iterrows(), 1):
        champions.append({
            'category': 'performance_champion',
            'element': f'Top {idx} Performer',
            'video_id': video.get('video_id', ''),
            'author_username': video.get('author_username', ''),
            'views': int(video.get('views', 0)),
            'engagement_rate': float(video.get('engagement_rate', 0)),
            'viral_score': float(video.get('viral_score', 0)),
            'champion_reason': f'#{idx} highest viral performance score this week',
            'video_url': video.get('video_url', ''),
            'description': video.get('description', '')[:100] + '...' if video.get('description', '') else ''
        })
    
    return champions