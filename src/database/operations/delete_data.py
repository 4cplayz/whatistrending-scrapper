"""
Supabase DELETE operations for data removal.

Single responsibility: Handle all database DELETE queries.
"""

import logging
from typing import List, Dict, Any
from src.database.client.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def delete_record_by_id(table_name: str, record_id: Any) -> Dict:
    """
    Delete a single record by its ID.
    
    Args:
        table_name (str): Name of the table to delete from
        record_id (Any): ID of the record to delete
        
    Returns:
        Dict: Deleted record data (if any)
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If delete operation fails
    """
    try:
        supabase = get_supabase_client()
        response = (
            supabase.table(table_name)
            .delete()
            .eq("id", record_id)
            .execute()
        )
        
        logger.info(f"Deleted record {record_id} from {table_name}")
        return response.data[0] if response.data else {}
        
    except Exception as e:
        logger.error(f"Failed to delete record {record_id} from {table_name}: {e}")
        raise ValueError(f"Delete operation failed: {e}")


def delete_records_with_filter(table_name: str, column: str, value: Any) -> List[Dict]:
    """
    Delete multiple records matching a filter condition.
    
    Args:
        table_name (str): Name of the table to delete from
        column (str): Column to filter by
        value (Any): Value to match for deletion
        
    Returns:
        List[Dict]: List of deleted records
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If delete operation fails
    """
    try:
        supabase = get_supabase_client()
        response = (
            supabase.table(table_name)
            .delete()
            .eq(column, value)
            .execute()
        )
        
        count = len(response.data) if response.data else 0
        logger.info(f"Deleted {count} records from {table_name}")
        return response.data or []
        
    except Exception as e:
        logger.error(f"Failed to delete records from {table_name}: {e}")
        raise ValueError(f"Bulk delete operation failed: {e}")


def delete_multiple_by_ids(table_name: str, record_ids: List[Any]) -> List[Dict]:
    """
    Delete multiple records by their IDs.
    
    Args:
        table_name (str): Name of the table to delete from
        record_ids (List[Any]): List of IDs to delete
        
    Returns:
        List[Dict]: List of deleted records
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If delete operation fails
    """
    try:
        supabase = get_supabase_client()
        response = (
            supabase.table(table_name)
            .delete()
            .in_("id", record_ids)
            .execute()
        )
        
        count = len(response.data) if response.data else 0
        logger.info(f"Deleted {count} records from {table_name}")
        return response.data or []
        
    except Exception as e:
        logger.error(f"Failed to delete multiple records from {table_name}: {e}")
        raise ValueError(f"Multiple delete operation failed: {e}")