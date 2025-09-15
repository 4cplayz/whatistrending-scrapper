"""
Process Twelve Labs analysis results into structured features.
Single responsibility: Extract and normalize AI analysis data.
"""
import pandas as pd
from typing import List, Any
import logging

logger = logging.getLogger(__name__)


def extract_car_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract car analysis features from Twelve Labs results.
    
    Args:
        df (pd.DataFrame): Video data with analysis_results column
        
    Returns:
        pd.DataFrame: Data with car feature columns added
    """
    df = df.copy()
    
    # Extract ALL car brands (not just first)
    df['car_brands_list'] = df['analysis_results'].apply(
        lambda x: x.get('car_analysis', {}).get('car_brands', []) 
        if isinstance(x, dict) else []
    )
    
    # Primary car brand and multi-brand tracking
    df['car_brand'] = df['car_brands_list'].apply(
        lambda x: x[0] if x else None
    )
    df['car_brand_count'] = df['car_brands_list'].apply(len)
    df['multi_brand_video'] = df['car_brand_count'] > 1
    
    # Extract car types
    df['car_types_list'] = df['analysis_results'].apply(
        lambda x: x.get('car_analysis', {}).get('car_types', []) 
        if isinstance(x, dict) else []
    )
    df['car_type'] = df['car_types_list'].apply(
        lambda x: x[0] if x else None
    )
    
    # Extract car topics (different from brands)
    df['car_topics_list'] = df['analysis_results'].apply(
        lambda x: x.get('car_analysis', {}).get('car_topics', []) 
        if isinstance(x, dict) else []
    )
    
    logger.info(f"Extracted car features: {df['car_brand'].nunique()} unique brands, {df['multi_brand_video'].sum()} multi-brand videos")
    return df


def extract_hook_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract hook analysis features from Twelve Labs results.
    
    Args:
        df (pd.DataFrame): Video data with analysis_results column
        
    Returns:
        pd.DataFrame: Data with hook feature columns added
    """
    df = df.copy()
    
    # Extract ALL hooks (not just first)
    df['hooks_list'] = df['analysis_results'].apply(
        lambda x: x.get('hook_analysis', {}).get('hooks', []) 
        if isinstance(x, dict) else []
    )
    
    # Primary hook and multi-hook tracking
    df['hook_type'] = df['hooks_list'].apply(
        lambda x: x[0] if x else None
    )
    df['hook_count'] = df['hooks_list'].apply(len)
    df['multi_hook_video'] = df['hook_count'] > 1
    
    # Extract engagement elements
    df['engagement_elements'] = df['analysis_results'].apply(
        lambda x: x.get('hook_analysis', {}).get('engagement_elements', []) 
        if isinstance(x, dict) else []
    )
    
    # Extract AI-generated titles and summaries
    df['ai_generated_title'] = df['analysis_results'].apply(
        lambda x: x.get('hook_analysis', {}).get('title') 
        if isinstance(x, dict) else None
    )
    
    df['hook_summary'] = df['analysis_results'].apply(
        lambda x: x.get('hook_analysis', {}).get('summary') 
        if isinstance(x, dict) else None
    )
    
    logger.info(f"Extracted hook features: {df['hook_type'].nunique()} unique hooks, {df['multi_hook_video'].sum()} multi-hook videos")
    return df


def extract_transition_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract transition and effects features from Twelve Labs results.
    
    Args:
        df (pd.DataFrame): Video data with analysis_results column
        
    Returns:
        pd.DataFrame: Data with transition feature columns added
    """
    df = df.copy()
    
    # Extract ALL transitions
    df['transitions_list'] = df['analysis_results'].apply(
        lambda x: x.get('transition_analysis', {}).get('transitions', []) 
        if isinstance(x, dict) else []
    )
    df['transition_type'] = df['transitions_list'].apply(
        lambda x: x[0] if x else None
    )
    df['transition_count'] = df['transitions_list'].apply(len)
    
    # Extract ALL effects
    df['effects_list'] = df['analysis_results'].apply(
        lambda x: x.get('transition_analysis', {}).get('effects', []) 
        if isinstance(x, dict) else []
    )
    df['effects_count'] = df['effects_list'].apply(len)
    
    # Extract edit style
    df['edit_style'] = df['analysis_results'].apply(
        lambda x: x.get('transition_analysis', {}).get('style') 
        if isinstance(x, dict) else None
    )
    
    logger.info(f"Extracted transition features: {df['transition_type'].nunique()} transitions, {df['edit_style'].nunique()} edit styles")
    return df


def extract_general_insights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract general insights from Twelve Labs analysis.
    
    Args:
        df (pd.DataFrame): Video data with analysis_results column
        
    Returns:
        pd.DataFrame: Data with general insight columns added
    """
    df = df.copy()
    
    # Extract video topics
    df['video_topics'] = df['analysis_results'].apply(
        lambda x: x.get('general_insights', {}).get('topics', []) 
        if isinstance(x, dict) else []
    )
    
    # Extract AI summary and suggested title
    df['ai_summary'] = df['analysis_results'].apply(
        lambda x: x.get('general_insights', {}).get('summary') 
        if isinstance(x, dict) else None
    )
    
    df['ai_suggested_title'] = df['analysis_results'].apply(
        lambda x: x.get('general_insights', {}).get('suggested_title') 
        if isinstance(x, dict) else None
    )
    
    logger.info("Extracted general insights features")
    return df


def process_all_analysis_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process all Twelve Labs analysis features in one pipeline.
    
    Args:
        df (pd.DataFrame): Raw video data with analysis_results
        
    Returns:
        pd.DataFrame: Data with all analysis features extracted
    """
    if df.empty:
        logger.warning("Empty DataFrame provided for feature processing")
        return df
    
    logger.info(f"Processing analysis features for {len(df)} videos")
    
    # Extract all feature types
    df = extract_car_features(df)
    df = extract_hook_features(df)
    df = extract_transition_features(df)
    df = extract_general_insights(df)
    
    logger.info(f"Feature processing complete: {len(df.columns)} total columns")
    return df


def get_feature_summary(df: pd.DataFrame) -> dict:
    """
    Generate summary of extracted features.
    
    Args:
        df (pd.DataFrame): Data with extracted features
        
    Returns:
        dict: Summary of feature extraction results
    """
    if df.empty:
        return {'status': 'no_data'}
    
    return {
        'total_videos': len(df),
        'unique_car_brands': df['car_brand'].nunique() if 'car_brand' in df.columns else 0,
        'unique_hooks': df['hook_type'].nunique() if 'hook_type' in df.columns else 0,
        'unique_transitions': df['transition_type'].nunique() if 'transition_type' in df.columns else 0,
        'multi_brand_videos': df['multi_brand_video'].sum() if 'multi_brand_video' in df.columns else 0,
        'multi_hook_videos': df['multi_hook_video'].sum() if 'multi_hook_video' in df.columns else 0,
        'videos_with_ai_titles': df['ai_generated_title'].notna().sum() if 'ai_generated_title' in df.columns else 0
    }