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


def get_config():
    """Get newsletter configuration instance."""
    return NewsletterConfig()