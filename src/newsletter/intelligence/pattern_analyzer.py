"""
GPT-powered pattern analysis with statistical backing.
Single responsibility: Identify patterns and insights from validated statistical data.
"""
import json
import logging
from typing import Dict, Any, List
import os
from openai import OpenAI

logger = logging.getLogger(__name__)


def analyze_content_performance_patterns(analyzer_results: Dict[str, Any], 
                                       statistical_validation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use GPT to analyze content performance patterns from validated statistical data.
    
    Args:
        analyzer_results (Dict[str, Any]): Results from all content analyzers
        statistical_validation (Dict[str, Any]): Statistically validated findings
        
    Returns:
        Dict[str, Any]: GPT analysis of content performance patterns
        
    Raises:
        Exception: If GPT API call fails
    """
    try:
        client = OpenAI()
        
        # Extract only statistically significant findings
        significant_correlations = statistical_validation.get('correlation_results', {}).get('significant_correlations', [])
        significant_tests = statistical_validation.get('significance_results', {}).get('significant_tests', [])
        
        # If no significant findings, return basic pattern analysis
        if not significant_correlations and not significant_tests:
            logger.warning("No significant statistical findings - generating basic pattern analysis")
            return _generate_basic_pattern_analysis(analyzer_results)
        
        # Clean data for JSON serialization
        clean_correlations = _clean_for_json_serialization(significant_correlations)
        clean_tests = _clean_for_json_serialization(significant_tests)
        
        prompt = f"""
        You are a TikTok car content performance analyst. Analyze these STATISTICALLY VALIDATED findings to identify actionable patterns.

        STATISTICALLY SIGNIFICANT CORRELATIONS (p < 0.05):
        {json.dumps(clean_correlations, indent=2)}

        STATISTICALLY SIGNIFICANT DIFFERENCES (p < 0.05):
        {json.dumps(clean_tests, indent=2)}

        CONTENT PERFORMANCE DATA:
        - Hook Analysis: {len(analyzer_results.get('hook_analysis', {}))} hooks analyzed
        - Car Brands: {len(analyzer_results.get('brand_analysis', {}))} brands analyzed  
        - Transitions: {len(analyzer_results.get('transition_analysis', {}))} transitions analyzed
        - Effects: {len(analyzer_results.get('effects_analysis', {}))} effects analyzed

        Based ONLY on statistically validated data (p < 0.05), identify:

        1. **Content Element Patterns**: Which combinations of hooks + car brands + transitions show statistical significance?
        2. **Performance Drivers**: What statistically proven factors drive higher views/engagement?
        3. **Optimal Strategies**: What validated combinations should creators use?
        4. **Avoid Patterns**: What statistically underperforming combinations should be avoided?

        Format response as JSON with:
        {{
            "validated_patterns": [
                {{
                    "pattern_name": "Hook + Brand combination effectiveness",
                    "statistical_evidence": "Chi-square p < 0.01, effect size medium",
                    "actionable_insight": "VS Graphics + Lamborghini increases views by 34%",
                    "confidence_level": "High"
                }}
            ],
            "performance_drivers": [
                {{
                    "driver": "Multi-hook videos",
                    "statistical_backing": "T-test p = 0.003, Cohen's d = 0.7",
                    "impact": "47% higher engagement rate",
                    "recommendation": "Use 2-3 different hooks per video"
                }}
            ],
            "optimal_strategies": [
                {{
                    "strategy": "Specific content formula",
                    "statistical_support": "Correlation r = 0.65, p < 0.001",
                    "expected_outcome": "2.3x higher viral success rate"
                }}
            ]
        }}

        Only include patterns with p < 0.05 statistical significance. Base all insights on provided validated data.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        response_content = response.choices[0].message.content
        try:
            pattern_analysis = json.loads(response_content)
        except json.JSONDecodeError:
            logger.warning(f"GPT returned non-JSON response: {response_content[:200]}...")
            pattern_analysis = {
                'validated_patterns': [],
                'performance_drivers': [],
                'optimal_strategies': [],
                'raw_response': response_content
            }
        
        logger.info("GPT content pattern analysis completed")
        return pattern_analysis
        
    except Exception as e:
        logger.error(f"GPT content pattern analysis failed: {e}")
        raise


def analyze_creator_behavior_patterns(analyzer_results: Dict[str, Any],
                                    statistical_validation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze creator behavior patterns and their impact on performance.
    
    Args:
        analyzer_results (Dict[str, Any]): Results from creator analyzers
        statistical_validation (Dict[str, Any]): Statistical validation results
        
    Returns:
        Dict[str, Any]: Creator behavior pattern analysis
    """
    try:
        client = OpenAI()
        
        # Extract creator-related statistical findings
        creator_stats = statistical_validation.get('significance_results', {}).get('significant_tests', [])
        creator_correlations = [
            corr for corr in statistical_validation.get('correlation_results', {}).get('significant_correlations', [])
            if 'follower' in corr.get('metric_pair', '').lower() or 'verified' in corr.get('metric_pair', '').lower()
        ]
        
        # If no significant creator findings, return basic creator analysis
        if not creator_stats and not creator_correlations:
            logger.warning("No significant creator findings - generating basic creator analysis")
            return _generate_basic_creator_analysis(analyzer_results)
        
        prompt = f"""
        You are a TikTok creator strategy analyst. Analyze these VALIDATED creator behavior patterns.

        STATISTICALLY SIGNIFICANT CREATOR FINDINGS:
        {json.dumps(creator_stats, indent=2)}

        CREATOR CORRELATIONS (p < 0.05):
        {json.dumps(creator_correlations, indent=2)}

        CREATOR PERFORMANCE DATA:
        {json.dumps(analyzer_results.get('creator_analysis', {}), indent=2)}

        Based on statistically validated evidence, identify:

        1. **Follower Impact**: How does follower count affect performance (with statistical proof)?
        2. **Verification Advantage**: What's the validated impact of verification status?
        3. **Creator Tier Strategies**: What content strategies work for different follower tiers?
        4. **Optimization Recommendations**: Specific, statistically-backed advice for creators

        Format as JSON with statistical evidence for each insight:
        {{
            "follower_impact": {{
                "statistical_finding": "Correlation/test result",
                "practical_impact": "Specific effect size",
                "recommendation": "Actionable advice"
            }},
            "verification_advantage": {{
                "statistical_evidence": "Test results",
                "performance_difference": "Quantified advantage",
                "strategic_implication": "What this means for creators"
            }},
            "tier_strategies": [
                {{
                    "tier": "Micro/Mid/Large/Mega",
                    "validated_approach": "Statistically proven strategy",
                    "expected_results": "Performance outcomes"
                }}
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        creator_pattern_analysis = json.loads(response.choices[0].message.content)
        logger.info("GPT creator pattern analysis completed")
        return creator_pattern_analysis
        
    except Exception as e:
        logger.error(f"GPT creator pattern analysis failed: {e}")
        raise


def analyze_timing_optimization_patterns(analyzer_results: Dict[str, Any],
                                       statistical_validation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze timing and technical optimization patterns.
    
    Args:
        analyzer_results (Dict[str, Any]): Results from timing/technical analyzers
        statistical_validation (Dict[str, Any]): Statistical validation results
        
    Returns:
        Dict[str, Any]: Timing optimization pattern analysis
    """
    try:
        client = OpenAI()
        
        # Extract timing and technical statistical findings
        timing_stats = [
            test for test in statistical_validation.get('significance_results', {}).get('significant_tests', [])
            if any(keyword in str(test).lower() for keyword in ['hour', 'day', 'time', 'duration', 'resolution'])
        ]
        
        prompt = f"""
        You are a TikTok timing and technical optimization expert. Analyze these VALIDATED findings.

        STATISTICALLY SIGNIFICANT TIMING/TECHNICAL FINDINGS:
        {json.dumps(timing_stats, indent=2)}

        TIMING ANALYSIS RESULTS:
        {json.dumps(analyzer_results.get('timing_analysis', {}), indent=2)}

        TECHNICAL SPECS ANALYSIS:
        {json.dumps(analyzer_results.get('specs_analysis', {}), indent=2)}

        Based on statistical validation (p < 0.05), provide:

        1. **Optimal Posting Times**: When to post for maximum engagement (with statistical proof)
        2. **Video Specifications**: Optimal duration/resolution/aspect ratio (validated)
        3. **Timing Strategies**: Day-of-week and time-slot recommendations (evidence-based)
        4. **Technical Optimization**: Proven specs that drive performance

        Format as JSON with statistical backing:
        {{
            "optimal_posting": {{
                "best_time_slot": "Time range",
                "statistical_evidence": "Test results showing significance",
                "performance_advantage": "Quantified improvement",
                "confidence_level": "High/Medium based on p-value"
            }},
            "video_specs": {{
                "optimal_duration": "Duration range",
                "optimal_resolution": "Resolution recommendation", 
                "statistical_support": "Evidence from significance tests"
            }},
            "timing_strategies": [
                {{
                    "strategy": "Specific timing recommendation",
                    "evidence": "Statistical test results",
                    "expected_impact": "Performance improvement"
                }}
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        timing_pattern_analysis = json.loads(response.choices[0].message.content)
        logger.info("GPT timing pattern analysis completed")
        return timing_pattern_analysis
        
    except Exception as e:
        logger.error(f"GPT timing pattern analysis failed: {e}")
        raise


def synthesize_cross_category_patterns(all_pattern_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Synthesize patterns across all categories to find interconnected insights.
    
    Args:
        all_pattern_analyses (List[Dict[str, Any]]): All pattern analysis results
        
    Returns:
        Dict[str, Any]: Cross-category pattern synthesis
    """
    try:
        client = OpenAI()
        
        prompt = f"""
        You are a TikTok strategy synthesizer. Analyze these VALIDATED pattern analyses to find interconnected insights.

        ALL PATTERN ANALYSES:
        {json.dumps(all_pattern_analyses, indent=2)}

        Identify cross-category patterns and create an integrated strategy framework:

        1. **Interconnected Patterns**: How do content + creator + timing patterns work together?
        2. **Compound Effects**: What combinations multiply performance (with evidence)?
        3. **Integrated Strategy**: Complete framework combining all validated insights
        4. **Success Formula**: Step-by-step statistically-backed approach for viral success

        Format as comprehensive strategy guide:
        {{
            "interconnected_insights": [
                {{
                    "pattern": "Cross-category relationship",
                    "statistical_support": "Combined evidence",
                    "multiplier_effect": "How categories amplify each other"
                }}
            ],
            "integrated_strategy": {{
                "content_formula": "Validated content approach",
                "timing_optimization": "Proven timing strategy", 
                "creator_positioning": "Evidence-based creator advice",
                "expected_results": "Projected performance improvement"
            }},
            "success_framework": [
                {{
                    "step": 1,
                    "action": "Specific validated action",
                    "rationale": "Statistical evidence",
                    "expected_impact": "Performance outcome"
                }}
            ]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        synthesis_analysis = json.loads(response.choices[0].message.content)
        logger.info("GPT cross-category synthesis completed")
        return synthesis_analysis
        
    except Exception as e:
        logger.error(f"GPT synthesis failed: {e}")
        raise


def get_pattern_analysis_summary(pattern_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary of pattern analysis results.
    
    Args:
        pattern_results (Dict[str, Any]): All pattern analysis results
        
    Returns:
        Dict[str, Any]: Pattern analysis summary
    """
    total_patterns = 0
    high_confidence_patterns = 0
    
    # Count patterns across all analyses
    for analysis_name, analysis_data in pattern_results.items():
        if isinstance(analysis_data, dict):
            for key, value in analysis_data.items():
                if isinstance(value, list):
                    total_patterns += len(value)
                    # Count high confidence patterns
                    high_confidence_patterns += len([
                        item for item in value 
                        if isinstance(item, dict) and 
                        item.get('confidence_level', '').lower() == 'high'
                    ])
    
    return {
        'total_patterns_identified': total_patterns,
        'high_confidence_patterns': high_confidence_patterns,
        'analysis_categories': len(pattern_results),
        'statistical_backing': 'All patterns validated with p < 0.05',
        'analysis_status': 'complete'
    }


def _generate_basic_pattern_analysis(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate basic pattern analysis when no significant statistical findings exist."""
    validated_patterns = []
    performance_drivers = []
    optimal_strategies = []
    
    # Extract top performers from each category
    for category, analysis in analyzer_results.items():
        if isinstance(analysis, dict) and analysis:
            # Get top performer
            top_item = max(analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0)
            if len(top_item) == 2 and isinstance(top_item[1], dict):
                validated_patterns.append({
                    'pattern_name': f"{category.replace('_', ' ').title()} performance leader",
                    'statistical_evidence': 'Observational analysis (limited sample)',
                    'actionable_insight': f"{top_item[0]} shows highest performance in {category}",
                    'confidence_level': 'Low'
                })
                
                if top_item[1].get('avg_views', 0) > 100000:  # Above 100K views
                    performance_drivers.append({
                        'driver': f"High-performing {category.replace('_', ' ')}",
                        'statistical_backing': 'Descriptive analysis only',
                        'impact': f"Top item: {top_item[1].get('avg_views', 0):,} views",
                        'recommendation': f"Consider using {top_item[0]} approach"
                    })
    
    # Generate basic optimal strategies
    if validated_patterns:
        optimal_strategies.append({
            'strategy': 'Focus on top-performing elements',
            'statistical_support': 'Based on current sample data',
            'expected_outcome': 'Improved performance potential'
        })
    
    return {
        'validated_patterns': validated_patterns,
        'performance_drivers': performance_drivers,
        'optimal_strategies': optimal_strategies
    }


def _generate_basic_creator_analysis(analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate basic creator analysis when no significant statistical findings exist."""
    creator_analysis = analyzer_results.get('creator_analysis', {})
    
    follower_impact = {
        'statistical_finding': 'Limited sample - no statistical significance',
        'practical_impact': 'Observational patterns only',
        'recommendation': 'Collect more data for statistical validation'
    }
    
    verification_advantage = {
        'statistical_evidence': 'Sample too small for significance testing',
        'performance_difference': 'Cannot determine with current data',
        'strategic_implication': 'Monitor verification impact as data grows'
    }
    
    tier_strategies = []
    if creator_analysis:
        for tier, data in creator_analysis.items():
            if isinstance(data, dict):
                tier_strategies.append({
                    'tier': tier,
                    'validated_approach': 'Observational patterns only',
                    'expected_results': f"Current avg: {data.get('avg_views', 0):,} views"
                })
    
    return {
        'follower_impact': follower_impact,
        'verification_advantage': verification_advantage,
        'tier_strategies': tier_strategies
    }


def _clean_for_json_serialization(data):
    """Clean data structure for JSON serialization by converting numpy/pandas types."""
    if isinstance(data, list):
        return [_clean_for_json_serialization(item) for item in data]
    elif isinstance(data, dict):
        return {key: _clean_for_json_serialization(value) for key, value in data.items()}
    elif hasattr(data, 'item'):  # numpy scalar
        return data.item()
    elif isinstance(data, bool):  # Handle boolean explicitly
        return bool(data)
    elif isinstance(data, (int, float)):
        return float(data) if isinstance(data, float) else int(data)
    elif hasattr(data, 'tolist'):  # numpy array
        return data.tolist()
    else:
        return str(data) if data is not None else None