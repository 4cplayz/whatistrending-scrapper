"""
Supabase client initialization and connection management.

Single responsibility: Create and configure Supabase client instance.
"""

import os
import logging
from supabase import create_client, Client
from typing import Optional

logger = logging.getLogger(__name__)

# Import after logger to avoid circular imports
def _log_database_failure(operation: str, error_message: str, context=None):
    """Internal helper to log database failures without circular import."""
    try:
        from src.utils.error_logger import log_database_failure
        log_database_failure(operation, error_message, context)
    except ImportError:
        logger.error(f"Could not log database failure: {error_message}")


def get_supabase_client() -> Optional[Client]:
    """
    Initialize and return Supabase client with environment configuration.
    
    Returns:
        Client: Configured Supabase client instance
        
    Raises:
        ValueError: If required environment variables are missing
        ConnectionError: If client creation fails
    """
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            error_msg = "SUPABASE_URL and SUPABASE_KEY must be set"
            _log_database_failure("client_initialization", error_msg)
            raise ValueError(error_msg)
        
        # Create client without additional options that might cause issues
        supabase = create_client(url, key)
        logger.info("Supabase client initialized successfully")
        return supabase
        
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        _log_database_failure("client_creation", f"Supabase connection failed: {str(e)}")
        raise ConnectionError(f"Supabase connection failed: {e}")