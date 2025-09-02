"""
Health check endpoint for Railway monitoring.

Single responsibility: Return service health status.
"""

from flask import jsonify
import time


def health_check():
    """
    Health check endpoint for Railway and monitoring systems.
    
    Returns:
        dict: Health status with timestamp and service info
        
    Raises:
        None: This endpoint should never fail
    """
    return jsonify({
        "status": "healthy",
        "service": "newsletter-scraper",
        "timestamp": time.time(),
        "message": "Service is running correctly"
    })