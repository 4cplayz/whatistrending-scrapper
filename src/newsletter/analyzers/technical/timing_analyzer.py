"""
Analyze upload timing patterns for viral performance impact.
Single responsibility: Upload timing performance analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_upload_hour_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance by hour of upload.
    
    Args:
        df (pd.DataFrame): Video data with created_at and viral metrics
        
    Returns:
        Dict[str, Any]: Upload hour performance analysis
        
    Raises:
        ValueError: If required columns are missing
    """
    if 'created_at' not in df.columns:
        raise ValueError("created_at column is required")
    
    # Convert created_at to datetime
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['upload_hour'] = df['created_at'].dt.hour
    
    hour_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for hour in range(24):
        hour_data = df[df['upload_hour'] == hour]
        if len(hour_data) == 0:
            continue
            
        hour_analysis[f"hour_{hour:02d}"] = {
            'avg_views': float(hour_data['views'].mean()),
            'avg_engagement': float(hour_data['engagement_rate'].mean()),
            'viral_impact_score': float(hour_data['viral_score'].mean()),
            'video_count': len(hour_data),
            'viral_videos': int((hour_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((hour_data['views'] >= viral_threshold).mean()),
            'time_slot': _get_time_slot(hour)
        }
    
    # Find peak performance hours
    if hour_analysis:
        peak_hour = max(hour_analysis.items(), key=lambda x: x[1]['avg_views'])
        hour_analysis['peak_performance'] = {
            'best_hour': peak_hour[0],
            'avg_views': peak_hour[1]['avg_views'],
            'time_slot': peak_hour[1]['time_slot']
        }
    
    logger.info(f"Analyzed upload hour performance: {len(hour_analysis)} hours with data")
    return hour_analysis


def analyze_day_of_week_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance by day of week upload.
    
    Args:
        df (pd.DataFrame): Video data with created_at and viral metrics
        
    Returns:
        Dict[str, Any]: Day of week performance analysis
    """
    if 'created_at' not in df.columns:
        logger.warning("created_at column missing")
        return {}
    
    # Convert created_at to datetime
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['upload_day'] = df['created_at'].dt.day_name()
    df['upload_weekday'] = df['created_at'].dt.weekday  # 0=Monday, 6=Sunday
    
    day_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    for day in df['upload_day'].dropna().unique():
        day_data = df[df['upload_day'] == day]
        if len(day_data) == 0:
            continue
            
        day_analysis[day] = {
            'avg_views': float(day_data['views'].mean()),
            'avg_engagement': float(day_data['engagement_rate'].mean()),
            'viral_impact_score': float(day_data['viral_score'].mean()),
            'video_count': len(day_data),
            'viral_videos': int((day_data['views'] >= viral_threshold).sum()),
            'viral_success_rate': float((day_data['views'] >= viral_threshold).mean()),
            'is_weekend': day in ['Saturday', 'Sunday']
        }
    
    # Compare weekday vs weekend performance
    weekdays = df[~df['upload_day'].isin(['Saturday', 'Sunday'])]
    weekends = df[df['upload_day'].isin(['Saturday', 'Sunday'])]
    
    if len(weekdays) > 0 and len(weekends) > 0:
        day_analysis['weekday_vs_weekend'] = {
            'weekday_avg_views': float(weekdays['views'].mean()),
            'weekend_avg_views': float(weekends['views'].mean()),
            'weekend_advantage': float(weekends['views'].mean() / weekdays['views'].mean()) if weekdays['views'].mean() > 0 else 0
        }
    
    logger.info(f"Analyzed day of week performance: {len(day_analysis)} patterns found")
    return day_analysis


def analyze_time_slot_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze viral performance by time slots (morning, afternoon, evening, night).
    
    Args:
        df (pd.DataFrame): Video data with upload timing
        
    Returns:
        Dict[str, Any]: Time slot performance analysis
    """
    if 'created_at' not in df.columns:
        logger.warning("created_at column missing")
        return {}
    
    # Convert created_at to datetime and extract hour
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['upload_hour'] = df['created_at'].dt.hour
    df['time_slot'] = df['upload_hour'].apply(_get_time_slot)
    
    slot_analysis = {}
    viral_threshold = df['views'].quantile(0.8)
    
    time_slots = ['Early_Morning', 'Morning', 'Afternoon', 'Evening', 'Night', 'Late_Night']
    
    for slot in time_slots:
        slot_data = df[df['time_slot'] == slot]
        if len(slot_data) == 0:
            continue
            
        slot_analysis[slot] = {
            'avg_views': float(slot_data['views'].mean()),
            'avg_engagement': float(slot_data['engagement_rate'].mean()),
            'viral_impact_score': float(slot_data['viral_score'].mean()),
            'video_count': len(slot_data),
            'viral_success_rate': float((slot_data['views'] >= viral_threshold).mean()),
            'hour_range': _get_slot_hours(slot),
            'engagement_velocity': float((slot_data['engagement_rate'] / slot_data['duration']).mean()) if 'duration' in slot_data.columns else 0
        }
    
    # Find optimal time slot
    if slot_analysis:
        best_slot = max(slot_analysis.items(), key=lambda x: x[1]['avg_views'])
        slot_analysis['optimal_time_slot'] = {
            'slot': best_slot[0],
            'avg_views': best_slot[1]['avg_views'],
            'hour_range': best_slot[1]['hour_range']
        }
    
    logger.info(f"Analyzed time slot performance: {len(slot_analysis)} slots")
    return slot_analysis


def analyze_upload_recency_impact(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze how video age affects current performance.
    
    Args:
        df (pd.DataFrame): Video data with upload timestamps
        
    Returns:
        Dict[str, Any]: Upload recency impact analysis
    """
    if 'created_at' not in df.columns:
        logger.warning("created_at column missing")
        return {}
    
    # Convert created_at to datetime
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    current_time = pd.Timestamp.now()
    df['hours_since_upload'] = (current_time - df['created_at']).dt.total_seconds() / 3600
    df['days_since_upload'] = df['hours_since_upload'] / 24
    
    recency_analysis = {}
    
    # Categorize by recency
    recency_categories = {
        'very_recent': (0, 6),      # Last 6 hours
        'recent': (6, 24),          # Last day
        'day_old': (24, 48),        # 1-2 days
        'several_days': (48, 168),  # 2-7 days
        'week_plus': (168, float('inf'))  # Over a week
    }
    
    for category, (min_hours, max_hours) in recency_categories.items():
        category_data = df[
            (df['hours_since_upload'] >= min_hours) & 
            (df['hours_since_upload'] < max_hours)
        ]
        
        if len(category_data) == 0:
            continue
            
        recency_analysis[category] = {
            'avg_views': float(category_data['views'].mean()),
            'avg_engagement': float(category_data['engagement_rate'].mean()),
            'video_count': len(category_data),
            'avg_hours_old': float(category_data['hours_since_upload'].mean()),
            'views_per_hour': float(category_data['views'].mean() / category_data['hours_since_upload'].mean()) if category_data['hours_since_upload'].mean() > 0 else 0
        }
    
    # Analyze views per hour decay
    if len(df) > 5:
        views_time_corr = df['hours_since_upload'].corr(df['views'])
        recency_analysis['time_decay_correlation'] = float(views_time_corr)
    
    logger.info(f"Analyzed upload recency impact: {len(recency_analysis)} categories")
    return recency_analysis


def get_optimal_upload_timing(timing_analyses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine optimal upload timing based on all timing analyses.
    
    Args:
        timing_analyses (Dict[str, Any]): Combined timing analysis results
        
    Returns:
        Dict[str, Any]: Optimal upload timing recommendations
    """
    recommendations = {}
    
    # Extract best hour if available
    if 'hour_analysis' in timing_analyses and 'peak_performance' in timing_analyses['hour_analysis']:
        peak_data = timing_analyses['hour_analysis']['peak_performance']
        recommendations['best_hour'] = {
            'hour': peak_data['best_hour'],
            'time_slot': peak_data['time_slot'],
            'expected_views': peak_data['avg_views']
        }
    
    # Extract best day if available
    if 'day_analysis' in timing_analyses:
        day_data = timing_analyses['day_analysis']
        if day_data:
            best_day = max(
                [(day, data) for day, data in day_data.items() if day not in ['weekday_vs_weekend']],
                key=lambda x: x[1].get('avg_views', 0)
            )
            recommendations['best_day'] = {
                'day': best_day[0],
                'expected_views': best_day[1]['avg_views']
            }
    
    # Extract best time slot if available
    if 'slot_analysis' in timing_analyses and 'optimal_time_slot' in timing_analyses['slot_analysis']:
        slot_data = timing_analyses['slot_analysis']['optimal_time_slot']
        recommendations['best_time_slot'] = {
            'slot': slot_data['slot'],
            'hour_range': slot_data['hour_range'],
            'expected_views': slot_data['avg_views']
        }
    
    logger.info("Generated optimal upload timing recommendations")
    return recommendations


def _get_time_slot(hour: int) -> str:
    """Get time slot name for a given hour."""
    if 5 <= hour < 8:
        return "Early_Morning"
    elif 8 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 20:
        return "Evening"
    elif 20 <= hour < 24:
        return "Night"
    else:  # 0 <= hour < 5
        return "Late_Night"


def _get_slot_hours(slot: str) -> str:
    """Get hour range for a time slot."""
    slot_ranges = {
        'Early_Morning': '5AM-8AM',
        'Morning': '8AM-12PM',
        'Afternoon': '12PM-5PM',
        'Evening': '5PM-8PM',
        'Night': '8PM-12AM',
        'Late_Night': '12AM-5AM'
    }
    return slot_ranges.get(slot, 'Unknown')


def get_timing_analysis_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of upload timing analysis.
    
    Args:
        df (pd.DataFrame): Video data with timing features
        
    Returns:
        Dict[str, Any]: Timing analysis summary
    """
    if df.empty or 'created_at' not in df.columns:
        return {'status': 'no_data'}
    
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['upload_hour'] = df['created_at'].dt.hour
    df['upload_day'] = df['created_at'].dt.day_name()
    
    return {
        'total_videos': len(df),
        'time_range': (
            str(df['created_at'].min()),
            str(df['created_at'].max())
        ),
        'most_active_hour': int(df['upload_hour'].mode().iloc[0]) if len(df['upload_hour'].mode()) > 0 else None,
        'most_active_day': df['upload_day'].mode().iloc[0] if len(df['upload_day'].mode()) > 0 else None,
        'weekend_uploads': int(df['upload_day'].isin(['Saturday', 'Sunday']).sum()),
        'weekday_uploads': int(~df['upload_day'].isin(['Saturday', 'Sunday']).sum())
    }