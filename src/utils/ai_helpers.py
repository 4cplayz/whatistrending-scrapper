"""
AI assistance utilities for enhanced predictions and content generation.
Single responsibility: GPT integration for trend analysis and predictions.
"""
import logging
from typing import Dict, Any, List
import json
from src.config.settings import get_config

logger = logging.getLogger(__name__)


def enhance_predictions_with_gpt(analysis_data: Dict[str, Any],
                                video_sample: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Use GPT to enhance trend predictions with AI insights.

    Args:
        analysis_data (Dict[str, Any]): Statistical analysis results
        video_sample (List[Dict[str, Any]]): Sample of top performing videos

    Returns:
        Dict[str, Any]: Enhanced predictions with AI insights
    """
    try:
        # Prepare data summary for GPT
        data_summary = _prepare_data_summary(analysis_data, video_sample)

        # Create GPT prompt
        prompt = _create_prediction_prompt(data_summary)

        # Get GPT response using new API
        from openai import OpenAI
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a TikTok trend analysis expert specializing in car edit videos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )

        # Parse response
        ai_insights = _parse_gpt_response(response.choices[0].message.content)

        logger.info("Successfully enhanced predictions with GPT insights")
        return ai_insights

    except Exception as e:
        logger.error(f"GPT enhancement failed: {e}")
        return {"error": "AI enhancement unavailable", "fallback": True}


def generate_trend_explanations(trend_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate human-readable explanations for trending patterns.

    Args:
        trend_data (Dict[str, Any]): Raw trend analysis data

    Returns:
        Dict[str, Any]: Explained trend patterns
    """
    try:
        prompt = f"""
        Analyze these TikTok car edit trends and explain why they're working:

        Trending Elements: {json.dumps(trend_data, indent=2)}

        Provide:
        1. Why these trends are successful (psychology/algorithm factors)
        2. Predicted lifespan of each trend
        3. Best practices for creators
        4. Warning signs of trend saturation

        Be specific and actionable.
        """

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.6
        )

        return {
            "explanations": response.choices[0].message.content,
            "ai_generated": True,
            "confidence": "high"
        }

    except Exception as e:
        logger.error(f"Trend explanation generation failed: {e}")
        return {"explanations": "AI analysis unavailable", "ai_generated": False}


def predict_next_viral_combo(high_performers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predict next viral combination using AI pattern recognition.

    Args:
        high_performers (List[Dict[str, Any]]): Top performing video data

    Returns:
        Dict[str, Any]: Predicted viral combinations
    """
    try:
        # Format data for GPT
        performance_summary = []
        for video in high_performers[:10]:  # Top 10 videos
            performance_summary.append({
                "views": video.get("views", 0),
                "engagement_rate": video.get("engagement_rate", 0),
                "car_brand": video.get("car_brand", "unknown"),
                "hook_type": video.get("hook_type", "unknown"),
                "duration": video.get("duration", 0),
                "viral_score": video.get("viral_score", 0)
            })

        prompt = f"""
        Based on these top-performing TikTok car edit videos, predict the next viral combination:

        Performance Data: {json.dumps(performance_summary, indent=2)}

        Identify:
        1. Underexplored car brand + hook combinations
        2. Optimal video length patterns emerging
        3. Content gaps in current market
        4. Next breakthrough format likely to emerge

        Focus on actionable predictions for creators.
        """

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.8
        )

        return {
            "predictions": _parse_viral_predictions(response.choices[0].message.content),
            "ai_confidence": "medium-high",
            "prediction_horizon": "7-14 days"
        }

    except Exception as e:
        logger.error(f"Viral combo prediction failed: {e}")
        return {"predictions": [], "error": "AI prediction unavailable"}


def _prepare_data_summary(analysis_data: Dict[str, Any],
                         video_sample: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Prepare concise data summary for GPT analysis."""
    import pandas as pd

    # Clean video sample to remove non-serializable objects
    clean_sample = []
    for video in video_sample[:5]:
        clean_video = {}
        for k, v in video.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                clean_video[k] = v
            elif hasattr(v, 'isoformat'):  # datetime objects
                clean_video[k] = v.isoformat()
            elif pd.isna(v):
                clean_video[k] = None
            else:
                clean_video[k] = str(v)
        clean_sample.append(clean_video)

    return {
        "top_performing_elements": _extract_top_elements(analysis_data),
        "engagement_patterns": _extract_engagement_patterns(analysis_data),
        "sample_videos": clean_sample,
        "statistical_significance": _extract_significant_findings(analysis_data)
    }


def _create_prediction_prompt(data_summary: Dict[str, Any]) -> str:
    """Create structured prompt for GPT prediction enhancement."""
    return f"""
    Analyze this TikTok car edit performance data and provide enhanced predictions:

    Data Summary: {json.dumps(data_summary, indent=2)}

    Provide:
    1. 3 specific predictions for next week's trends
    2. Content creator recommendations
    3. Timing optimization insights
    4. Risk factors to avoid

    Be data-driven and specific. Focus on actionable insights.
    """


def _parse_gpt_response(response_text: str) -> Dict[str, Any]:
    """Parse GPT response into structured format."""
    return {
        "ai_predictions": response_text,
        "enhanced_insights": True,
        "generated_at": "current_timestamp",
        "model_used": "gpt-4"
    }


def _parse_viral_predictions(response_text: str) -> List[Dict[str, Any]]:
    """Parse viral combination predictions from GPT response."""
    # Simple parsing - could be enhanced with more sophisticated extraction
    predictions = []
    lines = response_text.split('\n')

    for line in lines:
        if any(keyword in line.lower() for keyword in ['predict', 'combination', 'likely', 'next']):
            predictions.append({
                "prediction": line.strip(),
                "confidence": "medium"
            })

    return predictions[:5]  # Return top 5 predictions


def _extract_top_elements(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract top performing elements from analysis data."""
    top_elements = {}

    for category, data in analysis_data.items():
        if isinstance(data, dict) and 'top_performers' in data:
            top_elements[category] = data['top_performers'][:3]  # Top 3

    return top_elements


def _extract_engagement_patterns(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract engagement patterns from analysis data."""
    patterns = {}

    for category, data in analysis_data.items():
        if isinstance(data, dict) and 'avg_engagement' in data:
            patterns[category] = {
                "avg_engagement": data['avg_engagement'],
                "pattern_strength": "high" if data['avg_engagement'] > 0.12 else "medium"
            }

    return patterns


def _extract_significant_findings(analysis_data: Dict[str, Any]) -> List[str]:
    """Extract statistically significant findings."""
    findings = []

    # Look for significance markers in the data
    for category, data in analysis_data.items():
        if isinstance(data, dict):
            if data.get('is_significant', False):
                findings.append(f"{category}: statistically significant")
            elif data.get('p_value', 1) < 0.05:
                findings.append(f"{category}: p < 0.05")

    return findings[:5]  # Top 5 findings