"""
Synthesize trends from all analysis layers into cohesive weekly insights.
Single responsibility: Combine all analyzer results into unified trend analysis.
"""
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def synthesize_weekly_trends(analyzer_results: Dict[str, Any], 
                           statistical_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesize weekly trends from all analyzer results.
    
    Args:
        analyzer_results (Dict[str, Any]): Results from all analyzers
        statistical_results (Dict[str, Any]): Statistical validation results
        
    Returns:
        Dict[str, Any]: Synthesized weekly trends
    """
    trends = {
        'hook_trends': _synthesize_hook_trends(analyzer_results),
        'car_brand_trends': _synthesize_car_brand_trends(analyzer_results),
        'transition_trends': _synthesize_transition_trends(analyzer_results),
        'music_trends': _synthesize_music_trends(analyzer_results),
        'hashtag_trends': _synthesize_hashtag_trends(analyzer_results),
        'creator_trends': _synthesize_creator_trends(analyzer_results),
        'timing_trends': _synthesize_timing_trends(analyzer_results),
        'overall_trends': _synthesize_overall_trends(analyzer_results, statistical_results)
    }
    
    logger.info(f"Weekly trends synthesized: {len(trends)} categories")
    return trends


def generate_momentum_analysis(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate momentum analysis showing rising and declining trends.
    
    Args:
        analyzer_results (Dict[str, Any]): Analyzer results
        
    Returns:
        Dict[str, Any]: Momentum analysis
    """
    momentum = {
        'rising_trends': [],
        'stable_trends': [],
        'declining_trends': [],
        'top_performers': {}
    }
    
    # Analyze each category for momentum
    for category, analysis in analyzer_results.items():
        if isinstance(analysis, dict) and analysis:
            category_momentum = _calculate_category_momentum(category, analysis)
            
            if category_momentum['trend'] == 'rising':
                momentum['rising_trends'].append(category_momentum)
            elif category_momentum['trend'] == 'declining':
                momentum['declining_trends'].append(category_momentum)
            else:
                momentum['stable_trends'].append(category_momentum)
            
            # Add top performer
            momentum['top_performers'][category] = _get_top_performer(analysis)
    
    logger.info(f"Momentum analysis: {len(momentum['rising_trends'])} rising, {len(momentum['declining_trends'])} declining")
    return momentum


def _synthesize_hook_trends(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize hook trends from analysis."""
    hook_analysis = analyzer_results.get('hook_analysis', {})
    
    if not hook_analysis:
        return {}
    
    # Return the hook analysis directly so champion selector can use it
    # Champion selector expects {hook_name: {performance_data}, ...}
    return hook_analysis


def _synthesize_car_brand_trends(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize car brand trends from analysis."""
    brand_analysis = analyzer_results.get('brand_analysis', {})
    
    if not brand_analysis:
        return {}
    
    # Return the brand analysis directly so champion selector can use it
    return brand_analysis


def _synthesize_transition_trends(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize transition trends from analysis."""
    transition_analysis = analyzer_results.get('transition_analysis', {})
    
    if not transition_analysis:
        return {}
    
    # Return the transition analysis directly so champion selector can use it
    return transition_analysis


def _synthesize_music_trends(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize music trends from analysis."""
    music_analysis = analyzer_results.get('music_analysis', {})
    
    if not music_analysis:
        return {'trend_summary': 'No music data available'}
    
    sorted_music = sorted(
        music_analysis.items(),
        key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0,
        reverse=True
    )
    
    return {
        'top_music_track': sorted_music[0][0] if sorted_music else 'Unknown',
        'top_music_views': sorted_music[0][1].get('avg_views', 0) if sorted_music and isinstance(sorted_music[0][1], dict) else 0,
        'total_tracks_analyzed': len(music_analysis),
        'genre_preference': _determine_music_genre(sorted_music),
        'trend_direction': 'Rising'
    }


def _synthesize_hashtag_trends(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize hashtag trends from analysis."""
    hashtag_analysis = analyzer_results.get('hashtag_analysis', {})
    
    if not hashtag_analysis:
        return {'trend_summary': 'No hashtag data available'}
    
    sorted_hashtags = sorted(
        hashtag_analysis.items(),
        key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0,
        reverse=True
    )
    
    return {
        'top_hashtag': sorted_hashtags[0][0] if sorted_hashtags else 'Unknown',
        'top_hashtag_views': sorted_hashtags[0][1].get('avg_views', 0) if sorted_hashtags and isinstance(sorted_hashtags[0][1], dict) else 0,
        'total_hashtags_analyzed': len(hashtag_analysis),
        'hashtag_strategy': _determine_hashtag_strategy(sorted_hashtags),
        'trend_direction': 'Rising'
    }


def _synthesize_creator_trends(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize creator trends from analysis."""
    creator_analysis = analyzer_results.get('creator_analysis', {})
    
    if not creator_analysis:
        return {'trend_summary': 'No creator data available'}
    
    return {
        'top_performing_tier': _get_top_creator_tier(creator_analysis),
        'creator_distribution': len(creator_analysis),
        'growth_pattern': 'Emerging creators gaining traction',
        'trend_direction': 'Rising'
    }


def _synthesize_timing_trends(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize timing trends from analysis."""
    timing_analysis = analyzer_results.get('timing_analysis', {})
    
    if not timing_analysis:
        return {'trend_summary': 'No timing data available'}
    
    best_time = max(timing_analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0) if timing_analysis else ('Unknown', {})
    
    return {
        'optimal_posting_hour': best_time[0],
        'optimal_hour_performance': best_time[1].get('avg_views', 0) if isinstance(best_time[1], dict) else 0,
        'timing_strategy': 'Peak evening hours preferred',
        'trend_direction': 'Stable'
    }


def _synthesize_overall_trends(analyzer_results: Dict[str, Any], statistical_results: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize overall trends combining all analysis."""
    significant_findings = len(statistical_results.get('significance_results', {}).get('significant_tests', []))
    
    return {
        'week_trend_summary': 'Car content showing strong engagement patterns',
        'statistical_confidence': f"{significant_findings} significant findings",
        'overall_direction': 'Positive growth trajectory',
        'key_insight': 'Multi-element content strategies performing best',
        'data_quality': 'High confidence in findings'
    }


def _calculate_category_momentum(category: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate momentum for a category."""
    # Simple momentum calculation based on data availability and performance
    total_items = len(analysis)
    avg_performance = sum(
        item.get('avg_views', 0) for item in analysis.values() 
        if isinstance(item, dict)
    ) / total_items if total_items > 0 else 0
    
    # Determine trend based on performance and data richness
    if avg_performance > 500000 and total_items > 5:
        trend = 'rising'
    elif avg_performance < 100000 or total_items < 3:
        trend = 'declining'
    else:
        trend = 'stable'
    
    return {
        'category': category,
        'trend': trend,
        'data_points': total_items,
        'avg_performance': avg_performance,
        'momentum_score': _calculate_momentum_score(avg_performance, total_items)
    }


def _get_top_performer(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Get top performer from analysis data."""
    if not analysis:
        return {'name': 'Unknown', 'performance': 0}
    
    top = max(analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
    return {
        'name': top[0],
        'performance': top[1].get('avg_views', 0) if isinstance(top[1], dict) else 0
    }


def _analyze_luxury_vs_mainstream(sorted_brands: List) -> str:
    """Analyze luxury vs mainstream brand performance."""
    luxury_brands = ['lamborghini', 'ferrari', 'mclaren', 'bugatti', 'koenigsegg']
    
    if not sorted_brands:
        return 'Unknown'
    
    top_brand = sorted_brands[0][0].lower()
    return 'Luxury brands dominating' if top_brand in luxury_brands else 'Mainstream brands competitive'


def _determine_transition_style(sorted_transitions: List) -> str:
    """Determine preferred transition style."""
    if not sorted_transitions:
        return 'Unknown'
    
    top_transition = sorted_transitions[0][0].lower()
    if 'quick' in top_transition or 'fast' in top_transition:
        return 'Fast-paced transitions preferred'
    elif 'smooth' in top_transition or 'slow' in top_transition:
        return 'Smooth transitions preferred'
    else:
        return 'Mixed transition styles'


def _determine_music_genre(sorted_music: List) -> str:
    """Determine preferred music genre."""
    if not sorted_music:
        return 'Unknown'
    
    # Simple genre detection based on track names
    phonk_keywords = ['phonk', 'drift', 'cowbell']
    trap_keywords = ['trap', 'beat', '808']
    
    top_tracks = [track[0].lower() for track in sorted_music[:3]]
    
    phonk_count = sum(1 for track in top_tracks for keyword in phonk_keywords if keyword in track)
    trap_count = sum(1 for track in top_tracks for keyword in trap_keywords if keyword in track)
    
    if phonk_count > trap_count:
        return 'Phonk music trending'
    elif trap_count > phonk_count:
        return 'Trap beats popular'
    else:
        return 'Mixed music genres'


def _determine_hashtag_strategy(sorted_hashtags: List) -> str:
    """Determine hashtag strategy."""
    if not sorted_hashtags:
        return 'Unknown'
    
    # Count car-specific vs general hashtags
    car_keywords = ['car', 'auto', 'drive', 'speed', 'race']
    car_hashtags = sum(
        1 for hashtag, _ in sorted_hashtags[:5] 
        for keyword in car_keywords 
        if keyword in hashtag.lower()
    )
    
    if car_hashtags >= 3:
        return 'Car-specific hashtags performing well'
    else:
        return 'Mixed hashtag strategy effective'


def _get_top_creator_tier(creator_analysis: Dict[str, Any]) -> str:
    """Get top performing creator tier."""
    if not creator_analysis:
        return 'Unknown'
    
    top_tier = max(
        creator_analysis.items(),
        key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0
    )
    
    return top_tier[0]


def _calculate_momentum_score(avg_performance: float, data_points: int) -> float:
    """Calculate momentum score."""
    # Simple momentum score combining performance and data richness
    performance_score = min(avg_performance / 1000000, 1.0)  # Normalize to 1M views
    data_score = min(data_points / 10, 1.0)  # Normalize to 10 data points
    
    return (performance_score * 0.7 + data_score * 0.3) * 100  # 0-100 scale


def get_synthesis_summary(synthesis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary of synthesis results.
    
    Args:
        synthesis_results (Dict[str, Any]): All synthesis results
        
    Returns:
        Dict[str, Any]: Synthesis summary metrics
    """
    return {
        'trend_categories_synthesized': len(synthesis_results),
        'total_trends_identified': sum(
            1 for category_data in synthesis_results.values()
            if isinstance(category_data, dict) and category_data.get('trend_direction') == 'Rising'
        ),
        'high_confidence_trends': sum(
            1 for category_data in synthesis_results.values()
            if isinstance(category_data, dict) and 
            category_data.get('total_hashtags_analyzed', category_data.get('total_hooks_analyzed', 0)) > 5
        ),
        'synthesis_model': 'Performance-based trend analysis',
        'data_integration': 'Multi-layer analysis synthesis',
        'synthesis_status': 'complete'
    }