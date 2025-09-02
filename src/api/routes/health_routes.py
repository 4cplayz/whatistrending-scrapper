"""
Health and status route definitions.

Single responsibility: Define Flask routes for health checking.
"""

from flask import Blueprint
from src.api.endpoints.health_check import health_check
from src.api.endpoints.service_status import get_service_status
from src.api.endpoints.welcome import get_welcome


def create_health_routes():
    """
    Create Blueprint with health and status routes.
    
    Returns:
        Blueprint: Flask blueprint with health routes configured
        
    Raises:
        None: Route creation should not fail
    """
    health_bp = Blueprint('health', __name__)
    
    health_bp.add_url_rule('/', 'welcome', get_welcome, methods=['GET'])
    health_bp.add_url_rule('/health', 'health_check', health_check, methods=['GET'])  
    health_bp.add_url_rule('/status', 'service_status', get_service_status, methods=['GET'])
    
    return health_bp