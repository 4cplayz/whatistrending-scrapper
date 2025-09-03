"""
Video transition and effect analysis.

Single responsibility: Detect video transitions, effects, and editing style.
"""

import logging
from typing import Dict, Any, List
from src.api_clients.twelve_labs.client import TwelveLabsClient

logger = logging.getLogger(__name__)


def analyze_transitions(video_id: str, client: TwelveLabsClient) -> Dict[str, Any]:
    """
    Analyze video transitions and effects using visual AI analysis.
    
    Args:
        video_id (str): Twelve Labs video ID
        client (TwelveLabsClient): Twelve Labs client instance
        
    Returns:
        Dict[str, Any]: Transition analysis results
    """
    try:
        # Use Twelve Labs to visually analyze editing techniques
        visual_prompt = """
        Analyze this video frame-by-frame and identify all editing techniques:
        
        TRANSITIONS:
        - Quick cuts between shots
        - Speed ramping (slow motion to fast motion)
        - Beat drops synced to music
        - Zoom in/out effects
        - Camera pans and tilts
        - Flash/strobe transitions
        - Screen shakes or bounces
        
        VISUAL EFFECTS:
        - Color grading and filters
        - Motion blur effects
        - Glow/neon lighting effects
        - Particle effects or sparks
        - Text overlays and graphics
        - Split screen effects
        - Chromatic aberration or glitch effects
        
        List all techniques you can visually identify in this video.
        """
        
        response = client.analyze(
            video_id=video_id,
            prompt=visual_prompt
        )
        
        if hasattr(response, 'data') and response.data:
            transitions, effects = _parse_editing_techniques(response.data)
        else:
            transitions, effects = [], []
        
        editing_style = _determine_editing_style(transitions + effects)
        
        return {
            "transitions": transitions,
            "effects": effects,
            "style": editing_style
        }
        
    except Exception as e:
        logger.error(f"Failed visual transition analysis: {e}")
        return {"transitions": [], "effects": [], "style": "Unknown"}


def _parse_editing_techniques(response_text: str) -> tuple:
    """
    Parse editing techniques from Twelve Labs visual analysis response.
    
    Args:
        response_text (str): Response from Twelve Labs
        
    Returns:
        tuple: (transitions, effects) lists
    """
    transitions = []
    effects = []
    
    response_lower = response_text.lower()
    
    # Visual transitions
    transition_patterns = {
        'quick cut': 'Quick cuts',
        'cut': 'Quick cuts',
        'speed ramp': 'Speed ramping',
        'slow motion': 'Slow motion',
        'fast motion': 'Speed ramping',
        'beat drop': 'Beat drop sync',
        'music sync': 'Music synchronized',
        'zoom': 'Zoom effects',
        'pan': 'Camera pans',
        'tilt': 'Camera tilts',
        'flash': 'Flash transitions',
        'strobe': 'Strobe effects',
        'shake': 'Screen shake',
        'bounce': 'Bounce effects'
    }
    
    # Visual effects
    effect_patterns = {
        'color grade': 'Color grading',
        'color filter': 'Color filters',
        'motion blur': 'Motion blur',
        'blur': 'Motion blur',
        'glow': 'Glow effects',
        'neon': 'Neon effects',
        'particle': 'Particle effects',
        'spark': 'Spark effects',
        'text overlay': 'Text overlays',
        'split screen': 'Split screen',
        'chromatic': 'Chromatic aberration',
        'glitch': 'Glitch effects'
    }
    
    # Check for transitions
    for pattern, description in transition_patterns.items():
        if pattern in response_lower:
            transitions.append(description)
    
    # Check for effects
    for pattern, description in effect_patterns.items():
        if pattern in response_lower:
            effects.append(description)
    
    return list(set(transitions)), list(set(effects))


def _detect_transitions(summary_text: str) -> List[str]:
    """
    Detect transition techniques from summary.
    
    Args:
        summary_text (str): Video summary text
        
    Returns:
        List[str]: Detected transitions
    """
    transitions = []
    transition_keywords = _get_transition_keywords()
    
    for keyword, description in transition_keywords:
        if keyword in summary_text:
            transitions.append(description)
    
    return transitions


def _detect_effects(summary_text: str) -> List[str]:
    """
    Detect visual effects from summary.
    
    Args:
        summary_text (str): Video summary text
        
    Returns:
        List[str]: Detected effects
    """
    effects = []
    effect_keywords = _get_effect_keywords()
    
    for keyword, description in effect_keywords:
        if keyword in summary_text:
            effects.append(description)
    
    return effects


def _get_transition_keywords() -> List[tuple]:
    """
    Get transition keywords for car edit detection.
    
    Returns:
        List[tuple]: Keyword and description pairs
    """
    return [
        # Basic cuts and timing
        ('cut', 'Quick cuts'), ('quick cut', 'Quick cuts'),
        ('fast cut', 'Quick cuts'), ('rapid cut', 'Quick cuts'),
        
        # Music synchronization (critical for car edits)
        ('beat drop', 'Beat drop sync'), ('drop', 'Beat drop sync'),
        ('bass drop', 'Bass drop sync'), ('sync', 'Music sync'),
        ('beat sync', 'Beat synchronized'), ('on beat', 'Beat synchronized'),
        
        # Speed effects
        ('slow motion', 'Slow motion'), ('slow mo', 'Slow motion'),
        ('speed up', 'Speed ramping'), ('speed ramp', 'Speed ramping'),
        ('velocity', 'Speed effects'), ('fast forward', 'Speed ramping'),
        
        # Visual transitions
        ('zoom', 'Zoom effects'), ('zoom in', 'Zoom effects'),
        ('pan', 'Camera pans'), ('tilt', 'Camera tilts'),
        ('whip pan', 'Whip pans'), ('sweep', 'Sweep transitions'),
        
        # Fade effects
        ('fade', 'Fade transitions'), ('fade in', 'Fade transitions'),
        ('fade out', 'Fade transitions'), ('crossfade', 'Crossfade'),
        
        # Advanced car edit techniques
        ('flip', 'Screen flip'), ('spin', 'Spin transitions'),
        ('shake', 'Screen shake'), ('bounce', 'Bounce effects'),
        ('flash', 'Flash transitions'), ('strobe', 'Strobe effects')
    ]


def _get_effect_keywords() -> List[tuple]:
    """
    Get visual effect keywords for car edit detection.
    
    Returns:
        List[tuple]: Keyword and description pairs
    """
    return [
        # Color grading and filters
        ('filter', 'Color filters'), ('color grade', 'Color grading'),
        ('color correction', 'Color grading'), ('saturation', 'Color enhancement'),
        ('contrast', 'Contrast effects'), ('brightness', 'Brightness effects'),
        
        # Glow and lighting
        ('glow', 'Glow effects'), ('neon', 'Neon effects'),
        ('light', 'Lighting effects'), ('flare', 'Lens flare'),
        ('lens flare', 'Lens flare'), ('rim light', 'Rim lighting'),
        
        # Motion effects
        ('blur', 'Motion blur'), ('motion blur', 'Motion blur'),
        ('radial blur', 'Radial blur'), ('zoom blur', 'Zoom blur'),
        ('shake', 'Camera shake'), ('vibration', 'Shake effects'),
        
        # Distortion and aesthetics
        ('vhs', 'VHS aesthetic'), ('glitch', 'Glitch effects'),
        ('chromatic', 'Chromatic aberration'), ('film grain', 'Film grain'),
        ('vintage', 'Vintage effects'), ('retro', 'Retro effects'),
        
        # Particle and energy effects
        ('particle', 'Particle effects'), ('spark', 'Spark effects'),
        ('smoke', 'Smoke effects'), ('fire', 'Fire effects'),
        ('energy', 'Energy effects'), ('electric', 'Electric effects'),
        
        # Car edit specific
        ('exhaust', 'Exhaust effects'), ('flame', 'Flame effects'),
        ('backfire', 'Backfire effects'), ('tire smoke', 'Tire smoke')
    ]


def _determine_editing_style(elements: List[str]) -> str:
    """
    Determine car edit specific editing style based on elements.
    
    Args:
        elements (List[str]): List of transition and effect elements
        
    Returns:
        str: Determined editing style
    """
    if not elements:
        return "Minimal"
    
    # Check for high-energy car edit indicators
    high_energy_indicators = [
        'Beat drop sync', 'Bass drop sync', 'Quick cuts', 'Speed ramping',
        'Strobe effects', 'Flash transitions', 'Screen shake'
    ]
    
    music_sync_indicators = [
        'Beat drop sync', 'Bass drop sync', 'Beat synchronized', 'Music sync'
    ]
    
    # Advanced car edit techniques
    advanced_indicators = [
        'Color grading', 'Motion blur', 'Particle effects', 'Glitch effects',
        'Chromatic aberration', 'Flame effects', 'Exhaust effects'
    ]
    
    high_energy_count = sum(1 for elem in elements if elem in high_energy_indicators)
    music_sync_count = sum(1 for elem in elements if elem in music_sync_indicators)
    advanced_count = sum(1 for elem in elements if elem in advanced_indicators)
    
    # Determine style based on sophisticated analysis
    if high_energy_count >= 3 or music_sync_count >= 2:
        return "High-energy car edit"
    elif advanced_count >= 2:
        return "Cinematic car edit"
    elif music_sync_count >= 1:
        return "Music-synced edit"
    elif len(elements) >= 4:
        return "Heavy editing"
    elif len(elements) >= 2:
        return "Moderate editing"
    else:
        return "Light editing"