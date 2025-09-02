"""
Supabase UPSERT operations for insert-or-update functionality.

Single responsibility: Handle all database UPSERT queries.
"""

import logging
from typing import Dict, List, Any, Optional
from src.database.client.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def upsert_single_record(table_name: str, data: Dict[str, Any], 
                        on_conflict: Optional[str] = None) -> Dict:
    """
    Upsert a single record (insert or update if exists).
    
    Args:
        table_name (str): Name of the table to upsert into
        data (Dict[str, Any]): Record data to upsert
        on_conflict (Optional[str]): Column(s) for conflict resolution
        
    Returns:
        Dict: Upserted record data
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If upsert operation fails
    """
    try:
        supabase = get_supabase_client()
        query = supabase.table(table_name).upsert(data)
        
        if on_conflict:
            query = query.on_conflict(on_conflict)
            
        response = query.execute()
        
        logger.info(f"Upserted record in {table_name}")
        return response.data[0] if response.data else {}
        
    except Exception as e:
        logger.error(f"Failed to upsert into {table_name}: {e}")
        raise ValueError(f"Upsert operation failed: {e}")


def upsert_multiple_records(table_name: str, data_list: List[Dict[str, Any]], 
                           on_conflict: Optional[str] = None) -> List[Dict]:
    """
    Upsert multiple records (bulk insert or update if exists).
    
    Args:
        table_name (str): Name of the table to upsert into
        data_list (List[Dict[str, Any]]): List of records to upsert
        on_conflict (Optional[str]): Column(s) for conflict resolution
        
    Returns:
        List[Dict]: List of upserted records
        
    Raises:
        ConnectionError: If database connection fails
        ValueError: If bulk upsert operation fails
    """
    try:
        supabase = get_supabase_client()
        query = supabase.table(table_name).upsert(data_list)
        
        if on_conflict:
            query = query.on_conflict(on_conflict)
            
        response = query.execute()
        
        logger.info(f"Upserted {len(data_list)} records in {table_name}")
        return response.data or []
        
    except Exception as e:
        logger.error(f"Failed to bulk upsert into {table_name}: {e}")
        raise ValueError(f"Bulk upsert operation failed: {e}")