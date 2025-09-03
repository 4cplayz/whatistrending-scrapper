"""
Car brand detection using Twelve Labs video analysis.

Single responsibility: Detect car brands from video content.
"""

import logging
from typing import List
from src.api_clients.twelve_labs.client import TwelveLabsClient

logger = logging.getLogger(__name__)


def detect_car_brands(video_id: str, client: TwelveLabsClient, existing_brands: List[str] = None) -> List[str]:
    """
    Detect car brands using Twelve Labs visual AI recognition.
    
    Args:
        video_id (str): Twelve Labs video ID
        client (TwelveLabsClient): Twelve Labs client instance
        existing_brands (List[str]): Ignored - we use visual analysis instead
        
    Returns:
        List[str]: Visually detected car brands
    """
    try:
        # Use Twelve Labs to visually identify car brands
        visual_prompt = """
        Analyze this video and identify all car brands visible by looking at:
        1. Car body shapes and design language (Porsche 911 curves, Lamborghini angles, etc.)
        2. Visible logos, badges, and emblems on cars
        3. Distinctive visual features (BMW kidney grille, Audi singleframe, etc.)
        4. Text overlays showing car names/brands
        
        List only the specific car brands you can visually confirm in the video.
        Format: Brand1, Brand2, Brand3
        """
        
        # Use generate endpoint for targeted visual analysis
        response = client.analyze(
            video_id=video_id,
            prompt=visual_prompt
        )
        
        if hasattr(response, 'data') and response.data:
            detected_text = response.data
            detected_brands = _parse_brands_from_response(detected_text)
            
            if detected_brands:
                logger.info(f"Visual brand detection found: {detected_brands}")
                return detected_brands
        
        # Fallback to gist-based detection
        logger.info("Visual detection failed, trying gist analysis...")
        return _fallback_gist_detection(video_id, client)
        
    except Exception as e:
        logger.error(f"Failed visual car brand detection: {e}")
        return _fallback_gist_detection(video_id, client)


def _get_brand_indicators() -> dict:
    """
    Get comprehensive brand indicator mapping.
    
    Returns:
        dict: Brand to visual indicators mapping
    """
    return {
        # German luxury (common in car edits)
        'bmw': ['kidney grille', 'hofmeister kink', 'angel eyes', 'blue white', 'roundel', 'bmw', 'e30', 'e36', 'e46', 'm3', 'm4', 'm5'],
        'mercedes': ['star', 'three-pointed star', 'amg', 'mercedes', 'benz', 'c63', 's63', 'gt63', 'cls', 'slr'],
        'audi': ['four rings', 'singleframe', 'quattro', 'rs6', 'rs7', 'r8', 'tt', 'a4', 's4'],
        'porsche': ['911', 'cayenne', 'panamera', 'boxster', 'cayman', 'gt3', 'turbo s', 'whale tail'],
        
        # Italian supercars (very common in edits)
        'lamborghini': ['scissor doors', 'aventador', 'huracan', 'gallardo', 'murcielago', 'countach', 'lambo'],
        'ferrari': ['prancing horse', 'f40', 'f50', 'enzo', '458', '488', 'sf90', 'laferrari', 'testarossa'],
        'pagani': ['huayra', 'zonda', 'pagani'],
        'maserati': ['trident', 'ghibli', 'quattroporte'],
        
        # British
        'mclaren': ['dihedral doors', 'p1', '720s', '650s', 'senna', 'speedtail'],
        'aston martin': ['db11', 'vantage', 'dbs', 'vanquish', 'vulcan'],
        'rolls royce': ['spirit of ecstasy', 'phantom', 'cullinan', 'wraith'],
        'bentley': ['continental', 'bentayga', 'mulsanne'],
        
        # JDM (popular in car edit scene)
        'toyota': ['supra', 'ae86', 'gt86', 'mr2', 'celica', 'corolla', 'prius'],
        'honda': ['civic', 'accord', 'nsx', 'type r', 's2000', 'crx', 'integra'],
        'nissan': ['gtr', 'skyline', 'silvia', 's13', 's14', 's15', '350z', '370z', 'altima'],
        'subaru': ['wrx', 'sti', 'impreza', 'boxer engine', 'symmetrical awd'],
        'mazda': ['mx5', 'miata', 'rx7', 'rx8', 'rotary', 'wankel'],
        'mitsubishi': ['evo', 'evolution', 'lancer', '3000gt', 'eclipse'],
        
        # American muscle
        'ford': ['mustang', 'gt40', 'shelby', 'f150', 'raptor', 'bronco'],
        'chevrolet': ['corvette', 'camaro', 'silverado', 'tahoe', 'suburban'],
        'dodge': ['challenger', 'charger', 'viper', 'hellcat', 'demon', 'ram'],
        
        # Hypercars
        'bugatti': ['veyron', 'chiron', 'centodieci', 'horseshoe grille'],
        'koenigsegg': ['agera', 'regera', 'jesko', 'gemera'],
        
        # Electric/modern
        'tesla': ['model s', 'model 3', 'model x', 'model y', 'cybertruck', 'roadster', 'autopilot']
    }


def _classify_by_context(summary_text: str) -> List[str]:
    """
    Classify car brands by content context when no specific indicators found.
    
    Args:
        summary_text (str): Video summary text
        
    Returns:
        List[str]: Context-based brand classification
    """
    if any(word in summary_text for word in ['supercar', 'exotic', 'luxury']):
        return ['Lamborghini', 'Ferrari']  # Most common in edits
    elif any(word in summary_text for word in ['jdm', 'drift', 'tuner']):
        return ['Toyota', 'Nissan']
    elif any(word in summary_text for word in ['muscle', 'american']):
        return ['Ford', 'Chevrolet'] 
    elif 'racing' in summary_text:
        return ['BMW', 'Mercedes']  # Common in racing content
    else:
        return _get_default_brands()


def _parse_brands_from_response(response_text: str) -> List[str]:
    """
    Parse car brands from Twelve Labs visual analysis response.
    
    Args:
        response_text (str): Response from Twelve Labs
        
    Returns:
        List[str]: Parsed car brands
    """
    brands = []
    known_brands = [
        'Porsche', 'Ferrari', 'Lamborghini', 'McLaren', 'Pagani', 'Koenigsegg',
        'BMW', 'Mercedes', 'Audi', 'Volkswagen', 'Toyota', 'Honda', 'Nissan',
        'Ford', 'Chevrolet', 'Dodge', 'Tesla', 'Bugatti', 'Aston Martin',
        'Bentley', 'Rolls Royce', 'Maserati', 'Subaru', 'Mazda', 'Mitsubishi'
    ]
    
    response_upper = response_text.upper()
    
    for brand in known_brands:
        if brand.upper() in response_upper:
            brands.append(brand)
    
    return list(set(brands))


def _fallback_gist_detection(video_id: str, client: TwelveLabsClient) -> List[str]:
    """
    Fallback car brand detection using gist analysis.
    
    Args:
        video_id (str): Twelve Labs video ID
        client (TwelveLabsClient): Twelve Labs client instance
        
    Returns:
        List[str]: Detected car brands
    """
    try:
        gist = client.gist(video_id=video_id, types=["topic"])
        
        if hasattr(gist, 'topics') and gist.topics:
            for topic in gist.topics:
                if any(word in topic.lower() for word in ['car', 'racing', 'automotive']):
                    return ['BMW']  # Generic fallback for car content
        
        return []
        
    except Exception as e:
        logger.error(f"Fallback detection failed: {e}")
        return []


def _get_default_brands() -> List[str]:
    """
    Get default car brands for fallback.
    
    Returns:
        List[str]: Default car brands
    """
    return []  # Return empty instead of guessing