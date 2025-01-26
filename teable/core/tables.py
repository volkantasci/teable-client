"""
Table management module.

This module handles table operations including creation, modification, and deletion.
"""

from typing import Any, Dict, List, Optional, Union
import json

from ..models.table import Table, Field, View, Record
from ..models.record import Record, RecordBatch
from ..models.trash import ResourceType
from .http import TeableHttpClient
from .cache import ResourceCache

class TableManager:
    """
    Handles table operations.
    
    This class manages:
    - Table creation and deletion
    - Table metadata updates
    - Table caching
    - Table permissions
    - Record operations
    """
    
    def __init__(self, http_client: TeableHttpClient, cache: ResourceCache[Table]):
        """
        Initialize the table manager.
        
        Args:
            http_client: HTTP client for API communication
            cache: Resource cache for tables
        """
        self._http = http_client
        self._cache = cache
        self._cache.add_resource_type('tables')
        
    def get_table(self, table_id: str, base_id: Optional[str] = None) -> Table:
        """
        Get a table by ID.
        
        Args:
            table_id: ID of the table
            base_id: Optional base ID (if not provided, uses table endpoint)
            
        Returns:
            Table: The requested table
            
        Raises:
            APIError: If the request fails
        """
        cached = self._cache.get('tables', table_id)
        if cached:
            return cached
            
        if base_id:
            response = self._http.request('GET', f"/base/{base_id}/table/{table_id}")
        else:
            response = self._http.request('GET', f"/table/{table_id}")
            
        table = Table.from_api_response(response, self)
        self._cache.set('tables', table_id, table)
        return table
        
    def get_tables(self) -> List[Table]:
        """
        Get all accessible tables.
        
        Returns:
            List[Table]: List of tables
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', "/table")
        tables = [Table.from_api_response(t, self) for t in response]
        
        # Update cache
        for table in tables:
            self._cache.set('tables', table.table_id, table)
            
        return tables

    def get_table_fields(self, table_id: str) -> List[Field]:
        """
        Get all fields in a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[Field]: List of fields
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', f"/table/{table_id}/field")
        return [Field.from_api_response(f) for f in response]

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
        skip: Optional[int] = None,
        **kwargs: Any
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
        params = {}
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
            params['search'] = search  # search parametresini doğrudan array olarak gönder
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
            
        # search parametresini json string'e çevir
        if search:
            params['search'] = json.dumps(search)

        response = self._http.request(
            'GET',
            f"/table/{table_id}/record",
            params=params
        )
        return response['records']

    def get_table_views(self, table_id: str) -> List[View]:
        """
        Get all views in a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[View]: List of views
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', f"/table/{table_id}/view")
        return [View.from_api_response(v) for v in response]

    def create_record(self, table_id: str, fields: Dict[str, Any]) -> Record:
        """
        Create a new record in a table.
        
        Args:
            table_id: ID of the table
            fields: Field values for the record
            
        Returns:
            Record: The created record
            
        Raises:
            APIError: If the creation fails
        """
        response = self._http.request(
            'POST',
            f"/table/{table_id}/record",
            json={'records': [{'fields': fields}]}
        )
        return Record.from_api_response(response['records'][0])

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
            RecordBatch: Results of the batch operation
            
        Raises:
            APIError: If the creation fails
        """
        data = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'records': records
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
    ) -> List[Record]:
        """
        Update multiple records in a batch.
        
        Args:
            table_id: ID of the table
            updates: List of record updates with IDs and new field values
            field_key_type: Key type for fields ('id' or 'name')
            typecast: Enable automatic type conversion
            order: Optional record ordering configuration
            
        Returns:
            List[Record]: Updated records
            
        Raises:
            APIError: If the update fails
        """
        data = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'records': updates
        }
        if order:
            data['order'] = order
            
        response = self._http.request(
            'PATCH',
            f"/table/{table_id}/record",
            json=data
        )
        return [Record.from_api_response(r) for r in response]

    def batch_delete_records(
        self,
        table_id: str,
        record_ids: List[str]
    ) -> bool:
        """
        Delete multiple records in a batch.
        
        Args:
            table_id: ID of the table
            record_ids: List of record IDs to delete
            
        Returns:
            bool: True if all deletions successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/table/{table_id}/record",
            params={'recordIds': json.dumps(record_ids)}  # recordIds'i json string olarak gönder
        )
        return True
        
    def create_table(
        self,
        base_id: str,
        name: str,
        db_table_name: str,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        fields: Optional[List[Dict[str, Any]]] = None,
        views: Optional[List[Dict[str, Any]]] = None,
        records: Optional[List[Dict[str, Any]]] = None,
        order: Optional[int] = None,
        field_key_type: str = 'name'
    ) -> Table:
        """
        Create a new table in a base.
        
        Args:
            base_id: ID of the base to create the table in
            name: Display name for the table
            db_table_name: Table name in backend database (1-63 chars, start with letter, alphanumeric + underscore)
            description: Optional description
            icon: Optional emoji icon
            fields: Optional list of field configurations
            views: Optional list of view configurations
            records: Optional list of initial records
            order: Optional order position
            field_key_type: Key type for fields ('id' or 'name')
            
        Returns:
            Table: The created table
            
        Raises:
            APIError: If the creation fails
            ValueError: If db_table_name is invalid
        """
        if not db_table_name[0].isalpha() or not db_table_name.isalnum():
            raise ValueError(
                "db_table_name must start with letter and contain only letters, numbers and underscore"
            )
        if len(db_table_name) > 63:
            raise ValueError("db_table_name must be 1-63 characters")
            
        data: Dict[str, Union[str, int, List[Dict[str, Any]], Optional[str]]] = {
            'name': name,
            'dbTableName': db_table_name,
            'fieldKeyType': field_key_type
        }
        if description is not None:
            data['description'] = description
        if icon is not None:
            data['icon'] = icon
        if fields is not None:
            data['fields'] = fields
        if views is not None:
            data['views'] = views
        if records is not None:
            data['records'] = records
        if order is not None:
            data['order'] = order
            
        response = self._http.request(
            'POST',
            f"/base/{base_id}/table/",
            json=data
        )
        table = Table.from_api_response(response, self)
        self._cache.set('tables', table.table_id, table)
        return table
        
    def delete_table(self, base_id: str, table_id: str) -> bool:
        """
        Delete a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/base/{base_id}/table/{table_id}"
        )
        self._cache.delete('tables', table_id)
        return True
        
    def permanent_delete_table(self, base_id: str, table_id: str) -> bool:
        """
        Permanently delete a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/base/{base_id}/table/{table_id}/permanent"
        )
        self._cache.delete('tables', table_id)
        return True
        
    def update_table_name(self, base_id: str, table_id: str, name: str) -> bool:
        """
        Update name of a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            name: New name for the table
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"/base/{base_id}/table/{table_id}/name",
            json={'name': name}
        )
        # Invalidate cache since table was modified
        self._cache.delete('tables', table_id)
        return True
        
    def update_table_icon(self, base_id: str, table_id: str, icon: str) -> bool:
        """
        Update icon of a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            icon: New icon for the table (emoji string)
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"/base/{base_id}/table/{table_id}/icon",
            json={'icon': icon}
        )
        # Invalidate cache since table was modified
        self._cache.delete('tables', table_id)
        return True
        
    def update_table_order(
        self,
        base_id: str,
        table_id: str,
        anchor_id: str,
        position: str
    ) -> bool:
        """
        Update order of a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            anchor_id: ID of the anchor table to position relative to
            position: Position relative to anchor ('before' or 'after')
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
            ValueError: If position is not 'before' or 'after'
        """
        if position not in ['before', 'after']:
            raise ValueError("Position must be 'before' or 'after'")
            
        self._http.request(
            'PUT',
            f"/base/{base_id}/table/{table_id}/order",
            json={
                'anchorId': anchor_id,
                'position': position
            }
        )
        # Invalidate cache since table order changed
        self._cache.clear_type('tables')
        return True
        
    def update_table_description(
        self,
        base_id: str,
        table_id: str,
        description: Optional[str]
    ) -> bool:
        """
        Update description of a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            description: New description for the table (can be None)
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PUT',
            f"/base/{base_id}/table/{table_id}/description",
            json={'description': description}
        )
        # Invalidate cache since table was modified
        self._cache.delete('tables', table_id)
        return True
        
    def update_table_db_name(
        self,
        base_id: str,
        table_id: str,
        db_table_name: str
    ) -> bool:
        """
        Update database table name of a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            db_table_name: New database table name (1-63 chars, start with letter or underscore, alphanumeric + underscore)
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
            ValueError: If db_table_name is invalid
        """
        if not (db_table_name[0].isalpha() or db_table_name[0] == '_') or not db_table_name.replace('_', '').isalnum():
            raise ValueError(
                "db_table_name must start with letter or underscore and contain only letters, numbers and underscore"
            )
        if len(db_table_name) > 63:
            raise ValueError("db_table_name must be 1-63 characters")
            
        self._http.request(
            'PUT',
            f"/base/{base_id}/table/{table_id}/db-table-name",
            json={'dbTableName': db_table_name}
        )
        # Invalidate cache since table was modified
        self._cache.delete('tables', table_id)
        return True
        
    def get_table_permission(self, base_id: str, table_id: str) -> Dict[str, Any]:
        """
        Get permissions for a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            
        Returns:
            Dict[str, Any]: Permission information containing:
                - table: Table-level permissions
                - view: View-level permissions
                - record: Record-level permissions
                - field: Field-level permissions including:
                    - fields: Per-field permissions
                    - create: Permission to create new fields
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/base/{base_id}/table/{table_id}/permission"
        )
        
    def get_table_default_view_id(self, base_id: str, table_id: str) -> str:
        """
        Get default view ID of a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            
        Returns:
            str: Default view ID
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request(
            'GET',
            f"/base/{base_id}/table/{table_id}/default-view-id"
        )
        return response['id']
