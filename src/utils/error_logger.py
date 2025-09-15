"""
Error logging utility for critical action failures.

Single responsibility: Log failed database operations, newsletter generation, and API calls to Supabase.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def log_failed_action(
    action_type: str,
    action_name: str,
    error_message: str,
    additional_context: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Log a failed action to the database for monitoring.

    Args:
        action_type (str): Type of action ('database', 'newsletter_generation', 'api_call')
        action_name (str): Specific action name ('supabase_insert', 'weekly_newsletter', 'apify_scrape')
        error_message (str): Error description
        additional_context (Optional[Dict[str, Any]]): Additional context data

    Returns:
        bool: True if logged successfully, False if logging failed

    Raises:
        None: Errors are caught and logged locally to prevent cascading failures
    """
    try:
        # Avoid circular dependency - don't log database connection errors to database
        if action_type == "database" and "client" in action_name.lower():
            logger.error(f"🔄 Skipping database logging for client error: {error_message}")
            return False

        from src.database.client.supabase_client import get_supabase_client

        client = get_supabase_client()

        error_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_type,
            "action_name": action_name,
            "error_message": error_message,
            "additional_context": additional_context or {}
        }

        result = client.table('failed_actions').insert(error_record).execute()

        if result.data:
            logger.info(f"✅ Logged failed action: {action_type}.{action_name}")
            return True
        else:
            logger.warning(f"⚠️ Failed to log action failure (no data returned)")
            return False

    except Exception as e:
        # Never let error logging break the main application
        logger.error(f"❌ Error logger itself failed: {e}")
        return False


# Convenience functions for common failure types
def log_database_failure(operation: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> bool:
    """Log database operation failure."""
    return log_failed_action("database", operation, error_message, context)


def log_newsletter_failure(stage: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> bool:
    """Log newsletter generation failure."""
    return log_failed_action("newsletter_generation", stage, error_message, context)


def log_api_failure(api_name: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> bool:
    """Log external API call failure."""
    return log_failed_action("api_call", api_name, error_message, context)