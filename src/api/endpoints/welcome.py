"""
Welcome endpoint for main API landing page.

Single responsibility: Return welcome message for API root.
"""

from flask import jsonify
from datetime import datetime


def get_welcome():
    """
    Main API welcome endpoint with basic service information.
    
    Returns:
        dict: Welcome message and service basics
        
    Raises:
        None: Welcome endpoint should always work
    """
    return jsonify({
        "message": "Newsletter Scraper Service API 🚀",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    })