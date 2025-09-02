"""
Flask application configuration and setup.

Single responsibility: Configure Flask app with all routes.
"""

from flask import Flask
import logging
from src.api.routes.health_routes import create_health_routes

logger = logging.getLogger(__name__)


def create_app():
    """
    Create and configure Flask application with all routes.
    
    Returns:
        Flask: Configured Flask application instance
        
    Raises:
        ImportError: If route modules cannot be imported
    """
    app = Flask(__name__)
    
    # Register health routes
    health_routes = create_health_routes()
    app.register_blueprint(health_routes)
    
    logger.info("Flask application configured successfully")
    return app