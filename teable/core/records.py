"""
Record management module.

This module handles record operations including creation, modification, and deletion.
"""

import json
import mimetypes
from typing import Any, Dict, List, Literal, Optional, Union

from ..exceptions import ValidationError
from ..models.record import Record, RecordBatch, RecordStatus
from ..models.history import HistoryResponse
from .http import TeableHttpClient

def _validate_table_id(table_id: str) -> None:
    """Validate table ID."""
    if not isinstance(table_id, str) or not table_id:
        raise ValidationError("Table ID must be a non-empty string")

def _validate_record_id(record_id: str) -> None:
    """Validate record ID."""
    if not isinstance(record_id, str) or not record_id:
        raise ValidationError("Record ID must be a non-empty string")

def _validate_field_values(fields: Dict[str, Any]) -> None:
    """Validate field values dictionary."""
    if not isinstance(fields, dict):
        raise ValidationError("Fields must be a dictionary")
    if not fields:
        raise ValidationError("Fields dictionary cannot be empty")

def _validate_batch_records(records: List[Dict[str, Any]]) -> None:
    """Validate batch records list."""
    if not isinstance(records, list):
        raise ValidationError("Records must be a list")
    if not records:
        raise ValidationError("Records list cannot be empty")
    if len(records) > 2000:
        raise ValidationError("Cannot process more than 2000 records at once")
    for record in records:
        _validate_field_values(record)

def _validate_field_key_type(field_key_type: str) -> None:
    """Validate field key type."""
    if field_key_type not in ('id', 'name'):
        raise ValidationError("field_key_type must be 'id' or 'name'")

RecordPosition = Literal['before', 'after']

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
            ValidationError: If input validation fails
            APIError: If the request fails
        """
        _validate_table_id(table_id)
        _validate_field_key_type(field_key_type)
        
        if take is not None and take > 1000:
            raise ValidationError("Cannot take more than 1000 records at once")
            
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
            # Ensure search is a list
            if not isinstance(search, list):
                raise ValidationError("Search must be a list")
            
            # Handle empty search list
            if not search:
                params['search'] = []
            else:
                # Convert search items to array format
                search_array = []
                for item in search:
                    if isinstance(item, dict):
                        # Convert dict format to array format
                        if not all(k in item for k in ('value', 'field', 'exact')):
                            raise ValidationError("Search dict must contain 'value', 'field', and 'exact' keys")
                        search_array.append([
                            str(item['value']),
                            str(item['field']),
                            str(item['exact']).lower()
                        ])
                    elif isinstance(item, list):
                        # Already in array format
                        if len(item) != 3:
                            raise ValidationError("Search array items must contain exactly 3 elements")
                        search_array.append([
                            str(item[0]),
                            str(item[1]),
                            str(item[2]).lower()
                        ])
                    else:
                        raise ValidationError("Search items must be either dict or array format")
                params['search'] = search_array
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
            f"/table/{table_id}/record",
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
            ValidationError: If input validation fails
            APIError: If the request fails
        """
        _validate_table_id(table_id)
        _validate_record_id(record_id)
        _validate_field_key_type(field_key_type)
        
        params: Dict[str, Any] = {}
        if projection:
            params['projection'] = projection
        if cell_format:
            params['cellFormat'] = cell_format
        if field_key_type:
            params['fieldKeyType'] = field_key_type
            
        return self._http.request(
            'GET',
            f"/table/{table_id}/record/{record_id}",
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
            ValidationError: If input validation fails
            APIError: If the creation fails
        """
        _validate_table_id(table_id)
        _validate_field_values(fields)
        
        response = self._http.request(
            'POST',
            f"/table/{table_id}/record",
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
            ValidationError: If input validation fails
            APIError: If the update fails
        """
        _validate_table_id(table_id)
        _validate_record_id(record_id)
        _validate_field_values(fields)
        _validate_field_key_type(field_key_type)
        
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
            ValidationError: If input validation fails
            APIError: If the deletion fails
        """
        _validate_table_id(table_id)
        _validate_record_id(record_id)
        
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
            field_key_type: Key type for fields ('id' or 'name')
            typecast: Enable automatic type conversion
            order: Optional record ordering configuration
            
        Returns:
            RecordBatch: Batch operation results
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the creation fails
        """
        _validate_table_id(table_id)
        _validate_batch_records(records)
        _validate_field_key_type(field_key_type)
        
        data: Dict[str, Any] = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'records': [{'fields': r} for r in records]
        }
        
        if order:
            data['order'] = order
        
        response = self._http.request(
            'POST',
            f"/table/{table_id}/record",
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
            field_key_type: Key type for fields ('id' or 'name')
            typecast: Enable automatic type conversion
            order: Optional record ordering configuration
            
        Returns:
            List[Dict[str, Any]]: Updated records data
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the update fails
        """
        _validate_table_id(table_id)
        _validate_batch_records(updates)
        _validate_field_key_type(field_key_type)
        
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
            ValidationError: If input validation fails
            APIError: If the deletion fails
        """
        _validate_table_id(table_id)
        if not isinstance(record_ids, list):
            raise ValidationError("record_ids must be a list")
        if not record_ids:
            raise ValidationError("record_ids list cannot be empty")
        for record_id in record_ids:
            _validate_record_id(record_id)
            
        self._http.request(
            'DELETE',
            f"/table/{table_id}/record",
            params={'recordIds[]': record_ids}
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
            ValidationError: If input validation fails
            APIError: If the request fails
        """
        _validate_table_id(table_id)
        _validate_record_id(record_id)
        _validate_field_key_type(field_key_type)
        
        if take is not None and take > 2000:
            raise ValidationError("Cannot take more than 2000 records at once")
            
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
            f"/table/{table_id}/record/{record_id}/status",
            params=params
        )
        return RecordStatus.from_api_response(response)
        
    def get_record_history(
        self,
        table_id: str,
        record_id: str
    ) -> HistoryResponse:
        """
        Get the history list for a specific record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            
        Returns:
            HistoryResponse: History entries and user information
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the request fails
        """
        _validate_table_id(table_id)
        _validate_record_id(record_id)
        
        response = self._http.request(
            'GET',
            f"/table/{table_id}/record/{record_id}/history"
        )
        return HistoryResponse.from_api_response(response)
        
    def get_table_record_history(
        self,
        table_id: str
    ) -> HistoryResponse:
        """
        Get the history list for all records in a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            HistoryResponse: History entries and user information
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the request fails
        """
        _validate_table_id(table_id)
        
        response = self._http.request(
            'GET',
            f"/table/{table_id}/record/history"
        )
        return HistoryResponse.from_api_response(response)
        
    def upload_attachment(
        self,
        table_id: str,
        record_id: str,
        field_id: str,
        file: Optional[bytes] = None,
        file_url: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload an attachment to a record field.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            field_id: ID of the attachment field
            file: Optional file data to upload
            file_url: Optional URL to file
            mime_type: Optional MIME type for file (default: auto-detect)
            
        Returns:
            Dict[str, Any]: Updated record data
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the upload fails
        """
        _validate_table_id(table_id)
        _validate_record_id(record_id)
        
        if not isinstance(field_id, str) or not field_id:
            raise ValidationError("Field ID must be a non-empty string")
            
        if not file and not file_url:
            raise ValidationError("Either file or file_url must be provided")
            
        data: Dict[str, Any] = {}
        files = None
        
        if file:
            if not isinstance(file, bytes):
                raise ValidationError("File must be provided as bytes")
                
            # Determine MIME type if not provided
            if not mime_type:
                mime_type = 'application/octet-stream'
                
            files = {
                'file': ('attachment', file, mime_type)
            }
            
        if file_url:
            if not isinstance(file_url, str):
                raise ValidationError("File URL must be a string")
            if not file_url.startswith(('http://', 'https://')):
                raise ValidationError("File URL must be an HTTP(S) URL")
                
            data['fileUrl'] = file_url
            
        return self._http.request(
            'POST',
            f"/table/{table_id}/record/{record_id}/{field_id}/uploadAttachment",
            data=data,
            files=files
        )
        
    def duplicate_record(
        self,
        table_id: str,
        record_id: str,
        *,
        view_id: str,
        anchor_id: str,
        position: RecordPosition
    ) -> RecordBatch:
        """
        Duplicate an existing record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record to duplicate
            view_id: ID of the view for record positioning
            anchor_id: ID of the record to anchor to
            position: Position relative to anchor ('before' or 'after')
            
        Returns:
            RecordBatch: Batch operation results including the duplicated record
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the duplication fails
        """
        _validate_table_id(table_id)
        _validate_record_id(record_id)
        
        if not isinstance(view_id, str) or not view_id:
            raise ValidationError("View ID must be a non-empty string")
            
        if not isinstance(anchor_id, str) or not anchor_id:
            raise ValidationError("Anchor ID must be a non-empty string")
            
        if position not in ('before', 'after'):
            raise ValidationError("Position must be 'before' or 'after'")
            
        data = {
            'viewId': view_id,
            'anchorId': anchor_id,
            'position': position
        }
        
        response = self._http.request(
            'POST',
            f"/table/{table_id}/record/{record_id}",
            json=data
        )
        
        return RecordBatch.from_api_response(response, 1)
