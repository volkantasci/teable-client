"""
Record management module.

This module handles record operations including creation, modification, and deletion.
"""

from typing import Any, Dict, List, Optional, Union

from ..models.record import Record, RecordBatch, RecordStatus
from .http import TeableHttpClient

class RecordManager:
    """
    Handles record operations.
    
    This class manages:
    - Record creation and deletion
    - Record updates
    - Batch operations
    - Record history
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the record manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def get_records(
        self,
        table_id: str,
        projection: Optional[List[str]] = None,
        cell_format: str = 'json',
        field_key_type: str = 'name',
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        group_by: Optional[str] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get records from a table.
        
        Args:
            table_id: ID of the table
            projection: Optional list of fields to return
            cell_format: Response format ('json' or 'text')
            field_key_type: Key type for fields ('id' or 'name')
            view_id: Optional view ID to filter by
            ignore_view_query: Whether to ignore view's filter/sort
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            filter_link_cell_candidate: Filter by link cell candidates
            filter_link_cell_selected: Filter by link cell selection
            selected_record_ids: Filter by specific record IDs
            order_by: Sort specification
            group_by: Group specification
            collapsed_group_ids: List of collapsed group IDs
            take: Number of records to take (max 2000)
            skip: Number of records to skip
            
        Returns:
            List[Dict[str, Any]]: List of record data
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        if projection:
            params['projection'] = projection
        if cell_format:
            params['cellFormat'] = cell_format
        if field_key_type:
            params['fieldKeyType'] = field_key_type
        if view_id:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql:
            params['filterByTql'] = filter_by_tql
        if filter:
            params['filter'] = filter
        if search:
            params['search'] = search
        if filter_link_cell_candidate:
            params['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected:
            params['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids:
            params['selectedRecordIds'] = selected_record_ids
        if order_by:
            params['orderBy'] = order_by
        if group_by:
            params['groupBy'] = group_by
        if collapsed_group_ids:
            params['collapsedGroupIds'] = collapsed_group_ids
        if take is not None:
            params['take'] = take
        if skip is not None:
            params['skip'] = skip
            
        response = self._http.request(
            'GET',
            f"table/{table_id}/record",
            params=params
        )
        return response['records']
        
    def get_record(
        self,
        table_id: str,
        record_id: str,
        projection: Optional[List[str]] = None,
        cell_format: str = 'json',
        field_key_type: str = 'name'
    ) -> Dict[str, Any]:
        """
        Get a single record by ID.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            projection: Optional list of fields to return
            cell_format: Response format ('json' or 'text')
            field_key_type: Key type for fields ('id' or 'name')
            
        Returns:
            Dict[str, Any]: Record data
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        if projection:
            params['projection'] = projection
        if cell_format:
            params['cellFormat'] = cell_format
        if field_key_type:
            params['fieldKeyType'] = field_key_type
            
        return self._http.request(
            'GET',
            f"table/{table_id}/record/{record_id}",
            params=params
        )
        
    def create_record(
        self,
        table_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new record.
        
        Args:
            table_id: ID of the table
            fields: Field values for the record
            
        Returns:
            Dict[str, Any]: Created record data
            
        Raises:
            APIError: If the creation fails
        """
        response = self._http.request(
            'POST',
            f"table/{table_id}/record",
            json={'records': [{'fields': fields}]}
        )
        return response['records'][0]
        
    def update_record(
        self,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any],
        field_key_type: str = 'name',
        typecast: bool = False,
        order: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            fields: New field values
            field_key_type: Key type for fields ('id' or 'name')
            typecast: Enable automatic type conversion
            order: Optional record ordering configuration
            
        Returns:
            Dict[str, Any]: Updated record data
            
        Raises:
            APIError: If the update fails
        """
        data: Dict[str, Any] = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'record': {'fields': fields}
        }
        
        if order:
            data['order'] = order
            
        return self._http.request(
            'PATCH',
            f"table/{table_id}/record/{record_id}",
            json=data
        )
        
    def delete_record(
        self,
        table_id: str,
        record_id: str
    ) -> bool:
        """
        Delete a record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            
        Returns:
            bool: True if successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"table/{table_id}/record/{record_id}"
        )
        return True
        
    def batch_create_records(
        self,
        table_id: str,
        records: List[Dict[str, Any]],
        field_key_type: str = 'name',
        typecast: bool = False,
        order: Optional[Dict[str, Any]] = None
    ) -> RecordBatch:
        """
        Create multiple records in a batch.
        
        Args:
            table_id: ID of the table
            records: List of record field values
            field_key_type: Key type for fields
            typecast: Enable automatic type conversion
            order: Optional record ordering configuration
            
        Returns:
            RecordBatch: Batch operation results
            
        Raises:
            APIError: If the creation fails
        """
        data: Dict[str, Any] = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'records': [{'fields': r} for r in records]
        }
        
        if order:
            data['order'] = order
        
        response = self._http.request(
            'POST',
            f"table/{table_id}/record",
            json=data
        )
        
        return RecordBatch.from_api_response(response, len(records))
        
    def batch_update_records(
        self,
        table_id: str,
        updates: List[Dict[str, Any]],
        field_key_type: str = 'name',
        typecast: bool = False,
        order: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Update multiple records in a batch.
        
        Args:
            table_id: ID of the table
            updates: List of record updates
            field_key_type: Key type for fields
            typecast: Enable automatic type conversion
            order: Optional record ordering configuration
            
        Returns:
            List[Dict[str, Any]]: Updated records data
            
        Raises:
            APIError: If the update fails
        """
        data: Dict[str, Any] = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'records': updates
        }
        
        if order:
            data['order'] = order
            
        return self._http.request(
            'PATCH',
            f"table/{table_id}/record",
            json=data
        )
        
    def batch_delete_records(
        self,
        table_id: str,
        record_ids: List[str]
    ) -> bool:
        """
        Delete multiple records in a batch.
        
        Args:
            table_id: ID of the table
            record_ids: List of record IDs
            
        Returns:
            bool: True if successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"table/{table_id}/record",
            params={'recordIds': record_ids}
        )
        return True
        
    def get_record_status(
        self,
        table_id: str,
        record_id: str,
        projection: Optional[List[str]] = None,
        cell_format: str = 'json',
        field_key_type: str = 'name',
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        group_by: Optional[str] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None
    ) -> RecordStatus:
        """
        Get visibility and deletion status of a record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            projection: Optional list of fields to return
            cell_format: Response format ('json' or 'text')
            field_key_type: Key type for fields ('id' or 'name')
            view_id: Optional view ID to filter by
            ignore_view_query: Whether to ignore view's filter/sort
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            filter_link_cell_candidate: Filter by link cell candidates
            filter_link_cell_selected: Filter by link cell selection
            selected_record_ids: Filter by specific record IDs
            order_by: Sort specification
            group_by: Group specification
            collapsed_group_ids: List of collapsed group IDs
            take: Number of records to take (max 2000)
            skip: Number of records to skip
            
        Returns:
            RecordStatus: Record status information
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        if projection:
            params['projection'] = projection
        if cell_format:
            params['cellFormat'] = cell_format
        if field_key_type:
            params['fieldKeyType'] = field_key_type
        if view_id:
            params['viewId'] = view_id
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql:
            params['filterByTql'] = filter_by_tql
        if filter:
            params['filter'] = filter
        if search:
            params['search'] = search
        if filter_link_cell_candidate:
            params['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected:
            params['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids:
            params['selectedRecordIds'] = selected_record_ids
        if order_by:
            params['orderBy'] = order_by
        if group_by:
            params['groupBy'] = group_by
        if collapsed_group_ids:
            params['collapsedGroupIds'] = collapsed_group_ids
        if take is not None:
            params['take'] = take
        if skip is not None:
            params['skip'] = skip
            
        response = self._http.request(
            'GET',
            f"table/{table_id}/record/{record_id}/status",
            params=params
        )
        return RecordStatus.from_api_response(response)
