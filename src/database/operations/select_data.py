"""
Supabase SELECT operations for data retrieval.

Single responsibility: Handle all database SELECT queries.
"""

import logging
from typing import Dict, List, Optional, Any
from src.database.client.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def select_all_from_table(table_name: str, columns: str = "*") -> List[Dict]:
    """
    Fetch all data from specified table with optional column selection.
    
    Args:
        table_name (str): Name of the table to query
        columns (str): Columns to select, defaults to "*"
        
    Returns:
        List[Dict]: List of records from the table
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If query execution fails
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table(table_name).select(columns).execute()
        
        logger.info(f"Selected {len(response.data)} records from {table_name}")
        return response.data
        
    except Exception as e:
        logger.error(f"Failed to select from {table_name}: {e}")
        raise ValueError(f"Select operation failed: {e}")


def select_with_filter(table_name: str, column: str, value: Any) -> List[Dict]:
    """
    Fetch data from table with equality filter.
    
    Args:
        table_name (str): Name of the table to query
        column (str): Column name for filtering
        value (Any): Value to filter by
        
    Returns:
        List[Dict]: Filtered records from the table
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If query execution fails
    """
    try:
        supabase = get_supabase_client()
        response = (
            supabase.table(table_name)
            .select("*")
            .eq(column, value)
            .execute()
        )
        
        logger.info(f"Found {len(response.data)} records in {table_name} where {column}={value}")
        return response.data
        
    except Exception as e:
        logger.error(f"Failed to select from {table_name} with filter: {e}")
        raise ValueError(f"Filtered select failed: {e}")