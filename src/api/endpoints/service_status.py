"""
Service status endpoint showing API information.

Single responsibility: Return API status and available endpoints.
"""

from flask import jsonify
from datetime import datetime


def get_service_status():
    """
    Get comprehensive service status and endpoint documentation.
    
    Returns:
        dict: Service information with available endpoints
        
    Raises:
        None: Status check should always succeed
    """
    return jsonify({
        "service": "Newsletter Scraper Service",
        "version": "1.0.0", 
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": 3,
        "message": "API is operational"
    })