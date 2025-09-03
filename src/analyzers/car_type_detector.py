"""
Car type detection from video content.

Single responsibility: Detect car types and classifications.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


def detect_car_types(topics: List[str]) -> List[str]:
    """
    Detect car types from video topics.
    
    Args:
        topics (List[str]): List of video topics from Twelve Labs
        
    Returns:
        List[str]: Detected car types
    """
    car_types = []
    car_type_keywords = _get_car_type_keywords()
    
    for topic in topics:
        topic_lower = topic.lower()
        
        for car_type in car_type_keywords:
            if car_type in topic_lower:
                car_types.append(car_type.title())
    
    return list(set(car_types))


def _get_car_type_keywords() -> List[str]:
    """
    Get comprehensive car type keywords for detection.
    
    Returns:
        List[str]: Car type keywords
    """
    return [
        # Performance categories
        'supercar', 'hypercar', 'sports car', 'race car', 'track car',
        'drift car', 'drag car', 'rally car', 'gt car',
        
        # Culture/scene specific
        'jdm', 'muscle car', 'tuner car', 'stance car', 'lowrider',
        'widebody', 'liberty walk', 'rocket bunny', 'bagged car',
        
        # Luxury/exotic
        'luxury car', 'exotic car', 'classic car', 'vintage car',
        'limited edition', 'one-off', 'prototype',
        
        # Body styles common in edits
        'coupe', 'convertible', 'roadster', 'hatchback', 'wagon'
    ]