"""
Supabase INSERT operations for data creation.

Single responsibility: Handle all database INSERT queries.
"""

import logging
from typing import Dict, List, Union, Any
from src.database.client.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def insert_single_record(table_name: str, data: Dict[str, Any]) -> Dict:
    """
    Insert a single record into specified table.
    
    Args:
        table_name (str): Name of the table to insert into
        data (Dict[str, Any]): Record data to insert
        
    Returns:
        Dict: Inserted record with generated fields
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If insert operation fails
    """
    try:
        supabase = get_supabase_client()
        response = (
            supabase.table(table_name)
            .insert(data)
            .execute()
        )
        
        logger.info(f"Inserted record into {table_name}")
        return response.data[0] if response.data else {}
        
    except Exception as e:
        logger.error(f"Failed to insert into {table_name}: {e}")
        raise ValueError(f"Insert operation failed: {e}")


def insert_multiple_records(table_name: str, data_list: List[Dict[str, Any]]) -> List[Dict]:
    """
    Insert multiple records into specified table.
    
    Args:
        table_name (str): Name of the table to insert into
        data_list (List[Dict[str, Any]]): List of records to insert
        
    Returns:
        List[Dict]: List of inserted records with generated fields
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If bulk insert operation fails
    """
    try:
        supabase = get_supabase_client()
        response = (
            supabase.table(table_name)
            .insert(data_list)
            .execute()
        )
        
        logger.info(f"Inserted {len(data_list)} records into {table_name}")
        return response.data or []
        
    except Exception as e:
        logger.error(f"Failed to bulk insert into {table_name}: {e}")
        raise ValueError(f"Bulk insert operation failed: {e}")