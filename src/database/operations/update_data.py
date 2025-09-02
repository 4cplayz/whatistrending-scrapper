"""
Supabase UPDATE operations for data modification.

Single responsibility: Handle all database UPDATE queries.
"""

import logging
from typing import Dict, List, Any
from src.database.client.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def update_record_by_id(table_name: str, record_id: Any, data: Dict[str, Any]) -> Dict:
    """
    Update a single record by its ID.
    
    Args:
        table_name (str): Name of the table to update
        record_id (Any): ID of the record to update
        data (Dict[str, Any]): Fields to update
        
    Returns:
        Dict: Updated record data
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If update operation fails
    """
    try:
        supabase = get_supabase_client()
        response = (
            supabase.table(table_name)
            .update(data)
            .eq("id", record_id)
            .execute()
        )
        
        logger.info(f"Updated record {record_id} in {table_name}")
        return response.data[0] if response.data else {}
        
    except Exception as e:
        logger.error(f"Failed to update record {record_id} in {table_name}: {e}")
        raise ValueError(f"Update operation failed: {e}")


def update_records_with_filter(table_name: str, filter_column: str, 
                              filter_value: Any, data: Dict[str, Any]) -> List[Dict]:
    """
    Update multiple records matching a filter condition.
    
    Args:
        table_name (str): Name of the table to update
        filter_column (str): Column to filter by
        filter_value (Any): Value to match for updates
        data (Dict[str, Any]): Fields to update
        
    Returns:
        List[Dict]: List of updated records
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If update operation fails
    """
    try:
        supabase = get_supabase_client()
        response = (
            supabase.table(table_name)
            .update(data)
            .eq(filter_column, filter_value)
            .execute()
        )
        
        count = len(response.data) if response.data else 0
        logger.info(f"Updated {count} records in {table_name}")
        return response.data or []
        
    except Exception as e:
        logger.error(f"Failed to update records in {table_name}: {e}")
        raise ValueError(f"Bulk update operation failed: {e}")