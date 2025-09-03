"""
Video hook and engagement element detection.

Single responsibility: Detect viral hooks and engagement patterns.
"""

import logging
from typing import Dict, Any, List
from src.api_clients.twelve_labs.client import TwelveLabsClient

logger = logging.getLogger(__name__)


def analyze_video_hooks(video_id: str, client: TwelveLabsClient) -> Dict[str, Any]:
    """
    Analyze video hooks and engagement elements using visual AI.
    
    Args:
        video_id (str): Twelve Labs video ID
        client (TwelveLabsClient): Twelve Labs client instance
        
    Returns:
        Dict[str, Any]: Hook analysis results
    """
    try:
        # Visual hook analysis prompt
        visual_prompt = """
        Analyze this video and identify all visual hooks and engagement elements:
        
        VISUAL HOOKS:
        - "VS" graphics or split-screen comparisons
        - Text overlays like "WAIT FOR IT", "LISTEN TO THIS", "WHICH IS BETTER"
        - Countdown timers or progress bars
        - Question graphics or polls
        - Before/after comparisons
        - Reaction face overlays
        - Challenge or competition graphics
        
        ENGAGEMENT ELEMENTS:
        - Split screen layouts showing comparisons
        - Text animations and callouts
        - Visual arrows pointing to important elements
        - Dramatic zoom-ins on key moments
        - Color-coded sections or categories
        - Social media interface overlays
        - Scoreboard or ranking graphics
        
        List all visual hooks and engagement techniques you see in this video.
        """
        
        response = client.analyze(
            video_id=video_id,
            prompt=visual_prompt
        )
        
        if hasattr(response, 'data') and response.data:
            hooks, engagement_elements = _parse_visual_hooks(response.data)
        else:
            hooks, engagement_elements = [], []
        
        # Get title for additional context
        try:
            title_gist = client.gist(video_id=video_id, types=["title"])
            title = title_gist.title if hasattr(title_gist, 'title') else None
        except:
            title = None
        
        return {
            "hooks": hooks,
            "engagement_elements": engagement_elements,
            "title": title,
            "summary": response.data if hasattr(response, 'data') else None
        }
        
    except Exception as e:
        logger.error(f"Failed visual hook analysis: {e}")
        return {"hooks": [], "engagement_elements": [], "title": None, "summary": None}


def _parse_visual_hooks(response_text: str) -> tuple:
    """
    Parse visual hooks from Twelve Labs visual analysis response.
    
    Args:
        response_text (str): Response from Twelve Labs
        
    Returns:
        tuple: (hooks, engagement_elements) lists
    """
    hooks = []
    engagement_elements = []
    
    response_lower = response_text.lower()
    
    # Visual hook patterns
    hook_patterns = {
        'vs': 'VS comparison graphics',
        'versus': 'VS comparison graphics',
        'wait for it': 'Wait for it text overlay',
        'listen to this': 'Listen to this callout',
        'which is better': 'Which is better question',
        'countdown': 'Countdown timer',
        'progress bar': 'Progress indicator',
        'before/after': 'Before/after comparison',
        'reaction': 'Reaction overlay',
        'challenge': 'Challenge graphics',
        'competition': 'Competition format',
        'poll': 'Poll or voting graphics',
        'question': 'Question graphics'
    }
    
    # Engagement element patterns  
    engagement_patterns = {
        'split screen': 'Split screen layout',
        'text animation': 'Text animations',
        'callout': 'Text callouts',
        'arrow': 'Visual arrows',
        'zoom': 'Dramatic zoom effects',
        'color-coded': 'Color-coded sections',
        'social media': 'Social media overlays',
        'scoreboard': 'Scoreboard graphics',
        'ranking': 'Ranking display',
        'highlight': 'Visual highlights',
        'overlay': 'Graphic overlays'
    }
    
    # Check for visual hooks
    for pattern, description in hook_patterns.items():
        if pattern in response_lower:
            hooks.append(description)
    
    # Check for engagement elements
    for pattern, description in engagement_patterns.items():
        if pattern in response_lower:
            engagement_elements.append(description)
    
    return list(set(hooks)), list(set(engagement_elements))


def _detect_hooks_from_title(title_text: str) -> List[str]:
    """
    Detect hook patterns from video title.
    
    Args:
        title_text (str): Video title text
        
    Returns:
        List[str]: Detected hook patterns
    """
    hooks = []
    title_lower = title_text.lower()
    hook_patterns = _get_hook_patterns()
    
    for pattern in hook_patterns:
        if pattern in title_lower:
            hooks.append(f"Uses '{pattern}' hook")
    
    return hooks


def _detect_engagement_elements(summary_text: str) -> List[str]:
    """
    Detect engagement elements from video summary.
    
    Args:
        summary_text (str): Video summary text
        
    Returns:
        List[str]: Detected engagement elements
    """
    engagement_elements = []
    summary_lower = summary_text.lower()
    engagement_patterns = _get_engagement_patterns()
    
    for pattern, description in engagement_patterns:
        if pattern in summary_lower:
            engagement_elements.append(description)
    
    return engagement_elements


def _get_hook_patterns() -> List[str]:
    """
    Get comprehensive hook patterns for detection.
    
    Returns:
        List[str]: Hook patterns
    """
    return [
        # Universal viral hooks
        'insane', 'crazy', 'epic', 'mind-blowing', 'incredible',
        'unbelievable', 'amazing', 'shocking', 'viral', 'trending',
        'omg', 'wtf', 'no way', 'insanely', 'absolutely',
        
        # Creative viral hooks (universal appeal)
        'you won\'t believe', 'wait until you see', 'this is why',
        'when you', 'pov:', 'tell me why', 'nobody talks about',
        'the reason why', 'this is what happens', 'watch this',
        'you need to see', 'i can\'t believe', 'this happened',
        
        # Content type hooks (anime, girls, gaming, etc.)
        'anime', 'waifu', 'kawaii', 'otaku', 'manga', 'cosplay',
        'girl', 'girls', 'model', 'beauty', 'aesthetic', 'pretty',
        'gaming', 'gamer', 'video game', 'gameplay', 'streamer',
        'blender', '3d animation', 'cgi', 'vfx', 'render',
        'edit', 'editing', 'tutorial', 'how to', 'behind the scenes',
        
        # TikTok viral formats
        'pov:', 'me when', 'that one', 'when the', 'this guy',
        'watch till the end', 'part 2', 'storytime', 'day in my life',
        'things that', 'people who', 'if you know you know',
        
        # Car edit specific hooks
        'wait for it', 'wait for the drop', 'listen to this',
        'sound check', 'exhaust note', 'launch', '0-60', 'acceleration',
        
        # Comparison/competitive hooks
        'vs', 'versus', 'battle', 'showdown', 'face off',
        'comparison', 'which is faster', 'better', 'who wins',
        
        # Reaction/engagement hooks
        'reaction', 'first time', 'hear this', 'see this',
        'check this out', 'must see', 'you have to',
        
        # Performance/test hooks
        'test', 'dyno', 'track', 'drag race', 'pulls',
        'pov', 'onboard', 'ride along', 'full send',
        
        # Emotional/aesthetic hooks
        'satisfying', 'oddly satisfying', 'so clean', 'perfection',
        'aesthetic', 'vibes', 'energy', 'mood', 'art', 'artistic'
    ]


def _get_engagement_patterns() -> List[tuple]:
    """
    Get engagement patterns for detection.
    
    Returns:
        List[tuple]: Pattern and description pairs
    """
    return [
        # Audio engagement (critical for car edits)
        ('sound', 'Audio-focused content'), ('exhaust', 'Exhaust sound focus'),
        ('music', 'Music-driven engagement'), ('bass', 'Bass-heavy content'),
        ('audio', 'Audio-centric'), ('listen', 'Audio engagement'),
        
        # Visual engagement
        ('edit', 'Editing-focused content'), ('transition', 'Transition showcase'),
        ('compilation', 'Compilation format'), ('montage', 'Montage style'),
        
        # Performance engagement
        ('acceleration', 'Performance showcase'), ('speed', 'Speed-focused'),
        ('launch', 'Launch showcase'), ('power', 'Power demonstration'),
        ('dyno', 'Dyno testing'), ('track', 'Track performance'),
        
        # Visual spectacle
        ('flame', 'Flame spectacle'), ('smoke', 'Smoke effects'),
        ('burnout', 'Burnout showcase'), ('drift', 'Drift action'),
        
        # Narrative engagement
        ('rivalry', 'Rivalry narrative'), ('versus', 'Comparison content'),
        ('battle', 'Battle format'), ('showdown', 'Showdown narrative')
    ]