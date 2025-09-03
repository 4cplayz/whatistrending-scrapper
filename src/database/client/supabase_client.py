"""
Supabase client initialization and connection management.

Single responsibility: Create and configure Supabase client instance.
"""

import os
import logging
from supabase import create_client, Client
from typing import Optional

logger = logging.getLogger(__name__)


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
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        # Create client without additional options that might cause issues
        supabase = create_client(url, key)
        logger.info("Supabase client initialized successfully")
        return supabase
        
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise ConnectionError(f"Supabase connection failed: {e}")