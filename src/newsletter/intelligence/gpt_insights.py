"""
GPT-powered contextual intelligence extraction and recommendations.
Single responsibility: Generate actionable insights and predictions from patterns.
"""
import json
import logging
from typing import Dict, Any, List
import os
import asyncio
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


async def generate_all_gpt_insights_concurrent(pattern_analysis: Dict[str, Any], 
                                             statistical_evidence: Dict[str, Any],
                                             analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate all GPT insights concurrently to speed up processing and reduce token usage.
    
    Args:
        pattern_analysis (Dict[str, Any]): Pattern analysis results
        statistical_evidence (Dict[str, Any]): Statistical validation data
        analyzer_results (Dict[str, Any]): Analyzer results
        
    Returns:
        Dict[str, Any]: All GPT insights generated concurrently
    """
    client = AsyncOpenAI()
    
    # Create all tasks for concurrent execution
    tasks = [
        _generate_creator_recommendations_async(client, pattern_analysis, statistical_evidence),
        _generate_content_gaps_async(client, analyzer_results, pattern_analysis),
        _generate_trend_predictions_async(client, pattern_analysis, analyzer_results),
        _generate_competitive_intelligence_async(client, analyzer_results, pattern_analysis)
    ]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    gpt_insights = {}
    task_names = ['creator_recommendations', 'content_gap_analysis', 'trend_predictions', 'competitive_intelligence']
    
    failed_tasks = []
    for i, (task_name, result) in enumerate(zip(task_names, results)):
        if isinstance(result, Exception):
            logger.error(f"GPT task {task_name} failed: {result}")
            failed_tasks.append(task_name)
        else:
            gpt_insights[task_name] = result

    # FAIL FAST - Don't generate newsletter with missing critical sections
    if failed_tasks:
        raise Exception(f"Critical GPT tasks failed: {failed_tasks}. Cannot generate newsletter with incomplete data.")
    
    # Generate final synthesis - CRITICAL, no fallback
    try:
        synthesis_task = _synthesize_actionable_intelligence_async(client, list(gpt_insights.values()))
        gpt_insights['actionable_intelligence'] = await synthesis_task
    except Exception as e:
        logger.error(f"GPT synthesis failed: {e}")
        raise Exception(f"Final synthesis failed: {e}. Newsletter cannot be completed.")
    
    logger.info(f"Concurrent GPT analysis complete: {len(gpt_insights)} insights generated")
    return gpt_insights


async def _generate_creator_recommendations_async(client: AsyncOpenAI,
                                                pattern_analysis: Dict[str, Any], 
                                                statistical_evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Generate creator recommendations asynchronously with reduced context."""
    try:
        # Create focused summary to reduce tokens
        summary = _create_focused_summary(pattern_analysis, statistical_evidence, "creator_recommendations")
        
        prompt = f"""You are a FUNK/PHONK CAR EDIT TikTok specialist. You understand the specific car edit culture:

FUNK/PHONK CAR EDIT STYLE:
- Fast cuts & beat sync: Clips jump on every kick/snare for aggressive stuttery feel
- Velocity edits: Slow-to-fast motion synced to bass drops
- Shake & motion blur: Cars vibrating with the music
- Zooms & spins: Quick push-ins/rotations for intensity
- Dark high contrast color grading: neon purple/orange tones
- Phonk overlays: VHS noise, film grain, retro timestamps, glowing text
- Raw, gritty, high-energy vibe - turning car showcase into a rave

ACTUAL SCRAPED VIDEO DATA:
{summary}

Based on this REAL performance data from funk/phonk car edits, create detailed, actionable recommendations:

Generate JSON with this structure:
{{
  "new_creators": [
    {{
      "recommendation": "Specific FUNK/PHONK technique with exact technical details (BPM timing, frame counts, effect intensity levels)",
      "statistical_backing": "Real performance metrics: 'X technique averages Y views vs Z views without' or 'Top performers use X method'",
      "expected_impact": "Specific improvement with numbers: 'X% increase in engagement' or 'Y more views on average'",
      "implementation": "Easy/Medium/Hard"
    }}
  ],
  "growing_creators": [
    {{
      "recommendation": "Advanced FUNK/PHONK technique with technical specifics (exact timing, layering methods, transition techniques)",
      "statistical_backing": "Performance comparison: 'Videos with X technique get Y% more engagement than baseline'",
      "expected_impact": "Measurable growth: 'Average Z% increase in views' or 'X times more likely to go viral'",
      "implementation": "Easy/Medium/Hard"
    }}
  ],
  "established_creators": [
    {{
      "recommendation": "Expert-level PHONK editing technique with precise technical parameters (frame-perfect timing, advanced layering)",
      "statistical_backing": "Data from top performers: 'Best creators use X method averaging Y views' or 'Z% of viral videos use this'",
      "expected_impact": "Concrete results: 'Maintains X million average views' or 'Y% improvement in retention'",
      "implementation": "Easy/Medium/Hard"
    }}
  ]
}}

Limit to 2 FUNK/PHONK car edit recommendations per category.

IMPORTANT TECHNICAL REQUIREMENTS:
- Include specific BPM ranges (most Phonk is 140-160 BPM)
- Mention exact timing (4-frame cuts, 8-beat transitions, etc.)
- Specify intensity levels (contrast +25, grain 15%, blur 3px, etc.)
- Reference real performance differences from the data
- NO generic advice like 'be consistent' or 'use trending sounds'
- Focus on underground car edit aesthetic and Phonk culture"""
        
        # Force structured output with retries
        for attempt in range(3):  # 3 retry attempts
            response = await client.chat.completions.create(
                model="gpt-4o",  # gpt-4o supports JSON mode
                messages=[
                    {"role": "system", "content": "You MUST return valid JSON only. No explanation text. Focus on CAR CONTENT ONLY."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for consistent structure
                max_tokens=1500,
                response_format={"type": "json_object"}  # Force JSON response
            )

            try:
                content = response.choices[0].message.content.strip()
                if not content:
                    logger.warning(f"Empty response attempt {attempt + 1}")
                    continue

                result = json.loads(content)
                # Validate structure has required keys
                if _validate_creator_recommendations_structure(result):
                    return result
                else:
                    logger.warning(f"Invalid structure attempt {attempt + 1}: {result}")
                    continue
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode failed attempt {attempt + 1}: {e}")
                logger.warning(f"Response content: {response.choices[0].message.content[:200]}...")
                continue

        # All retries failed - ABORT instead of fallback
        raise Exception("Failed to generate valid creator recommendations after 3 attempts")
        
    except Exception as e:
        logger.error(f"Async creator recommendations failed: {e}")
        # NO FALLBACK - Re-raise to fail entire process
        raise Exception(f"Creator recommendations failed: {e}")


async def _generate_content_gaps_async(client: AsyncOpenAI,
                                     analyzer_results: Dict[str, Any],
                                     pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate content gap analysis asynchronously."""
    try:
        # Create focused summary
        summary = _create_focused_summary(analyzer_results, pattern_analysis, "content_gaps")
        
        prompt = f"""You are a CAR CONTENT TikTok strategist. Identify CAR CONTENT opportunities from this automotive data:

{summary}

IMPORTANT: Every opportunity MUST be about CAR CONTENT (car brands, automotive content, car video opportunities, etc.).

Generate JSON with this structure:
{{
  "underexplored_combinations": [
    {{
      "combination": "Car brand + Hook + Music combo not being used enough",
      "viral_probability": "Success likelihood percentage",
      "competition_level": "Low/Medium/High"
    }}
  ],
  "blue_ocean_opportunities": [
    {{
      "unique_approach": "Novel content strategy nobody is doing",
      "market_validation": "Why this could work",
      "first_mover_advantage": "Benefits of being first"
    }}
  ]
}}

Limit to 3 combinations and 2 blue ocean opportunities."""
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You MUST return valid JSON only. No explanation text. Focus on CAR CONTENT ONLY."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1200,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        if not content:
            raise Exception("Empty response from GPT for content gaps")

        return json.loads(content)

    except Exception as e:
        logger.error(f"Async content gaps failed: {e}")
        # NO FALLBACK - Re-raise to fail entire process
        raise Exception(f"Content gap analysis failed: {e}")


async def _generate_trend_predictions_async(client: AsyncOpenAI,
                                          pattern_analysis: Dict[str, Any],
                                          analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate trend predictions asynchronously."""
    try:
        # Create focused summary
        summary = _create_focused_summary(pattern_analysis, analyzer_results, "trend_predictions")
        
        prompt = f"""You are a FUNK/PHONK CAR EDIT trend forecaster. You understand the underground car edit culture:

FUNK/PHONK CAR EDIT CULTURE:
- Fast cuts & beat sync: Clips jump on every kick/snare for aggressive stuttery feel
- Velocity edits: Slow-to-fast motion synced to bass drops
- Shake & motion blur: Cars vibrating with Phonk music
- Zooms & spins: Quick push-ins/rotations for intensity
- Dark high contrast color grading: neon purple/orange tones
- Phonk overlays: VHS noise, film grain, retro timestamps, glowing text
- Raw, gritty, high-energy vibe - turning car showcase into a rave

ACTUAL SCRAPED PERFORMANCE DATA:
{summary}

Predict FUNK/PHONK car edit trends based on this real data:

Generate JSON with this structure:
{{
  "content_trend_predictions": [
    {{
      "trend": "Specific FUNK/PHONK editing trend with technical details (BPM changes, new effect combinations, timing innovations)",
      "confidence": "High/Medium/Low",
      "timeline": "When it will peak (next 1-3 weeks)",
      "creator_action": "Exact technical steps car editors should take with specific parameters"
    }}
  ],
  "creator_strategy_trends": [
    {{
      "strategy": "Specific PHONK editing strategy with technical execution details",
      "evidence": "Performance data showing X% improvement or Y view increase",
      "success_probability": "Likelihood percentage with supporting metrics"
    }}
  ]
}}

Limit to 3 FUNK/PHONK car edit trends and 2 underground car edit strategies.

TECHNICAL REQUIREMENTS:
- Include specific BPM timing and frame-perfect cutting techniques
- Mention exact effect parameters and intensity levels
- Reference performance improvements from actual data
- Focus on Phonk music culture and underground car aesthetic
- Provide actionable technical steps, not vague suggestions"""
        
        # Force structured output with retries
        for attempt in range(3):  # 3 retry attempts
            response = await client.chat.completions.create(
                model="gpt-4o",  # gpt-4o supports JSON mode
                messages=[
                    {"role": "system", "content": "You MUST return valid JSON only. No explanation text. Focus on CAR TRENDS ONLY - automotive, vehicles, car brands, car content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Lower temperature for consistent structure
                max_tokens=1200,
                response_format={"type": "json_object"}  # Force JSON response
            )

            try:
                content = response.choices[0].message.content.strip()
                if not content:
                    logger.warning(f"Empty response attempt {attempt + 1}")
                    continue

                result = json.loads(content)
                # Validate structure has required keys and CAR content
                if _validate_trend_predictions_structure(result):
                    return result
                else:
                    logger.warning(f"Invalid trend predictions structure attempt {attempt + 1}: {result}")
                    continue
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode failed attempt {attempt + 1}: {e}")
                logger.warning(f"Response content: {response.choices[0].message.content[:200]}...")
                continue

        # All retries failed - ABORT instead of fallback
        raise Exception("Failed to generate valid trend predictions after 3 attempts")

    except Exception as e:
        logger.error(f"Async trend predictions failed: {e}")
        # DO NOT USE FALLBACK - Re-raise to fail the entire process
        raise Exception(f"Trend predictions generation failed: {e}")


async def _generate_competitive_intelligence_async(client: AsyncOpenAI,
                                                 analyzer_results: Dict[str, Any],
                                                 pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate competitive intelligence asynchronously."""
    try:
        # Create focused summary
        summary = _create_focused_summary(analyzer_results, pattern_analysis, "competitive_intel")
        
        prompt = f"""You are a CAR CONTENT TikTok competitive analyst. Analyze the CAR CONTENT competitive landscape from this automotive data:

{summary}

IMPORTANT: Every analysis MUST be about CAR CONTENT creators and automotive video competition.

Generate JSON with this structure:
{{
  "market_leaders": [
    {{
      "success_factors": "What makes top performers successful",
      "content_formula": "Their winning approach",
      "vulnerability": "Where they could be challenged"
    }}
  ],
  "competitive_opportunities": [
    {{
      "niche_opportunity": "Underserved market segment",
      "entry_strategy": "How to compete effectively",
      "differentiation_approach": "How to stand out"
    }}
  ]
}}

Limit to 2 market leaders and 2 opportunities."""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You MUST return valid JSON only. No explanation text. Focus on CAR CONTENT ONLY."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        if not content:
            raise Exception("Empty response from GPT for competitive intelligence")

        return json.loads(content)

    except Exception as e:
        logger.error(f"Async competitive intelligence failed: {e}")
        # NO FALLBACK - Re-raise to fail entire process
        raise Exception(f"Competitive intelligence failed: {e}")


async def _synthesize_actionable_intelligence_async(client: AsyncOpenAI,
                                                   all_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Synthesize all insights into actionable intelligence."""
    try:
        # Create concise summary of all insights
        insights_summary = _create_insights_summary(all_insights)
        
        prompt = f"""Synthesize these insights into final actionable intelligence:

{insights_summary}

Generate JSON with this structure:
{{
  "immediate_actions": [
    {{
      "action": "Specific step creators can take now",
      "impact": "Expected improvement",
      "effort": "Easy/Medium/Hard",
      "timeline": "How quickly to implement"
    }}
  ],
  "viral_success_formula": {{
    "content_elements": "Key content approach",
    "timing_strategy": "When to post",
    "engagement_tactics": "How to boost engagement",
    "success_probability": "Likelihood of viral success"
  }}
}}

Limit to 5 immediate actions."""
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You MUST return valid JSON only. No explanation text. Focus on CAR CONTENT ONLY."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()
        if not content:
            raise Exception("Empty response from GPT for synthesis")

        return json.loads(content)
        
    except Exception as e:
        logger.error(f"Async synthesis failed: {e}")
        # NO FALLBACK - Re-raise to fail entire process
        raise Exception(f"Actionable intelligence synthesis failed: {e}")


def generate_creator_recommendations(pattern_analysis: Dict[str, Any], 
                                   statistical_evidence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate specific, actionable recommendations for creators based on validated patterns.
    
    Args:
        pattern_analysis (Dict[str, Any]): Validated pattern analysis results
        statistical_evidence (Dict[str, Any]): Statistical validation data
        
    Returns:
        Dict[str, Any]: Specific creator recommendations with evidence
        
    Raises:
        Exception: If GPT API call fails
    """
    try:
        client = OpenAI()
        
        # Clean data for JSON serialization
        clean_pattern_analysis = _clean_for_json_serialization(pattern_analysis)
        clean_statistical_evidence = _clean_for_json_serialization(statistical_evidence)
        
        prompt = f"""
        You are a TikTok creator success coach. Generate SPECIFIC, ACTIONABLE recommendations based on VALIDATED data.

        VALIDATED PATTERN ANALYSIS:
        {json.dumps(clean_pattern_analysis, indent=2)}

        STATISTICAL EVIDENCE (all p < 0.05):
        {json.dumps(clean_statistical_evidence, indent=2)}

        Create specific recommendations for different creator scenarios:

        1. **New Creators (0-10K followers)**: What validated strategies should they focus on first?
        2. **Growing Creators (10K-100K)**: What statistically proven tactics help growth?
        3. **Established Creators (100K+)**: How to maintain/increase engagement with evidence-based methods?
        4. **Car Content Creators**: Specific car edit strategies with statistical backing

        For each recommendation, include:
        - Specific action to take
        - Statistical evidence supporting it
        - Expected impact/outcome
        - Implementation difficulty (Easy/Medium/Hard)

        Format as actionable guide:
        {{
            "new_creators": [
                {{
                    "recommendation": "Specific action to take",
                    "statistical_backing": "Evidence with p-value",
                    "expected_impact": "Quantified improvement",
                    "implementation": "Easy/Medium/Hard",
                    "example": "Concrete example"
                }}
            ],
            "growing_creators": [...],
            "established_creators": [...],
            "car_content_creators": [
                {{
                    "car_strategy": "Car-specific recommendation",
                    "performance_data": "Statistical evidence",
                    "viral_potential": "Success rate increase",
                    "content_formula": "Exact approach to use"
                }}
            ]
        }}

        Make recommendations SPECIFIC and ACTIONABLE with clear statistical support.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        response_content = response.choices[0].message.content
        try:
            creator_recommendations = json.loads(response_content)
        except json.JSONDecodeError:
            logger.warning(f"GPT returned non-JSON response: {response_content[:200]}...")
            creator_recommendations = {
                'new_creators': [],
                'growing_creators': [],
                'established_creators': [],
                'car_content_creators': [],
                'raw_response': response_content
            }
        
        logger.info("GPT creator recommendations generated")
        return creator_recommendations
        
    except Exception as e:
        logger.error(f"GPT creator recommendations failed: {e}")
        raise


def generate_content_gap_analysis(analyzer_results: Dict[str, Any],
                                pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identify content gaps and untapped opportunities based on analysis.
    
    Args:
        analyzer_results (Dict[str, Any]): Results from all analyzers
        pattern_analysis (Dict[str, Any]): Pattern analysis results
        
    Returns:
        Dict[str, Any]: Content gap analysis and opportunities
    """
    try:
        client = OpenAI()
        
        # Create summarized data to reduce token usage
        content_summary = _create_content_summary(analyzer_results)
        pattern_summary = _create_pattern_summary(pattern_analysis)
        
        prompt = f"""
        You are a TikTok content opportunity analyst. Identify UNTAPPED opportunities and content gaps.

        CURRENT CONTENT SUMMARY:
        {content_summary}

        VALIDATED PATTERNS SUMMARY:
        {pattern_summary}

        Identify gaps and opportunities:

        1. **Underexplored Combinations**: What high-potential car + hook + music combinations are creators missing?
        2. **Performance Gaps**: What content types are underperforming but have potential?
        3. **Market Opportunities**: What trending elements could be combined in new ways?
        4. **Blue Ocean Content**: What unique approaches haven't been tried yet?

        For each opportunity, provide:
        - Specific gap identified
        - Why it's an opportunity (evidence-based reasoning)
        - Estimated competition level (Low/Medium/High)
        - Potential impact (viral probability)
        - Implementation strategy

        Format as opportunity guide:
        {{
            "underexplored_combinations": [
                {{
                    "combination": "Car brand + Hook + Music combo",
                    "current_usage": "How often it appears",
                    "performance_potential": "Why it should work better",
                    "competition_level": "Low/Medium/High",
                    "viral_probability": "Success likelihood"
                }}
            ],
            "content_gaps": [
                {{
                    "gap_description": "What's missing in current content",
                    "opportunity_size": "Potential reach/engagement",
                    "implementation_strategy": "How to capitalize on it"
                }}
            ],
            "blue_ocean_opportunities": [
                {{
                    "unique_approach": "Novel content strategy",
                    "market_validation": "Evidence it could work",
                    "first_mover_advantage": "Benefits of being first"
                }}
            ]
        }}

        Focus on DATA-DRIVEN opportunities with statistical support where possible.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4  # Slightly higher for creativity
        )
        
        gap_analysis = json.loads(response.choices[0].message.content)
        logger.info("GPT content gap analysis completed")
        return gap_analysis
        
    except Exception as e:
        logger.error(f"GPT content gap analysis failed: {e}")
        raise


def generate_competitive_intelligence(analyzer_results: Dict[str, Any],
                                    pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate competitive intelligence and market positioning insights.
    
    Args:
        analyzer_results (Dict[str, Any]): Analyzer results including creator data
        pattern_analysis (Dict[str, Any]): Pattern analysis results
        
    Returns:
        Dict[str, Any]: Competitive intelligence insights
    """
    try:
        client = OpenAI()
        
        # Clean data for JSON serialization
        clean_creator_data = _clean_for_json_serialization(analyzer_results.get('creator_analysis', {}))
        clean_pattern_analysis = _clean_for_json_serialization(pattern_analysis)
        
        prompt = f"""
        You are a TikTok competitive intelligence analyst. Analyze the competitive landscape for car content creators.

        CREATOR PERFORMANCE DATA:
        {json.dumps(clean_creator_data, indent=2)}

        CONTENT PERFORMANCE PATTERNS:
        {json.dumps(clean_pattern_analysis, indent=2)}

        Provide competitive intelligence:

        1. **Market Leaders**: Who are the top performers and what makes them successful?
        2. **Rising Stars**: Which creators are gaining momentum and why?
        3. **Content Strategies**: What approaches are winning vs losing in the market?
        4. **Competitive Gaps**: Where can new creators find their niche?

        Format as intelligence briefing:
        {{
            "market_leaders": [
                {{
                    "creator_profile": "Top performer characteristics",
                    "success_factors": "What makes them successful (data-driven)",
                    "content_formula": "Their winning approach",
                    "vulnerability": "Where they could be challenged"
                }}
            ],
            "rising_stars": [
                {{
                    "growth_pattern": "How they're gaining traction", 
                    "differentiation": "What sets them apart",
                    "momentum_factors": "Why they're rising"
                }}
            ],
            "winning_strategies": [
                {{
                    "strategy": "Successful content approach",
                    "adoption_rate": "How common it is",
                    "performance_data": "Statistical results",
                    "saturation_level": "Market saturation assessment"
                }}
            ],
            "competitive_opportunities": [
                {{
                    "niche_opportunity": "Underserved market segment",
                    "entry_strategy": "How to compete effectively",
                    "differentiation_approach": "How to stand out"
                }}
            ]
        }}

        Base insights on PERFORMANCE DATA and validated patterns, not speculation.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        competitive_intelligence = json.loads(response.choices[0].message.content)
        logger.info("GPT competitive intelligence generated")
        return competitive_intelligence
        
    except Exception as e:
        logger.error(f"GPT competitive intelligence failed: {e}")
        raise


def generate_trend_predictions(pattern_analysis: Dict[str, Any],
                             analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate predictions for next week's trends based on current patterns.
    
    Args:
        pattern_analysis (Dict[str, Any]): Current pattern analysis
        analyzer_results (Dict[str, Any]): Current week's analyzer results
        
    Returns:
        Dict[str, Any]: Next week trend predictions with confidence levels
    """
    try:
        client = OpenAI()
        
        # Clean data for JSON serialization
        clean_pattern_analysis = _clean_for_json_serialization(pattern_analysis)
        clean_analyzer_results = _clean_for_json_serialization(analyzer_results)
        
        prompt = f"""
        You are a TikTok trend forecasting expert. Predict NEXT WEEK'S trends based on current validated patterns.

        CURRENT VALIDATED PATTERNS:
        {json.dumps(clean_pattern_analysis, indent=2)}

        CURRENT WEEK PERFORMANCE DATA:
        {json.dumps(clean_analyzer_results, indent=2)}

        Predict trends for NEXT WEEK (7 days from now):

        1. **Content Trends**: What car content styles will trend up/down?
        2. **Creator Trends**: What creator strategies will gain momentum?
        3. **Technical Trends**: What video specs/timing will become more important?
        4. **Engagement Trends**: How will audience behavior patterns shift?

        For each prediction:
        - Specific trend prediction
        - Evidence supporting the prediction
        - Confidence level (High/Medium/Low)
        - Timeline (when it will peak)
        - Impact assessment (how big the trend will be)

        Format as trend forecast:
        {{
            "content_trend_predictions": [
                {{
                    "trend": "Specific content trend prediction",
                    "evidence": "Current data supporting this prediction",
                    "confidence": "High/Medium/Low",
                    "timeline": "When it will peak",
                    "impact_assessment": "How significant the trend will be",
                    "creator_action": "What creators should do"
                }}
            ],
            "creator_strategy_trends": [...],
            "technical_optimization_trends": [...],
            "overall_market_direction": {{
                "primary_trend": "Main market direction",
                "supporting_evidence": "Data backing this forecast",
                "strategic_implications": "What this means for creators"
            }}
        }}

        Base predictions on STATISTICAL PATTERNS and current momentum, not speculation.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        
        trend_predictions = json.loads(response.choices[0].message.content)
        logger.info("GPT trend predictions generated")
        return trend_predictions
        
    except Exception as e:
        logger.error(f"GPT trend predictions failed: {e}")
        raise


def synthesize_actionable_intelligence(all_gpt_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Synthesize all GPT insights into final actionable intelligence package.
    
    Args:
        all_gpt_insights (List[Dict[str, Any]]): All GPT-generated insights
        
    Returns:
        Dict[str, Any]: Final actionable intelligence synthesis
    """
    try:
        client = OpenAI()
        
        # Clean data for JSON serialization
        clean_gpt_insights = _clean_for_json_serialization(all_gpt_insights)
        
        prompt = f"""
        You are a TikTok strategy executive. Synthesize these insights into FINAL ACTIONABLE INTELLIGENCE for creators.

        ALL GPT INSIGHTS:
        {json.dumps(clean_gpt_insights, indent=2)}

        Create the ultimate strategy guide:

        1. **Top 5 Immediate Actions**: Most impactful things creators can do RIGHT NOW
        2. **Success Formula**: Step-by-step validated approach for viral content
        3. **Optimization Checklist**: Pre-posting checklist for maximum performance
        4. **Next Week Strategy**: Specific approach for the coming week

        Format as executive strategy brief:
        {{
            "immediate_actions": [
                {{
                    "action": "Specific immediate step",
                    "impact": "Expected performance improvement",
                    "effort": "Implementation difficulty",
                    "timeline": "How quickly to implement"
                }}
            ],
            "viral_success_formula": {{
                "content_elements": "Validated content approach",
                "timing_strategy": "Optimal posting approach",
                "engagement_tactics": "Proven engagement methods",
                "success_probability": "Likelihood of viral success"
            }},
            "optimization_checklist": [
                "Pre-posting validation step"
            ],
            "next_week_strategy": {{
                "focus_areas": "Primary strategic focus",
                "content_priorities": "What content to create",
                "timing_plan": "When to post",
                "success_metrics": "What to measure"
            }}
        }}

        Make everything SPECIFIC, ACTIONABLE, and EVIDENCE-BASED.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        actionable_intelligence = json.loads(response.choices[0].message.content)
        logger.info("GPT actionable intelligence synthesis completed")
        return actionable_intelligence
        
    except Exception as e:
        logger.error(f"GPT intelligence synthesis failed: {e}")
        raise


def get_gpt_insights_summary(insights_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate summary of GPT insights generation results.
    
    Args:
        insights_results (Dict[str, Any]): All GPT insights results
        
    Returns:
        Dict[str, Any]: GPT insights summary
    """
    total_recommendations = 0
    total_opportunities = 0
    total_predictions = 0
    
    # Count recommendations across all insights
    for insight_type, insight_data in insights_results.items():
        if isinstance(insight_data, dict):
            for key, value in insight_data.items():
                if isinstance(value, list):
                    if 'recommendation' in key.lower():
                        total_recommendations += len(value)
                    elif 'opportunit' in key.lower():
                        total_opportunities += len(value)
                    elif 'prediction' in key.lower():
                        total_predictions += len(value)
    
    return {
        'total_recommendations': total_recommendations,
        'total_opportunities': total_opportunities,
        'total_predictions': total_predictions,
        'insight_categories': len(insights_results),
        'ai_model': 'GPT-4',
        'insights_status': 'complete'
    }


def generate_all_gpt_insights_sync(pattern_analysis: Dict[str, Any], 
                                  statistical_evidence: Dict[str, Any],
                                  analyzer_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for concurrent GPT insights generation.
    
    Args:
        pattern_analysis (Dict[str, Any]): Pattern analysis results
        statistical_evidence (Dict[str, Any]): Statistical validation data
        analyzer_results (Dict[str, Any]): Analyzer results
        
    Returns:
        Dict[str, Any]: All GPT insights generated concurrently
    """
    try:
        return asyncio.run(generate_all_gpt_insights_concurrent(
            pattern_analysis, statistical_evidence, analyzer_results
        ))
    except Exception as e:
        logger.error(f"Concurrent GPT insights failed: {e}")
        # NO FALLBACK - Re-raise to fail the entire newsletter generation
        raise Exception(f"GPT insights generation failed: {e}. Newsletter cannot be generated with incomplete data.")


def _create_focused_summary(data1: Dict[str, Any], data2: Dict[str, Any], focus_area: str) -> str:
    """Create focused summary for specific GPT task to reduce token usage."""
    
    if focus_area == "creator_recommendations":
        # Get REAL performance data for Funk/Phonk car edits
        performance_data = []

        # Top car brands with detailed performance
        if 'brand_analysis' in data1 and isinstance(data1['brand_analysis'], dict):
            brands = sorted(data1['brand_analysis'].items(),
                          key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0,
                          reverse=True)[:3]
            for brand, data in brands:
                if isinstance(data, dict):
                    performance_data.append(f"🏆 TOP CAR BRAND: {brand}")
                    performance_data.append(f"   - {data.get('avg_views', 0):,} avg views across {data.get('video_count', 0)} videos")
                    performance_data.append(f"   - {data.get('avg_engagement', 0)*100:.1f}% engagement rate")

        # Top hooks with context
        if 'hook_analysis' in data1 and isinstance(data1['hook_analysis'], dict):
            hooks = sorted(data1['hook_analysis'].items(),
                         key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0,
                         reverse=True)[:3]
            for hook, data in hooks:
                if isinstance(data, dict):
                    performance_data.append(f"🎬 TOP HOOK: {hook}")
                    performance_data.append(f"   - {data.get('avg_views', 0):,} avg views, {data.get('video_count', 0)} videos")

        # Top hashtags
        if 'hashtag_analysis' in data1 and isinstance(data1['hashtag_analysis'], dict):
            hashtags = sorted(data1['hashtag_analysis'].items(),
                            key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0,
                            reverse=True)[:3]
            for hashtag, data in hashtags:
                if isinstance(data, dict):
                    performance_data.append(f"📱 TOP HASHTAG: #{hashtag}")
                    performance_data.append(f"   - {data.get('avg_views', 0):,} avg views, used {data.get('usage_count', 0)} times")

        return f"""REAL FUNK/PHONK CAR EDIT PERFORMANCE DATA:

{chr(10).join(performance_data)}

📊 STATISTICAL INSIGHTS:
- {len(data2.get('significant_differences', []))} significant performance differences found
- Use this ACTUAL data to create recommendations for the Funk/Phonk car edit community
- Focus on what's PROVEN to work in this specific underground aesthetic"""
    
    elif focus_area == "content_gaps":
        # Focus on underused combinations
        elements_summary = []
        for category, analysis in data1.items():
            if isinstance(analysis, dict) and len(analysis) > 1:
                elements_summary.append(f"- {category}: {len(analysis)} elements analyzed")
        
        return f"""Current Content Landscape:
{chr(10).join(elements_summary[:4])}

Pattern Insights: Focus on combinations not being fully exploited
Opportunity Area: Cross-category content mixing"""
    
    elif focus_area == "trend_predictions":
        # Focus on momentum indicators  
        trends_summary = []
        for category, analysis in data1.items():
            if isinstance(analysis, dict) and analysis:
                avg_performance = sum(item.get('avg_views', 0) for item in analysis.values() if isinstance(item, dict)) / len(analysis)
                trends_summary.append(f"- {category}: {len(analysis)} items, {avg_performance:,.0f} avg views")
        
        return f"""Current Performance Trends:
{chr(10).join(trends_summary[:4])}

Momentum Indicators: Based on current sample data
Prediction Scope: Next 7 days based on observed patterns"""
    
    elif focus_area == "competitive_intel":
        # Focus on competitive landscape
        competitive_summary = []
        for category, analysis in data1.items():
            if isinstance(analysis, dict) and analysis:
                sorted_items = sorted(analysis.items(), key=lambda x: x[1].get('avg_views', 0) if isinstance(x[1], dict) else 0, reverse=True)
                top_3 = [item[0] for item in sorted_items[:3]]
                competitive_summary.append(f"- {category} leaders: {', '.join(top_3)}")
        
        return f"""Competitive Landscape:
{chr(10).join(competitive_summary[:4])}

Market Analysis: Based on performance data
Focus: Content strategy differentiation opportunities"""
    
    else:
        return "Limited data available for analysis"


def _create_insights_summary(all_insights: List[Dict[str, Any]]) -> str:
    """Create concise summary of all insights for synthesis."""
    summary_parts = []
    
    for insight in all_insights:
        if isinstance(insight, dict):
            for category, data in insight.items():
                if isinstance(data, list) and data:
                    summary_parts.append(f"- {category}: {len(data)} insights generated")
                elif isinstance(data, dict) and data:
                    summary_parts.append(f"- {category}: Strategic framework provided")
    
    return f"""Generated Insights Summary:
{chr(10).join(summary_parts[:8])}

Focus: Synthesize into actionable intelligence
Target: Immediate creator actions with high impact potential"""


def _validate_creator_recommendations_structure(result: Dict[str, Any]) -> bool:
    """Validate creator recommendations has required structure and CAR content."""
    required_keys = ['new_creators', 'growing_creators', 'established_creators']

    if not all(key in result for key in required_keys):
        return False

    # Check each category has recommendations
    for key in required_keys:
        if not isinstance(result[key], list) or len(result[key]) == 0:
            return False

        # Validate each recommendation has required fields
        for rec in result[key]:
            if not isinstance(rec, dict):
                return False
            if not all(field in rec for field in ['recommendation', 'statistical_backing', 'expected_impact', 'implementation']):
                return False

            # Check content is related to FUNK/PHONK car editing culture
            content_text = str(rec.get('recommendation', '')).lower()
            car_words = ['car', 'vehicle', 'automotive', 'engine', 'ferrari', 'lamborghini', 'tesla', 'bmw', 'mercedes']
            phonk_edit_words = ['beat sync', 'velocity edit', 'motion blur', 'color grading', 'phonk', 'funk', 'bass drop',
                               'fast cuts', 'shake', 'zoom', 'spin', 'vhs noise', 'film grain', 'retro', 'neon', 'contrast']
            content_words = ['video', 'content', 'creator', 'tiktok', 'edit', 'transition', 'hook', 'viral', 'engagement']

            has_car_content = any(word in content_text for word in car_words)
            has_phonk_editing = any(word in content_text for word in phonk_edit_words)
            has_content_creation = any(word in content_text for word in content_words)

            if not (has_car_content or has_phonk_editing or has_content_creation):
                logger.warning(f"Non-relevant content detected: {rec.get('recommendation', '')}")
                return False

    return True


def _validate_trend_predictions_structure(result: Dict[str, Any]) -> bool:
    """Validate trend predictions has required structure and CAR content."""
    if 'content_trend_predictions' not in result:
        return False

    predictions = result['content_trend_predictions']
    if not isinstance(predictions, list) or len(predictions) == 0:
        return False

    for pred in predictions:
        if not isinstance(pred, dict):
            return False
        if not all(field in pred for field in ['trend', 'confidence', 'timeline', 'creator_action']):
            return False

        # Check content is related to FUNK/PHONK car editing culture
        trend_text = str(pred.get('trend', '')).lower()
        car_words = ['car', 'vehicle', 'automotive', 'engine', 'ferrari', 'lamborghini', 'tesla', 'bmw', 'mercedes', 'supercar']
        phonk_edit_words = ['beat sync', 'velocity edit', 'motion blur', 'color grading', 'phonk', 'funk', 'bass drop',
                           'fast cuts', 'shake', 'zoom', 'spin', 'vhs noise', 'film grain', 'retro', 'neon', 'contrast']
        content_words = ['video', 'content', 'creator', 'tiktok', 'viral', 'trend', 'edit', 'music', 'hook', 'transition']

        has_car_content = any(word in trend_text for word in car_words)
        has_phonk_editing = any(word in trend_text for word in phonk_edit_words)
        has_content_creation = any(word in trend_text for word in content_words)

        if not (has_car_content or has_phonk_editing or has_content_creation):
            logger.warning(f"Non-relevant trend detected: {pred.get('trend', '')}")
            return False

    return True


# REMOVED: _get_fallback_data function
# No more garbage placeholder data - system will fail fast instead


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