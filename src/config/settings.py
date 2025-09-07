"""
Configuration settings for TikTok Car Edit Newsletter service.

Single responsibility: Centralize scaling limits from environment variables.
"""

import os


class NewsletterConfig:
    """Newsletter generation limits configuration."""
    
    # Newsletter generation limits
    TOP_RANKINGS_LIMIT = int(os.getenv('TOP_RANKINGS_LIMIT', 5))
    RECOMMENDATIONS_LIMIT = int(os.getenv('RECOMMENDATIONS_LIMIT', 3))
    STATISTICAL_FINDINGS_LIMIT = int(os.getenv('STATISTICAL_FINDINGS_LIMIT', 5))
    
    # Database query limits
    VIDEO_ANALYSIS_DEFAULT_LIMIT = int(os.getenv('VIDEO_ANALYSIS_DEFAULT_LIMIT', 50))
    NEWSLETTER_RETRIEVAL_LIMIT = int(os.getenv('NEWSLETTER_RETRIEVAL_LIMIT', 1))
    
    # Analysis processing limits
    HASHTAG_COMBINATIONS_LIMIT = int(os.getenv('HASHTAG_COMBINATIONS_LIMIT', 10))
    CREATOR_ANALYSIS_LIMIT = int(os.getenv('CREATOR_ANALYSIS_LIMIT', 5))
    CHAMPION_SELECTION_LIMIT = int(os.getenv('CHAMPION_SELECTION_LIMIT', 2))
    
    # Cost-optimized filtering settings (reduce waste from aggressive filtering)
    MIN_VIEWS_THRESHOLD = int(os.getenv('MIN_VIEWS_THRESHOLD', 100))  # Much lower threshold
    MIN_ENGAGEMENT_RATE = float(os.getenv('MIN_ENGAGEMENT_RATE', 0.005))  # 0.5% instead of 2%
    TOP_PERFORMERS_LIMIT = int(os.getenv('TOP_PERFORMERS_LIMIT', 35))  # Keep more videos


def get_config():
    """Get newsletter configuration instance."""
    return NewsletterConfig()