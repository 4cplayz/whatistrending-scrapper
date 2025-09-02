"""
Apify client initialization and configuration.

Single responsibility: Create and configure Apify client instance.
"""

import os
import logging
from apify_client import ApifyClient
from typing import Optional

logger = logging.getLogger(__name__)


def get_apify_client() -> Optional[ApifyClient]:
    """
    Initialize and return Apify client with environment configuration.
    
    Returns:
        ApifyClient: Configured Apify client instance
        
    Raises:
        ValueError: If APIFY_TOKEN environment variable is missing
        ConnectionError: If client creation fails
    """
    try:
        token = os.environ.get("APIFY_TOKEN")
        
        if not token:
            raise ValueError("APIFY_TOKEN environment variable must be set")
        
        client = ApifyClient(token)
        logger.info("Apify client initialized successfully")
        return client
        
    except Exception as e:
        logger.error(f"Failed to create Apify client: {e}")
        raise ConnectionError(f"Apify client creation failed: {e}")