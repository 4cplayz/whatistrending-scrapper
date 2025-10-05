"""
Extract past 7 days video data from Supabase.
Single responsibility: Clean data extraction with error handling.
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import logging

from src.database.client.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def extract_past_7_days_videos() -> pd.DataFrame:
    """
    Extract past 7 days of ANALYZED video data from Supabase.
    Only includes videos that passed pre-filtering and completed Twelve Labs analysis.
    
    Returns:
        pd.DataFrame: Pre-filtered and analyzed video data from database
        
    Raises:
        Exception: If database query fails
    """
    try:
        supabase = get_supabase_client()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        logger.info(f"Extracting videos SCRAPED from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Filter by scraped_at (when WE got the video) not created_at (when video was made on TikTok)
        # Only get videos that completed Twelve Labs analysis (analysis_status = 'completed') 
        response = supabase.table('videos').select('*').gte(
            'scraped_at', start_date.isoformat()
        ).lte(
            'scraped_at', end_date.isoformat()
        ).eq(
            'analysis_status', 'completed'
        ).execute()
        
        if not response.data:
            logger.warning("No analyzed video data found for past 7 days")
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        logger.info(f"✅ Successfully extracted {len(df)} pre-filtered and analyzed videos with {len(df.columns)} fields")
        logger.info(f"   - These videos already passed pre-filtering and Twelve Labs analysis")
        logger.info(f"   - No additional filtering waste - using all analyzed videos for newsletter")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to extract 7-day video data: {e}")
        raise


def validate_extracted_data(df: pd.DataFrame) -> bool:
    """
    Validate that extracted data has required fields for analysis.
    
    Args:
        df (pd.DataFrame): Extracted video data
        
    Returns:
        bool: True if data is valid for analysis
    """
    if df.empty:
        logger.error("DataFrame is empty")
        return False
    
    required_fields = [
        'video_id', 'views', 'likes', 'comments', 'shares', 
        'author_username', 'created_at', 'analysis_results'
    ]
    
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        logger.error(f"Missing required fields: {missing_fields}")
        return False
    
    logger.info(f"Data validation passed: {len(df)} videos ready for analysis")
    return True


def get_data_quality_summary(df: pd.DataFrame) -> dict:
    """
    Generate data quality summary for monitoring.
    
    Args:
        df (pd.DataFrame): Extracted video data
        
    Returns:
        dict: Data quality metrics
    """
    if df.empty:
        return {'status': 'empty', 'video_count': 0}
    
    return {
        'status': 'success',
        'video_count': len(df),
        'field_count': len(df.columns),
        'date_range': {
            'start': df['created_at'].min() if 'created_at' in df.columns else None,
            'end': df['created_at'].max() if 'created_at' in df.columns else None
        },
        'has_analysis_results': 'analysis_results' in df.columns and df['analysis_results'].notna().sum(),
        'engagement_data_complete': all(
            field in df.columns and df[field].notna().sum() > 0 
            for field in ['views', 'likes', 'comments', 'shares']
        )
    }