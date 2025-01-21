"""
Core Client Module

This module provides the main TeableClient class that handles
API communication and serves as the primary interface for the library.
"""

import time
from typing import Any, Dict, List, Optional, Union, Literal
import requests

from ..exceptions import (
    APIError,
    AuthenticationError,
    BatchOperationError,
    ConfigurationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError
)
from ..models.config import TeableConfig
from ..models.user import User
from ..models.base import Base
from ..models.field import Field
from ..models.record import Record, RecordBatch, RecordStatus
from ..models.space import Space
from ..models.table import Table
from ..models.trash import ResourceType, TrashResponse
from ..models.view import View
from ..models.history import HistoryResponse
from ..models.plugin import PluginInstallation
from ..models.dashboard import Dashboard, DashboardLayout, DashboardPlugin
from ..models.aggregation import (
    Aggregation,
    GroupPoint,
    CalendarDailyCollection,
    SearchIndex
)
from ..models.permission import TablePermission
from ..models.selection import SelectionRange


class TeableClient:
    """
    Main client class for interacting with the Teable API.
    
    This class handles:
    - API authentication and configuration
    - HTTP request management
    - Rate limiting and retries
    - Resource caching
    - High-level operations on tables, records, fields, and views
    
    Attributes:
        config (TeableConfig): Client configuration
    """
    
    def __init__(self, config: Union[TeableConfig, Dict[str, Any]]):
        """
        Initialize the client with configuration.
        
        Args:
            config: Configuration instance or dictionary
        """
        if isinstance(config, dict):
            self.config = TeableConfig.from_dict(config)
        else:
            self.config = config
            
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Rate limiting state
        self._rate_limit_remaining = 100
        self._rate_limit_reset = 0
        
        # Cache for resources
        self._cache = {
            'tables': {},
            'fields': {},
            'views': {}
        }

    def _check_rate_limit(self) -> None:
        """
        Check and enforce rate limits.
        
        Raises:
            RateLimitError: If rate limit exceeded
        """
        if self._rate_limit_remaining <= 0:
            reset_time = self._rate_limit_reset - time.time()
            if reset_time > 0:
                if self.config.retry_delay is not None:
                    time.sleep(min(reset_time, self.config.retry_delay))
                else:
                    raise RateLimitError(
                        "Rate limit exceeded",
                        reset_time=self._rate_limit_reset
                    )

    def _update_rate_limits(self, headers: Any) -> None:
        """
        Update rate limit tracking from response headers.
        
        Args:
            headers: Response headers (CaseInsensitiveDict from requests)
        """
        if 'X-RateLimit-Remaining' in headers:
            self._rate_limit_remaining = int(headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in headers:
            self._rate_limit_reset = int(headers['X-RateLimit-Reset'])

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Any:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data
            
        Raises:
            Various exceptions based on response
        """
        self._check_rate_limit()
        
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        retries = 0
        
        while True:
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.config.timeout,
                    **kwargs
                )
                self._update_rate_limits(response.headers)
                
                if response.status_code == 429:  # Rate limit exceeded
                    if (self.config.max_retries is not None and
                        retries < self.config.max_retries):
                        retries += 1
                        time.sleep(self.config.retry_delay or 1)
                        continue
                    else:
                        raise RateLimitError(
                            "Rate limit exceeded",
                            response.status_code,
                            reset_time=float(response.headers.get('X-RateLimit-Reset', 0))
                        )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError(
                        "Authentication failed",
                        e.response.status_code
                    )
                elif e.response.status_code == 404:
                    raise ResourceNotFoundError(
                        "Resource not found",
                        endpoint,
                        str(kwargs.get('params', {})),
                        e.response.status_code
                    )
                else:
                    raise APIError(
                        f"HTTP {e.response.status_code}: {e.response.text}",
                        e.response.status_code,
                        e.response.text
                    )
            except requests.exceptions.RequestException as e:
                raise NetworkError(f"Request failed: {str(e)}")

    def get_table(self, table_id: str) -> Table:
        """
        Get a table by ID.
        
        Args:
            table_id: ID of the table
            
        Returns:
            Table: The requested table
        """
        if table_id in self._cache['tables']:
            return self._cache['tables'][table_id]
            
        response = self._make_request('GET', f"table/{table_id}")
        table = Table.from_api_response(response, self)
        self._cache['tables'][table_id] = table
        return table

    def get_tables(self) -> List[Table]:
        """
        Get all accessible tables.
        
        Returns:
            List[Table]: List of tables
        """
        response = self._make_request('GET', "table")
        tables = [Table.from_api_response(t, self) for t in response]
        
        # Update cache
        for table in tables:
            self._cache['tables'][table.table_id] = table
            
        return tables

    def get_table_fields(self, table_id: str) -> List[Field]:
        """
        Get all fields for a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[Field]: List of fields
        """
        cache_key = f"{table_id}_fields"
        if cache_key in self._cache['fields']:
            return self._cache['fields'][cache_key]
            
        response = self._make_request('GET', f"table/{table_id}/field")
        fields = [Field.from_api_response(f) for f in response]
        self._cache['fields'][cache_key] = fields
        return fields

    def get_table_views(self, table_id: str) -> List[View]:
        """
        Get all views for a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[View]: List of views
        """
        cache_key = f"{table_id}_views"
        if cache_key in self._cache['views']:
            return self._cache['views'][cache_key]
            
        response = self._make_request('GET', f"table/{table_id}/view")
        views = [View.from_api_response(v, self) for v in response]
        self._cache['views'][cache_key] = views
        return views

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
            List[Dict]: List of record data
        """
        params: Dict[str, Union[str, int, bool, Dict[str, Any], List[Any]]] = {}
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
            
        response = self._make_request(
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
            Dict: Record data
        """
        params = {}
        if projection:
            params['projection'] = projection
        if cell_format:
            params['cellFormat'] = cell_format
        if field_key_type:
            params['fieldKeyType'] = field_key_type
            
        return self._make_request(
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
            Dict: Created record data
        """
        response = self._make_request(
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
            Dict: Updated record data
        """
        data = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'record': {'fields': fields}
        }
        
        if order:
            data['order'] = order
            
        return self._make_request(
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
        """
        self._make_request(
            'DELETE',
            f"table/{table_id}/record/{record_id}"
        )
        return True

    def duplicate_record(
        self,
        table_id: str,
        record_id: str,
        view_id: str,
        anchor_id: str,
        position: str
    ) -> Dict[str, Any]:
        """
        Duplicate an existing record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record to duplicate
            view_id: ID of the view for positioning
            anchor_id: ID of the anchor record
            position: Position relative to anchor ('before' or 'after')
            
        Returns:
            Dict: Created record data
        """
        data = {
            'viewId': view_id,
            'anchorId': anchor_id,
            'position': position
        }
        
        return self._make_request(
            'POST',
            f"table/{table_id}/record/{record_id}",
            json=data
        )

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
        """
        data = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'records': [{'fields': r} for r in records]
        }
        
        if order:
            data['order'] = order
        
        response = self._make_request(
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
            List[Dict]: Updated records data
        """
        data = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'records': updates
        }
        
        if order:
            data['order'] = order
            
        return self._make_request(
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
        """
        self._make_request(
            'DELETE',
            f"table/{table_id}/record",
            params={'recordIds': record_ids}
        )
        return True

    def get_spaces(self) -> List[Space]:
        """
        Get all accessible spaces.
        
        Returns:
            List[Space]: List of spaces
        """
        response = self._make_request('GET', "space")
        return [Space.from_api_response(s, self) for s in response]

    def get_space(self, space_id: str) -> Space:
        """
        Get a space by ID.
        
        Args:
            space_id: ID of the space to retrieve
            
        Returns:
            Space: The requested space
            
        Raises:
            ResourceNotFoundError: If space not found
        """
        response = self._make_request('GET', f"space/{space_id}")
        return Space.from_api_response(response, self)

    def create_space(self, name: str) -> Space:
        """
        Create a new space.
        
        Args:
            name: Display name for the space
            
        Returns:
            Space: The created space
        """
        response = self._make_request(
            'POST',
            "space",
            json={'name': name}
        )
        return Space.from_api_response(response, self)

    def get_bases(self) -> List[Base]:
        """
        Get all accessible bases.
        
        Returns:
            List[Base]: List of bases
        """
        response = self._make_request('GET', "base/access/all")
        return [Base.from_api_response(b, self) for b in response]

    def get_shared_bases(self) -> List[Base]:
        """
        Get all shared bases.
        
        Returns:
            List[Base]: List of shared bases
        """
        response = self._make_request('GET', "base/shared-base")
        return [Base.from_api_response(b, self) for b in response]

    def get_base(self, base_id: str) -> Base:
        """
        Get a base by ID.
        
        Args:
            base_id: ID of the base to retrieve
            
        Returns:
            Base: The requested base
            
        Raises:
            ResourceNotFoundError: If base not found
        """
        response = self._make_request('GET', f"base/{base_id}")
        return Base.from_api_response(response, self)

    def create_base(
        self,
        space_id: str,
        name: Optional[str] = None,
        icon: Optional[str] = None
    ) -> Base:
        """
        Create a new base in a space.
        
        Args:
            space_id: ID of the space to create the base in
            name: Optional display name for the base
            icon: Optional icon for the base
            
        Returns:
            Base: The created base
        """
        data = {'spaceId': space_id}
        if name:
            data['name'] = name
        if icon:
            data['icon'] = icon
            
        response = self._make_request(
            'POST',
            "base",
            json=data
        )
        return Base.from_api_response(response, self)

    def duplicate_base(
        self,
        from_base_id: str,
        space_id: str,
        name: Optional[str] = None,
        with_records: bool = False
    ) -> Base:
        """
        Duplicate an existing base.
        
        Args:
            from_base_id: ID of the base to duplicate
            space_id: ID of the space to create the duplicate in
            name: Optional name for the duplicated base
            with_records: Whether to include records in the duplicate
            
        Returns:
            Base: The duplicated base
        """
        data = {
            'fromBaseId': from_base_id,
            'spaceId': space_id,
            'withRecords': with_records
        }
        if name:
            data['name'] = name
            
        response = self._make_request(
            'POST',
            "base/duplicate",
            json=data
        )
        return Base.from_api_response(response, self)

    def create_base_from_template(
        self,
        space_id: str,
        template_id: str,
        with_records: bool = False
    ) -> Base:
        """
        Create a new base from a template.
        
        Args:
            space_id: ID of the space to create the base in
            template_id: ID of the template to use
            with_records: Whether to include template records
            
        Returns:
            Base: The created base
        """
        response = self._make_request(
            'POST',
            "base/create-from-template",
            json={
                'spaceId': space_id,
                'templateId': template_id,
                'withRecords': with_records
            }
        )
        return Base.from_api_response(response, self)

    def clear_cache(self) -> None:
        """Clear all cached resources."""
        self._cache = {
            'tables': {},
            'fields': {},
            'views': {}
        }

    def get_trash_items(self, resource_type: ResourceType) -> TrashResponse:
        """
        Get items in trash for a specific resource type.
        
        Args:
            resource_type: Type of resources to list ('space' or 'base')
            
        Returns:
            TrashResponse: Trash listing response
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            'trash',
            params={'resourceType': resource_type.value}
        )
        return TrashResponse.from_api_response(response)

    def get_trash_items_for_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        cursor: Optional[str] = None
    ) -> TrashResponse:
        """
        Get trash items for a specific base or table.
        
        Args:
            resource_id: ID of the base or table
            resource_type: Type of resource ('base' or 'table')
            cursor: Optional cursor for pagination
            
        Returns:
            TrashResponse: Trash listing response
            
        Raises:
            APIError: If the request fails
        """
        params = {
            'resourceId': resource_id,
            'resourceType': resource_type.value
        }
        if cursor:
            params['cursor'] = cursor
            
        response = self._make_request(
            'GET',
            'trash/items',
            params=params
        )
        return TrashResponse.from_api_response(response)

    def reset_trash_items_for_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        cursor: Optional[str] = None
    ) -> bool:
        """
        Reset (permanently delete) trash items for a specific base or table.
        
        Args:
            resource_id: ID of the base or table
            resource_type: Type of resource ('base' or 'table')
            cursor: Optional cursor for pagination
            
        Returns:
            bool: True if reset successful
            
        Raises:
            APIError: If the reset fails
        """
        params = {
            'resourceId': resource_id,
            'resourceType': resource_type.value
        }
        if cursor:
            params['cursor'] = cursor
            
        self._make_request(
            'DELETE',
            'trash/reset-items',
            params=params
        )
        return True

    def restore_trash_item(self, trash_id: str) -> bool:
        """
        Restore an item from trash.
        
        Args:
            trash_id: ID of the trash item to restore
            
        Returns:
            bool: True if restoration successful
            
        Raises:
            APIError: If the restoration fails
        """
        self._make_request(
            'POST',
            f"trash/restore/{trash_id}"
        )
        return True

    def get_record_history(
        self,
        table_id: str,
        record_id: str
    ) -> HistoryResponse:
        """
        Get history of changes for a record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            
        Returns:
            HistoryResponse: Record history response
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"table/{table_id}/record/{record_id}/history"
        )
        return HistoryResponse.from_api_response(response)

    def get_table_record_history(
        self,
        table_id: str
    ) -> HistoryResponse:
        """
        Get history of changes for all records in a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            HistoryResponse: Record history response
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"table/{table_id}/record/history"
        )
        return HistoryResponse.from_api_response(response)

    def get_field(
        self,
        table_id: str,
        field_id: str
    ) -> Field:
        """
        Get a field by ID.
        
        Args:
            table_id: ID of the table
            field_id: ID of the field
            
        Returns:
            Field: The requested field
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"table/{table_id}/field/{field_id}"
        )
        return Field.from_api_response(response)

    def update_field(
        self,
        table_id: str,
        field_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        db_field_name: Optional[str] = None
    ) -> None:
        """
        Update a field's common properties.
        
        Args:
            table_id: ID of the table
            field_id: ID of the field
            name: Optional new name for the field
            description: Optional new description
            db_field_name: Optional new database field name
            
        Raises:
            APIError: If the update fails
        """
        data = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if db_field_name is not None:
            data['dbFieldName'] = db_field_name
            
        self._make_request(
            'PATCH',
            f"table/{table_id}/field/{field_id}",
            json=data
        )

    def delete_field(
        self,
        table_id: str,
        field_id: str
    ) -> bool:
        """
        Delete a field.
        
        Args:
            table_id: ID of the table
            field_id: ID of the field
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._make_request(
            'DELETE',
            f"table/{table_id}/field/{field_id}"
        )
        return True

    def convert_field(
        self,
        table_id: str,
        field_id: str,
        field_type: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        db_field_name: Optional[str] = None,
        is_lookup: Optional[bool] = None,
        lookup_options: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        not_null: Optional[bool] = None,
        unique: Optional[bool] = None
    ) -> Field:
        """
        Convert a field to a different type.
        
        Args:
            table_id: ID of the table
            field_id: ID of the field
            field_type: New type for the field
            name: Optional new name
            description: Optional new description
            db_field_name: Optional new database field name
            is_lookup: Whether field is a lookup field
            lookup_options: Optional lookup configuration
            options: Optional field type-specific options
            not_null: Whether field is not null
            unique: Whether field is unique
            
        Returns:
            Field: Updated field data
            
        Raises:
            APIError: If the conversion fails
        """
        data: Dict[str, Union[str, bool, Dict[str, Any]]] = {'type': field_type}
        
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if db_field_name is not None:
            data['dbFieldName'] = db_field_name
        if is_lookup is not None:
            data['isLookup'] = is_lookup
        if lookup_options is not None:
            data['lookupOptions'] = lookup_options
        if options is not None:
            data['options'] = options
        if not_null is not None:
            data['notNull'] = not_null
        if unique is not None:
            data['unique'] = unique
            
        response = self._make_request(
            'PUT',
            f"table/{table_id}/field/{field_id}/convert",
            json=data
        )
        return Field.from_api_response(response)

    def upload_attachment(
        self,
        table_id: str,
        record_id: str,
        field_id: str,
        file: Optional[bytes] = None,
        file_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload an attachment for a record field.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            field_id: ID of the attachment field
            file: Optional file data to upload
            file_url: Optional URL to file
            
        Returns:
            Dict[str, Any]: Updated record data
            
        Raises:
            APIError: If the upload fails
            ValueError: If neither file nor file_url is provided
        """
        if not file and not file_url:
            raise ValueError("Either file or file_url must be provided")
            
        data = {}
        if file:
            data['file'] = ('file', file, 'application/octet-stream')
        if file_url:
            data['fileUrl'] = (None, file_url)
            
        return self._make_request(
            'POST',
            f"table/{table_id}/record/{record_id}/{field_id}/uploadAttachment",
            files=data
        )

    def get_field_filter_link_records(
        self,
        table_id: str,
        field_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get associated records for a field filter configuration.
        
        Args:
            table_id: ID of the table
            field_id: ID of the field
            
        Returns:
            List[Dict[str, Any]]: List of associated records grouped by table
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"table/{table_id}/field/{field_id}/filter-link-records"
        )
        return response

    def create_view(
        self,
        table_id: str,
        view_type: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        order: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, Any]] = None,
        filter: Optional[Dict[str, Any]] = None,
        group: Optional[List[Dict[str, Any]]] = None,
        share_id: Optional[str] = None,
        enable_share: Optional[bool] = None,
        share_meta: Optional[Dict[str, Any]] = None,
        column_meta: Optional[Dict[str, Any]] = None,
        plugin_id: Optional[str] = None
    ) -> View:
        """
        Create a new view in a table.
        
        Args:
            table_id: ID of the table
            view_type: Type of view ('grid', 'calendar', 'kanban', 'form', 'gallery', 'gantt', 'plugin')
            name: Optional display name for the view
            description: Optional description
            order: Optional order position
            options: Optional view-specific options
            sort: Optional sort configuration
            filter: Optional filter configuration
            group: Optional group configuration
            share_id: Optional share ID
            enable_share: Optional enable sharing flag
            share_meta: Optional sharing metadata
            column_meta: Optional column metadata
            plugin_id: Optional plugin ID
            
        Returns:
            View: The created view
            
        Raises:
            APIError: If the creation fails
        """
        data: Dict[str, Union[str, int, bool, Dict[str, Any], List[Dict[str, Any]]]] = {'type': view_type}
        
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if order is not None:
            data['order'] = order
        if options is not None:
            data['options'] = options
        if sort is not None:
            data['sort'] = sort
        if filter is not None:
            data['filter'] = filter
        if group is not None:
            data['group'] = group
        if share_id is not None:
            data['shareId'] = share_id
        if enable_share is not None:
            data['enableShare'] = enable_share
        if share_meta is not None:
            data['shareMeta'] = share_meta
        if column_meta is not None:
            data['columnMeta'] = column_meta
        if plugin_id is not None:
            data['pluginId'] = plugin_id
            
        response = self._make_request(
            'POST',
            f"table/{table_id}/view",
            json=data
        )
        return View.from_api_response(response, self)

    def get_view(
        self,
        table_id: str,
        view_id: str
    ) -> View:
        """
        Get a view by ID.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            View: The requested view
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"table/{table_id}/view/{view_id}"
        )
        return View.from_api_response(response, self)

    def delete_view(
        self,
        table_id: str,
        view_id: str
    ) -> bool:
        """
        Delete a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._make_request(
            'DELETE',
            f"table/{table_id}/view/{view_id}"
        )
        return True

    def update_view_manual_sort(
        self,
        table_id: str,
        view_id: str,
        sort_objects: List[Dict[str, str]]
    ) -> bool:
        """
        Update manual sort configuration for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            sort_objects: List of sort configurations, each containing:
                - fieldId: ID of the field to sort by
                - order: Sort direction ('asc' or 'desc')
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PUT',
            f"table/{table_id}/view/{view_id}/manual-sort",
            json={'sortObjs': sort_objects}
        )
        return True

    def update_view_column_meta(
        self,
        table_id: str,
        view_id: str,
        column_meta_updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Update column metadata for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            column_meta_updates: List of column metadata updates, each containing:
                - fieldId: ID of the field
                - columnMeta: Column metadata configuration with properties like:
                    - order: Column order in view (number)
                    - width: Column width in view (number)
                    - hidden: Whether column is hidden (boolean)
                    - statisticFunc: Statistical function for column (string, optional)
                    - visible: Whether column is visible (boolean)
                    - required: Whether column is required (boolean)
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PUT',
            f"table/{table_id}/view/{view_id}/column-meta",
            json=column_meta_updates
        )
        return True

    def update_view_filter(
        self,
        table_id: str,
        view_id: str,
        filter_config: Dict[str, Any]
    ) -> bool:
        """
        Update filter configuration for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            filter_config: Filter configuration containing:
                - filterSet: List of filter conditions, each with:
                    - isSymbol: Whether condition uses symbols
                    - fieldId: ID of the field to filter
                    - value: Filter value
                    - operator: Filter operator (e.g., 'is', 'contains', etc.)
                - conjunction: How to combine conditions ('and' or 'or')
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PUT',
            f"table/{table_id}/view/{view_id}/filter",
            json={'filter': filter_config}
        )
        return True

    def update_view_sort(
        self,
        table_id: str,
        view_id: str,
        sort_objects: List[Dict[str, str]],
        manual_sort: Optional[bool] = None
    ) -> bool:
        """
        Update sort configuration for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            sort_objects: List of sort configurations, each containing:
                - fieldId: ID of the field to sort by
                - order: Sort direction ('asc' or 'desc')
            manual_sort: Optional flag for manual sorting
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        data: Dict[str, Union[List[Dict[str, str]], bool]] = {'sortObjs': sort_objects}
        if manual_sort is not None:
            data['manualSort'] = manual_sort
            
        self._make_request(
            'PUT',
            f"table/{table_id}/view/{view_id}/sort",
            json=data
        )
        return True

    def update_view_group(
        self,
        table_id: str,
        view_id: str,
        group_objects: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """
        Update group configuration for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            group_objects: Optional list of group configurations, each containing:
                - fieldId: ID of the field to group by
                - order: Sort direction within groups ('asc' or 'desc')
                If None, grouping will be removed
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PUT',
            f"table/{table_id}/view/{view_id}/group",
            json=group_objects
        )
        return True

    def update_view_options(
        self,
        table_id: str,
        view_id: str,
        options: Dict[str, Any]
    ) -> bool:
        """
        Update options for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            options: View options configuration, which can be one of:
                Grid view options:
                    - rowHeight: Row height level ('short', 'medium', 'tall', 'extraTall', 'autoFit')
                    - frozenColumnCount: Number of frozen columns
                Kanban view options:
                    - stackFieldId: Field ID for Kanban stacks
                    - coverFieldId: Attachment field ID for card covers
                    - isCoverFit: Whether to fit cover images to cards
                    - isFieldNameHidden: Whether to hide field names
                    - isEmptyStackHidden: Whether to hide empty stacks
                Gallery view options:
                    - coverFieldId: Attachment field ID for card covers
                    - isCoverFit: Whether to fit cover images to cards
                    - isFieldNameHidden: Whether to hide field names
                Calendar/Gantt view options:
                    - startDateFieldId: Field ID for start dates
                    - endDateFieldId: Field ID for end dates
                    - titleFieldId: Field ID for titles
                    - colorConfig: Color configuration
                Form view options:
                    - coverUrl: Form cover image URL
                    - logoUrl: Form logo URL
                    - submitLabel: Submit button text
                Plugin view options:
                    - pluginId: Plugin ID
                    - pluginInstallId: Plugin installation ID
                    - pluginLogo: Plugin logo URL
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PATCH',
            f"table/{table_id}/view/{view_id}/options",
            json={'options': options}
        )
        return True

    def update_view_record_order(
        self,
        table_id: str,
        view_id: str,
        anchor_id: str,
        position: str,
        record_ids: List[str]
    ) -> bool:
        """
        Update record order in a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            anchor_id: ID of the record to move other records around
            position: Position relative to anchor ('before' or 'after')
            record_ids: List of record IDs to move (max 1000)
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
            ValueError: If record_ids exceeds 1000 items
        """
        if len(record_ids) > 1000:
            raise ValueError("Cannot move more than 1000 records at once")
            
        self._make_request(
            'PUT',
            f"table/{table_id}/view/{view_id}/record-order",
            json={
                'anchorId': anchor_id,
                'position': position,
                'recordIds': record_ids
            }
        )
        return True

    def update_view_name(
        self,
        table_id: str,
        view_id: str,
        name: str
    ) -> bool:
        """
        Update name of a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            name: New name for the view
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PUT',
            f"table/{table_id}/view/{view_id}/name",
            json={'name': name}
        )
        return True

    def update_view_description(
        self,
        table_id: str,
        view_id: str,
        description: str
    ) -> bool:
        """
        Update description of a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            description: New description for the view
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PUT',
            f"table/{table_id}/view/{view_id}/description",
            json={'description': description}
        )
        return True

    def update_view_share_meta(
        self,
        table_id: str,
        view_id: str,
        allow_copy: Optional[bool] = None,
        include_hidden_field: Optional[bool] = None,
        password: Optional[str] = None,
        include_records: Optional[bool] = None,
        submit_allow: Optional[bool] = None,
        submit_require_login: Optional[bool] = None
    ) -> bool:
        """
        Update share metadata for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            allow_copy: Whether to allow copying of shared data
            include_hidden_field: Whether to include hidden fields in shared view
            password: Password protection for shared view (min length 3)
            include_records: Whether to include records in shared view
            submit_allow: Whether to allow form submissions
            submit_require_login: Whether to require login for form submissions
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
            ValueError: If password is provided but less than 3 characters
        """
        if password is not None and len(password) < 3:
            raise ValueError("Password must be at least 3 characters long")
            
        data = {}
        if allow_copy is not None:
            data['allowCopy'] = allow_copy
        if include_hidden_field is not None:
            data['includeHiddenField'] = include_hidden_field
        if password is not None:
            data['password'] = password
        if include_records is not None:
            data['includeRecords'] = include_records
        if submit_allow is not None or submit_require_login is not None:
            data['submit'] = {}
            if submit_allow is not None:
                data['submit']['allow'] = submit_allow
            if submit_require_login is not None:
                data['submit']['requireLogin'] = submit_require_login
            
        self._make_request(
            'PUT',
            f"table/{table_id}/view/{view_id}/share-meta",
            json=data
        )
        return True

    def refresh_view_share_id(
        self,
        table_id: str,
        view_id: str
    ) -> str:
        """
        Refresh share ID for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            str: New share ID
            
        Raises:
            APIError: If the refresh fails
        """
        response = self._make_request(
            'POST',
            f"table/{table_id}/view/{view_id}/refresh-share-id"
        )
        return response['shareId']

    def disable_view_share(
        self,
        table_id: str,
        view_id: str
    ) -> bool:
        """
        Disable sharing for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            bool: True if sharing was successfully disabled
            
        Raises:
            APIError: If the operation fails
        """
        self._make_request(
            'POST',
            f"table/{table_id}/view/{view_id}/disable-share"
        )
        return True

    def enable_view_share(
        self,
        table_id: str,
        view_id: str
    ) -> str:
        """
        Enable sharing for a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            str: Share ID for the enabled view
            
        Raises:
            APIError: If the operation fails
        """
        response = self._make_request(
            'POST',
            f"table/{table_id}/view/{view_id}/enable-share"
        )
        return response['shareId']

    def install_view_plugin(
        self,
        table_id: str,
        plugin_id: str,
        name: Optional[str] = None
    ) -> PluginInstallation:
        """
        Install a plugin to create a new plugin view.
        
        Args:
            table_id: ID of the table
            plugin_id: ID of the plugin to install
            name: Optional display name for the plugin view
            
        Returns:
            PluginInstallation: Information about the installed plugin
            
        Raises:
            APIError: If the installation fails
        """
        data = {'pluginId': plugin_id}
        if name is not None:
            data['name'] = name
            
        response = self._make_request(
            'POST',
            f"table/{table_id}/view/plugin",
            json=data
        )
        return PluginInstallation.from_api_response(response)

    def get_dashboards(
        self,
        base_id: str
    ) -> List[Dashboard]:
        """
        Get all dashboards in a base.
        
        Args:
            base_id: ID of the base
            
        Returns:
            List[Dashboard]: List of dashboards
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"base/{base_id}/dashboard"
        )
        # API returns a nested array, we need to flatten it
        dashboards = [item for sublist in response for item in sublist]
        return [Dashboard.from_api_response(d) for d in dashboards]

    def create_dashboard(
        self,
        base_id: str,
        name: str
    ) -> Dashboard:
        """
        Create a new dashboard in a base.
        
        Args:
            base_id: ID of the base
            name: Display name for the dashboard
            
        Returns:
            Dashboard: The created dashboard
            
        Raises:
            APIError: If the creation fails
        """
        response = self._make_request(
            'POST',
            f"base/{base_id}/dashboard",
            json={'name': name}
        )
        return Dashboard.from_api_response(response)

    def get_dashboard(
        self,
        base_id: str,
        dashboard_id: str
    ) -> Dashboard:
        """
        Get a dashboard by ID.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            
        Returns:
            Dashboard: The requested dashboard
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"base/{base_id}/dashboard/{dashboard_id}"
        )
        return Dashboard.from_api_response(response)

    def delete_dashboard(
        self,
        base_id: str,
        dashboard_id: str
    ) -> bool:
        """
        Delete a dashboard.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._make_request(
            'DELETE',
            f"base/{base_id}/dashboard/{dashboard_id}"
        )
        return True

    def rename_dashboard(
        self,
        base_id: str,
        dashboard_id: str,
        name: str
    ) -> Dashboard:
        """
        Rename a dashboard.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            name: New name for the dashboard
            
        Returns:
            Dashboard: The renamed dashboard
            
        Raises:
            APIError: If the rename fails
        """
        response = self._make_request(
            'PATCH',
            f"base/{base_id}/dashboard/{dashboard_id}/rename",
            json={'name': name}
        )
        return Dashboard.from_api_response(response)

    def update_dashboard_layout(
        self,
        base_id: str,
        dashboard_id: str,
        layout: List[DashboardLayout]
    ) -> Dashboard:
        """
        Update a dashboard's layout.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            layout: List of layout configurations for dashboard widgets
            
        Returns:
            Dashboard: The updated dashboard
            
        Raises:
            APIError: If the update fails
        """
        data = {
            'layout': [
                {
                    'pluginInstallId': item.plugin_install_id,
                    'x': item.x,
                    'y': item.y,
                    'w': item.w,
                    'h': item.h
                }
                for item in layout
            ]
        }
        response = self._make_request(
            'PATCH',
            f"base/{base_id}/dashboard/{dashboard_id}/layout",
            json=data
        )
        return Dashboard.from_api_response(response)

    def install_dashboard_plugin(
        self,
        base_id: str,
        dashboard_id: str,
        plugin_id: str,
        name: str
    ) -> DashboardPlugin:
        """
        Install a plugin to a dashboard.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            plugin_id: ID of the plugin to install
            name: Display name for the plugin
            
        Returns:
            DashboardPlugin: Information about the installed plugin
            
        Raises:
            APIError: If the installation fails
        """
        response = self._make_request(
            'POST',
            f"base/{base_id}/dashboard/{dashboard_id}/plugin",
            json={
                'pluginId': plugin_id,
                'name': name
            }
        )
        return DashboardPlugin.from_api_response(response)

    def remove_dashboard_plugin(
        self,
        base_id: str,
        dashboard_id: str,
        plugin_install_id: str
    ) -> bool:
        """
        Remove a plugin from a dashboard.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            plugin_install_id: ID of the plugin installation to remove
            
        Returns:
            bool: True if removal successful
            
        Raises:
            APIError: If the removal fails
        """
        self._make_request(
            'DELETE',
            f"base/{base_id}/dashboard/{dashboard_id}/plugin/{plugin_install_id}"
        )
        return True

    def rename_dashboard_plugin(
        self,
        base_id: str,
        dashboard_id: str,
        plugin_install_id: str,
        name: str
    ) -> DashboardPlugin:
        """
        Rename a plugin in a dashboard.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            plugin_install_id: ID of the plugin installation to rename
            name: New name for the plugin
            
        Returns:
            DashboardPlugin: The renamed plugin
            
        Raises:
            APIError: If the rename fails
        """
        response = self._make_request(
            'PATCH',
            f"base/{base_id}/dashboard/{dashboard_id}/plugin/{plugin_install_id}/rename",
            json={'name': name}
        )
        return DashboardPlugin.from_api_response(response)

    def get_dashboard_plugin(
        self,
        base_id: str,
        dashboard_id: str,
        plugin_install_id: str
    ) -> DashboardPlugin:
        """
        Get a dashboard plugin by ID.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            plugin_install_id: ID of the plugin installation
            
        Returns:
            DashboardPlugin: The requested plugin
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"base/{base_id}/dashboard/{dashboard_id}/plugin/{plugin_install_id}"
        )
        return DashboardPlugin.from_api_response(response)

    def update_dashboard_plugin_storage(
        self,
        base_id: str,
        dashboard_id: str,
        plugin_install_id: str,
        storage: Dict[str, Any]
    ) -> DashboardPlugin:
        """
        Update storage of a plugin in a dashboard.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            plugin_install_id: ID of the plugin installation
            storage: New storage data for the plugin
            
        Returns:
            DashboardPlugin: The updated plugin
            
        Raises:
            APIError: If the update fails
        """
        response = self._make_request(
            'PATCH',
            f"base/{base_id}/dashboard/{dashboard_id}/plugin/{plugin_install_id}/update-storage",
            json={'storage': storage}
        )
        return DashboardPlugin.from_api_response(response)

    def update_view_plugin_storage(
        self,
        table_id: str,
        view_id: str,
        plugin_install_id: str,
        storage: Dict[str, Any]
    ) -> PluginInstallation:
        """
        Update storage of a plugin in a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            plugin_install_id: ID of the plugin installation
            storage: New storage data for the plugin
            
        Returns:
            PluginInstallation: The updated plugin
            
        Raises:
            APIError: If the update fails
        """
        response = self._make_request(
            'PATCH',
            f"table/{table_id}/view/{view_id}/plugin/{plugin_install_id}",
            json={'storage': storage}
        )
        return PluginInstallation.from_api_response(response)

    def get_view_plugin(
        self,
        table_id: str,
        view_id: str
    ) -> PluginInstallation:
        """
        Get a view plugin by ID.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            PluginInstallation: The requested plugin
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"table/{table_id}/view/{view_id}/plugin"
        )
        return PluginInstallation.from_api_response(response)

    def get_table_aggregations(
        self,
        table_id: str
    ) -> List[Aggregation]:
        """
        Get aggregations for a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[Aggregation]: List of aggregations
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"table/{table_id}/aggregation"
        )
        return [Aggregation.from_api_response(a) for a in response]

    def get_table_row_count(
        self,
        table_id: str,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None
    ) -> int:
        """
        Get row count for a table or view.
        
        Args:
            table_id: ID of the table
            view_id: Optional view ID to filter by
            ignore_view_query: Whether to ignore view's filter/sort
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            filter_link_cell_candidate: Filter by link cell candidates
            filter_link_cell_selected: Filter by link cell selection
            selected_record_ids: Filter by specific record IDs
            
        Returns:
            int: Number of rows
            
        Raises:
            APIError: If the request fails
        """
        params = {}
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
            
        response = self._make_request(
            'GET',
            f"table/{table_id}/aggregation/row-count",
            params=params
        )
        return response['rowCount']

    def get_table_group_points(
        self,
        table_id: str,
        view_id: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        group_by: Optional[str] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        ignore_view_query: Optional[bool] = None
    ) -> Optional[List[GroupPoint]]:
        """
        Get group points for a table or view.
        
        Args:
            table_id: ID of the table
            view_id: Optional view ID to filter by
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            group_by: Group specification
            collapsed_group_ids: List of collapsed group IDs
            ignore_view_query: Whether to ignore view's filter/sort
            
        Returns:
            Optional[List[GroupPoint]]: List of group points if any
            
        Raises:
            APIError: If the request fails
        """
        params = {}
        if view_id:
            params['viewId'] = view_id
        if filter:
            params['filter'] = filter
        if search:
            params['search'] = search
        if group_by:
            params['groupBy'] = group_by
        if collapsed_group_ids:
            params['collapsedGroupIds'] = collapsed_group_ids
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
            
        response = self._make_request(
            'GET',
            f"table/{table_id}/aggregation/group-points",
            params=params
        )
        return [GroupPoint.from_api_response(p) for p in response] if response else None

    def get_table_calendar_daily_collection(
        self,
        table_id: str,
        start_date: str,
        end_date: str,
        start_date_field_id: str,
        end_date_field_id: str,
        view_id: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        ignore_view_query: Optional[bool] = None
    ) -> CalendarDailyCollection:
        """
        Get calendar daily collection for a table or view.
        
        Args:
            table_id: ID of the table
            start_date: Start date for the range
            end_date: End date for the range
            start_date_field_id: ID of the start date field
            end_date_field_id: ID of the end date field
            view_id: Optional view ID to filter by
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            ignore_view_query: Whether to ignore view's filter/sort
            
        Returns:
            CalendarDailyCollection: Calendar daily collection data
            
        Raises:
            APIError: If the request fails
        """
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'startDateFieldId': start_date_field_id,
            'endDateFieldId': end_date_field_id
        }
        if view_id:
            params['viewId'] = view_id
        if filter:
            params['filter'] = filter
        if search:
            params['search'] = search
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
            
        response = self._make_request(
            'GET',
            f"table/{table_id}/aggregation/calendar-daily-collection",
            params=params
        )
        return CalendarDailyCollection.from_api_response(response)

    def get_table_search_count(
        self,
        table_id: str,
        filter: Optional[Dict[str, Any]] = None,
        view_id: Optional[str] = None,
        search: Optional[List[Any]] = None,
        ignore_view_query: Optional[bool] = None
    ) -> int:
        """
        Get search result count with query.
        
        Args:
            table_id: ID of the table
            filter: Filter object for complex queries
            view_id: Optional view ID to filter by
            search: Search parameters [value, field, exact]
            ignore_view_query: Whether to ignore view's filter/sort
            
        Returns:
            int: Number of search results
            
        Raises:
            APIError: If the request fails
        """
        params = {}
        if filter:
            params['filter'] = filter
        if view_id:
            params['viewId'] = view_id
        if search:
            params['search'] = search
        if ignore_view_query is not None:
            params['ignoreViewQuery'] = ignore_view_query
            
        response = self._make_request(
            'GET',
            f"table/{table_id}/aggregation/search-count",
            params=params
        )
        return response['count']

    def get_table_search_index(
        self,
        table_id: str,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None
    ) -> Optional[List[SearchIndex]]:
        """
        Get record index with search query.
        
        Args:
            table_id: ID of the table
            view_id: Optional view ID to filter by
            ignore_view_query: Whether to ignore view's filter/sort
            filter_by_tql: Filter using Teable Query Language
            filter: Filter object for complex queries
            search: Search parameters [value, field, exact]
            filter_link_cell_candidate: Filter by link cell candidates
            filter_link_cell_selected: Filter by link cell selection
            selected_record_ids: Filter by specific record IDs
            
        Returns:
            Optional[List[SearchIndex]]: List of search indices if any
            
        Raises:
            APIError: If the request fails
        """
        params = {}
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
            
        response = self._make_request(
            'GET',
            f"table/{table_id}/aggregation/search-index",
            params=params
        )
        return [SearchIndex.from_api_response(i) for i in response] if response else None

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
            
        data = {
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
            
        response = self._make_request(
            'POST',
            f"base/{base_id}/table/",
            json=data
        )
        return Table.from_api_response(response, self)

    def delete_table(
        self,
        base_id: str,
        table_id: str
    ) -> bool:
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
        self._make_request(
            'DELETE',
            f"base/{base_id}/table/{table_id}"
        )
        return True

    def get_base_table(
        self,
        base_id: str,
        table_id: str
    ) -> Table:
        """
        Get a table from a base by ID.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            
        Returns:
            Table: The requested table
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"base/{base_id}/table/{table_id}"
        )
        return Table.from_api_response(response, self)

    def get_base_tables(
        self,
        base_id: str
    ) -> List[Table]:
        """
        Get all tables in a base.
        
        Args:
            base_id: ID of the base
            
        Returns:
            List[Table]: List of tables
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"base/{base_id}/table"
        )
        tables = [Table.from_api_response(t, self) for t in response]
        
        # Update cache
        for table in tables:
            self._cache['tables'][table.table_id] = table
            
        return tables

    def permanent_delete_table(
        self,
        base_id: str,
        table_id: str
    ) -> bool:
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
        self._make_request(
            'DELETE',
            f"base/{base_id}/table/{table_id}/permanent"
        )
        return True

    def update_table_name(
        self,
        base_id: str,
        table_id: str,
        name: str
    ) -> bool:
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
        self._make_request(
            'PUT',
            f"base/{base_id}/table/{table_id}/name",
            json={'name': name}
        )
        return True

    def update_table_icon(
        self,
        base_id: str,
        table_id: str,
        icon: str
    ) -> bool:
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
        self._make_request(
            'PUT',
            f"base/{base_id}/table/{table_id}/icon",
            json={'icon': icon}
        )
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
            
        self._make_request(
            'PUT',
            f"base/{base_id}/table/{table_id}/order",
            json={
                'anchorId': anchor_id,
                'position': position
            }
        )
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
        self._make_request(
            'PUT',
            f"base/{base_id}/table/{table_id}/description",
            json={'description': description}
        )
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
            
        self._make_request(
            'PUT',
            f"base/{base_id}/table/{table_id}/db-table-name",
            json={'dbTableName': db_table_name}
        )
        return True

    def get_table_default_view_id(
        self,
        base_id: str,
        table_id: str
    ) -> str:
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
        response = self._make_request(
            'GET',
            f"base/{base_id}/table/{table_id}/default-view-id"
        )
        return response['id']

    def get_table_permission(
        self,
        base_id: str,
        table_id: str
    ) -> TablePermission:
        """
        Get permissions for a table.
        
        Args:
            base_id: ID of the base
            table_id: ID of the table
            
        Returns:
            TablePermission: Table permission information
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"base/{base_id}/table/{table_id}/permission"
        )
        return TablePermission.from_api_response(response)

    def get_selection_range_to_id(
        self,
        table_id: str,
        ranges: str,
        return_type: Literal['recordId', 'fieldId', 'all'],
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
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> SelectionRange:
        """
        Get the ID of records and fields from the selected range.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
            return_type: Type of IDs to return ('recordId', 'fieldId', 'all')
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
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections ('rows' or 'columns')
            
        Returns:
            SelectionRange: Selection range information
            
        Raises:
            APIError: If the request fails
        """
        params = {
            'ranges': ranges,
            'returnType': return_type
        }
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
        if exclude_field_ids:
            params['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            params['type'] = selection_type
            
        response = self._make_request(
            'GET',
            f"table/{table_id}/selection/range-to-id",
            params=params
        )
        return SelectionRange.from_api_response(response)

    def get_view_filter_link_records(
        self,
        table_id: str,
        view_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get associated records for a view filter configuration.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            List[Dict[str, Any]]: List of associated records grouped by table
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"table/{table_id}/view/{view_id}/filter-link-records"
        )
        return response

    def clear_selection(
        self,
        table_id: str,
        ranges: List[List[int]],
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[List[Dict[str, Any]]] = None,
        group_by: Optional[List[Dict[str, str]]] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> bool:
        """
        Clear the selection range.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
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
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections ('rows' or 'columns')
            
        Returns:
            bool: True if successful
            
        Raises:
            APIError: If the request fails
        """
        data = {
            'ranges': ranges
        }
        if view_id:
            data['viewId'] = view_id
        if ignore_view_query is not None:
            data['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql:
            data['filterByTql'] = filter_by_tql
        if filter:
            data['filter'] = filter
        if search:
            data['search'] = search
        if filter_link_cell_candidate:
            data['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected:
            data['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids:
            data['selectedRecordIds'] = selected_record_ids
        if order_by:
            data['orderBy'] = order_by
        if group_by:
            data['groupBy'] = group_by
        if collapsed_group_ids:
            data['collapsedGroupIds'] = collapsed_group_ids
        if exclude_field_ids:
            data['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            data['type'] = selection_type
            
        self._make_request(
            'PATCH',
            f"table/{table_id}/selection/clear",
            json=data
        )
        return True

    def get_selection_copy(
        self,
        table_id: str,
        ranges: str,
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
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> Dict[str, Any]:
        """
        Get copy content from selection range.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
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
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections ('rows' or 'columns')
            
        Returns:
            Dict[str, Any]: Copy content and header information
            
        Raises:
            APIError: If the request fails
        """
        params = {
            'ranges': ranges
        }
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
        if exclude_field_ids:
            params['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            params['type'] = selection_type
            
        return self._make_request(
            'GET',
            f"table/{table_id}/selection/copy",
            params=params
        )

    def paste_selection(
        self,
        table_id: str,
        ranges: List[List[int]],
        content: str,
        header: Optional[List[Dict[str, Any]]] = None,
        view_id: Optional[str] = None,
        ignore_view_query: Optional[bool] = None,
        filter_by_tql: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        search: Optional[List[Any]] = None,
        filter_link_cell_candidate: Optional[Union[str, List[str]]] = None,
        filter_link_cell_selected: Optional[Union[str, List[str]]] = None,
        selected_record_ids: Optional[List[str]] = None,
        order_by: Optional[List[Dict[str, Any]]] = None,
        group_by: Optional[List[Dict[str, str]]] = None,
        collapsed_group_ids: Optional[List[str]] = None,
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> Dict[str, List[List[int]]]:
        """
        Paste content into selection range.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
            content: Content to paste
            header: Optional table header for paste operation
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
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections ('rows' or 'columns')
            
        Returns:
            Dict[str, List[List[int]]]: Updated ranges after paste
            
        Raises:
            APIError: If the request fails
        """
        data = {
            'ranges': ranges,
            'content': content
        }
        if header is not None:
            data['header'] = header
        if view_id:
            data['viewId'] = view_id
        if ignore_view_query is not None:
            data['ignoreViewQuery'] = ignore_view_query
        if filter_by_tql:
            data['filterByTql'] = filter_by_tql
        if filter:
            data['filter'] = filter
        if search:
            data['search'] = search
        if filter_link_cell_candidate:
            data['filterLinkCellCandidate'] = filter_link_cell_candidate
        if filter_link_cell_selected:
            data['filterLinkCellSelected'] = filter_link_cell_selected
        if selected_record_ids:
            data['selectedRecordIds'] = selected_record_ids
        if order_by:
            data['orderBy'] = order_by
        if group_by:
            data['groupBy'] = group_by
        if collapsed_group_ids:
            data['collapsedGroupIds'] = collapsed_group_ids
        if exclude_field_ids:
            data['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            data['type'] = selection_type
            
        return self._make_request(
            'PATCH',
            f"table/{table_id}/selection/paste",
            json=data
        )

    def delete_selection(
        self,
        table_id: str,
        ranges: str,
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
        exclude_field_ids: Optional[List[str]] = None,
        selection_type: Optional[Literal['rows', 'columns']] = None
    ) -> Dict[str, List[str]]:
        """
        Delete the selected data.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
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
            exclude_field_ids: List of field IDs to exclude
            selection_type: Type of non-contiguous selections ('rows' or 'columns')
            
        Returns:
            Dict[str, List[str]]: IDs of deleted records
            
        Raises:
            APIError: If the request fails
        """
        params = {
            'ranges': ranges
        }
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
        if exclude_field_ids:
            params['excludeFieldIds'] = exclude_field_ids
        if selection_type:
            params['type'] = selection_type
            
        return self._make_request(
            'DELETE',
            f"table/{table_id}/selection/delete",
            params=params
        )

    def temporary_paste(
        self,
        table_id: str,
        ranges: List[List[int]],
        content: str,
        view_id: Optional[str] = None,
        exclude_field_ids: Optional[List[str]] = None,
        ignore_view_query: Optional[bool] = None,
        header: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Dict[str, Any]]]:
        """
        Paste operation for pre-filled table rows.
        
        Args:
            table_id: ID of the table
            ranges: Coordinates [column, row][] of selected range
            content: Content to paste
            view_id: Optional view ID to filter by
            exclude_field_ids: Optional list of field IDs to exclude
            ignore_view_query: Whether to ignore view's filter/sort
            header: Optional table header for paste operation
            
        Returns:
            List[Dict[str, Dict[str, Any]]]: List of pre-filled records
            
        Raises:
            APIError: If the request fails
        """
        data = {
            'ranges': ranges,
            'content': content
        }
        if view_id:
            data['viewId'] = view_id
        if exclude_field_ids:
            data['excludeFieldIds'] = exclude_field_ids
        if ignore_view_query is not None:
            data['ignoreViewQuery'] = ignore_view_query
        if header is not None:
            data['header'] = header
            
        return self._make_request(
            'PATCH',
            f"table/{table_id}/selection/temporaryPaste",
            json=data
        )

    def post_field_plan(
        self,
        table_id: str,
        field_type: str,
        name: Optional[str] = None,
        unique: Optional[bool] = None,
        not_null: Optional[bool] = None,
        db_field_name: Optional[str] = None,
        is_lookup: Optional[bool] = None,
        description: Optional[str] = None,
        lookup_options: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        field_id: Optional[str] = None,
        order: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate calculation plan for creating the field.
        
        Args:
            table_id: ID of the table
            field_type: Type of field to create
            name: Optional name for the field
            unique: Whether field should be unique
            not_null: Whether field should be not null
            db_field_name: Optional database field name
            is_lookup: Whether field is a lookup field
            description: Optional field description
            lookup_options: Optional lookup configuration
            options: Optional field type-specific options
            field_id: Optional field ID to use
            order: Optional order configuration with viewId and orderIndex
            
        Returns:
            Dict[str, Any]: Field creation plan containing:
                - estimateTime: Estimated time for creation
                - graph: Dependency graph with nodes, edges, and combos
                - updateCellCount: Number of cells to update
            
        Raises:
            APIError: If the request fails
        """
        data = {'type': field_type}
        if name is not None:
            data['name'] = name
        if unique is not None:
            data['unique'] = unique
        if not_null is not None:
            data['notNull'] = not_null
        if db_field_name is not None:
            data['dbFieldName'] = db_field_name
        if is_lookup is not None:
            data['isLookup'] = is_lookup
        if description is not None:
            data['description'] = description
        if lookup_options is not None:
            data['lookupOptions'] = lookup_options
        if options is not None:
            data['options'] = options
        if field_id is not None:
            data['id'] = field_id
        if order is not None:
            data['order'] = order
            
        return self._make_request(
            'POST',
            f"table/{table_id}/field/plan",
            json=data
        )

    def notify_attachment(
        self,
        token: str,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Attachment information.
        
        Args:
            token: Token for the attachment
            filename: Optional filename
            
        Returns:
            Dict[str, Any]: Attachment information containing:
                - token: Token for the uploaded file
                - size: File size in bytes
                - url: URL of the uploaded file
                - path: File path
                - mimetype: MIME type of the file
                - width: Optional image width
                - height: Optional image height
                - presignedUrl: Preview URL
            
        Raises:
            APIError: If the request fails
        """
        params = {}
        if filename:
            params['filename'] = filename
            
        return self._make_request(
            'POST',
            f"attachments/notify/{token}",
            params=params
        )

    def get_attachment(
        self,
        token: str,
        filename: Optional[str] = None
    ) -> bytes:
        """
        Upload attachment.
        
        Args:
            token: Token for the attachment
            filename: Optional filename for download
            
        Returns:
            bytes: Attachment data
            
        Raises:
            APIError: If the request fails
        """
        params = {}
        if filename:
            params['filename'] = filename
            
        response = self.session.get(
            f"{self.config.base_url}/attachments/{token}",
            params=params,
            headers={
                'Authorization': f'Bearer {self.config.api_key}'
            },
            stream=True
        )
        response.raise_for_status()
        return response.content

    def get_attachment_signature(
        self,
        content_type: str,
        content_length: int,
        attachment_type: int,
        expires_in: Optional[int] = None,
        hash_value: Optional[str] = None,
        base_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve upload signature.
        
        Args:
            content_type: Mime type of the file
            content_length: Size of the file in bytes
            attachment_type: Type of attachment (1-7)
            expires_in: Optional token expiration time in seconds
            hash_value: Optional file hash
            base_id: Optional base ID
            
        Returns:
            Dict[str, Any]: Upload signature containing:
                - url: Upload URL
                - uploadMethod: Upload method (e.g. POST)
                - token: Secret key
                - requestHeaders: Headers for upload request
            
        Raises:
            APIError: If the request fails
            ValueError: If attachment_type is not between 1 and 7
        """
        if not 1 <= attachment_type <= 7:
            raise ValueError("attachment_type must be between 1 and 7")
            
        data = {
            'contentType': content_type,
            'contentLength': content_length,
            'type': attachment_type
        }
        if expires_in is not None:
            data['expiresIn'] = expires_in
        if hash_value is not None:
            data['hash'] = hash_value
        if base_id is not None:
            data['baseId'] = base_id
            
        return self._make_request(
            'POST',
            "attachments/signature",
            json=data
        )

    def upload_attachment_with_token(
        self,
        token: str,
        file_data: bytes
    ) -> bool:
        """
        Upload attachment with token.
        
        Args:
            token: Upload token from get_attachment_signature
            file_data: Binary file data to upload
            
        Returns:
            bool: True if upload successful
            
        Raises:
            APIError: If the upload fails
        """
        self._make_request(
            'POST',
            f"attachments/upload/{token}",
            data=file_data,
            headers={
                'Content-Type': 'application/octet-stream'
            }
        )
        return True

    def update_user_name(
        self,
        name: str
    ) -> bool:
        """
        Update user name.
        
        Args:
            name: New name for the user
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PATCH',
            "user/name",
            json={'name': name}
        )
        return True

    def update_user_avatar(
        self,
        avatar_data: bytes
    ) -> bool:
        """
        Update user avatar.
        
        Args:
            avatar_data: Binary image data for avatar
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PATCH',
            "user/avatar",
            files={'file': ('avatar', avatar_data, 'image/*')}
        )
        return True

    def update_user_notify_meta(
        self,
        email: bool
    ) -> bool:
        """
        Update user notification meta.
        
        Args:
            email: Whether to enable email notifications
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._make_request(
            'PATCH',
            "user/notify-meta",
            json={'email': email}
        )
        return True

    def send_change_email_code(
        self,
        email: str,
        password: str
    ) -> Dict[str, str]:
        """
        Send change email code.
        
        Args:
            email: New email address
            password: Current password
            
        Returns:
            Dict[str, str]: Response containing:
                - token: Verification token
            
        Raises:
            APIError: If sending code fails
        """
        response = self._make_request(
            'POST',
            "auth/send-change-email-code",
            json={
                'email': email,
                'password': password
            }
        )
        return response

    def change_email(
        self,
        email: str,
        token: str,
        code: str
    ) -> bool:
        """
        Change email.
        
        Args:
            email: New email address
            token: Verification token
            code: Verification code
            
        Returns:
            bool: True if email change successful
            
        Raises:
            APIError: If the email change fails
        """
        self._make_request(
            'PATCH',
            "auth/change-email",
            json={
                'email': email,
                'token': token,
                'code': code
            }
        )
        return True

    def send_signup_verification_code(
        self,
        email: str
    ) -> Dict[str, str]:
        """
        Send signup verification code.
        
        Args:
            email: User email
            
        Returns:
            Dict[str, str]: Response containing:
                - token: Verification token
                - expiresTime: Token expiration time
            
        Raises:
            APIError: If sending code fails
        """
        response = self._make_request(
            'POST',
            "auth/send-signup-verification-code",
            json={'email': email}
        )
        return response

    def get_user(self) -> User:
        """
        Get user information via access token.
        
        Returns:
            User: User information
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request('GET', "auth/user")
        return User.from_api_response(response)

    def add_password(
        self,
        password: str
    ) -> bool:
        """
        Add password for user.
        
        Args:
            password: Password to add (minimum 8 chars, must contain uppercase and number)
            
        Returns:
            bool: True if password added successfully
            
        Raises:
            APIError: If adding password fails
            ValueError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        if not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one uppercase letter and one number")
            
        self._make_request(
            'POST',
            "auth/add-password",
            json={'password': password}
        )
        return True

    def reset_password(
        self,
        password: str,
        code: str
    ) -> bool:
        """
        Reset user password.
        
        Args:
            password: New password (minimum 8 chars, must contain uppercase and number)
            code: Reset code from email
            
        Returns:
            bool: True if password reset successful
            
        Raises:
            APIError: If the password reset fails
            ValueError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        if not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one uppercase letter and one number")
            
        self._make_request(
            'POST',
            "auth/reset-password",
            json={
                'password': password,
                'code': code
            }
        )
        return True

    def send_reset_password_email(
        self,
        email: str
    ) -> bool:
        """
        Send reset password email.
        
        Args:
            email: User email
            
        Returns:
            bool: True if email sent successfully
            
        Raises:
            APIError: If sending email fails
        """
        self._make_request(
            'POST',
            "auth/send-reset-password-email",
            json={'email': email}
        )
        return True

    def change_password(
        self,
        password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            password: Current password
            new_password: New password (minimum 8 chars, must contain uppercase and number)
            
        Returns:
            bool: True if password change successful
            
        Raises:
            APIError: If the password change fails
            ValueError: If new password doesn't meet requirements
        """
        if len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters")
            
        if not any(c.isupper() for c in new_password) or not any(c.isdigit() for c in new_password):
            raise ValueError("New password must contain at least one uppercase letter and one number")
            
        self._make_request(
            'PATCH',
            "auth/change-password",
            json={
                'password': password,
                'newPassword': new_password
            }
        )
        return True

    def signup(
        self,
        email: str,
        password: str,
        default_space_name: Optional[str] = None,
        ref_meta: Optional[Dict[str, str]] = None,
        verification: Optional[Dict[str, str]] = None
    ) -> User:
        """
        Sign up a new user.
        
        Args:
            email: User email
            password: User password (minimum 8 chars, must contain uppercase and number)
            default_space_name: Optional name for default space
            ref_meta: Optional reference metadata with query and referer
            verification: Optional verification with code and token
            
        Returns:
            User: User information
            
        Raises:
            APIError: If the sign up fails
            ValueError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        if not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one uppercase letter and one number")
            
        data = {
            'email': email,
            'password': password
        }
        
        if default_space_name:
            data['defaultSpaceName'] = default_space_name
        if ref_meta:
            data['refMeta'] = ref_meta
        if verification:
            data['verification'] = verification
            
        response = self._make_request(
            'POST',
            "auth/signup",
            json=data
        )
        return User.from_api_response(response)

    def signout(self) -> bool:
        """
        Sign out the current user.
        
        Returns:
            bool: True if sign out successful
            
        Raises:
            APIError: If the sign out fails
        """
        self._make_request('POST', "auth/signout")
        return True

    def signin(
        self,
        email: str,
        password: str
    ) -> User:
        """
        Sign in with email and password.
        
        Args:
            email: User email
            password: User password (minimum 8 chars)
            
        Returns:
            User: User information
            
        Raises:
            APIError: If the sign in fails
            ValueError: If password is less than 8 characters
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        response = self._make_request(
            'POST',
            "auth/signin",
            json={
                'email': email,
                'password': password
            }
        )
        return User.from_api_response(response)

    def create_db_connection(
        self,
        base_id: str
    ) -> Dict[str, Any]:
        """
        Create a database connection URL.
        
        Args:
            base_id: ID of the base
            
        Returns:
            Dict[str, Any]: Connection information containing:
                - dsn: Database connection details
                - connection: Connection pool stats
                - url: Connection URL
            
        Raises:
            APIError: If the creation fails
        """
        response = self._make_request(
            'POST',
            f"base/{base_id}/connection",
            json={'baseId': base_id}
        )
        return response

    def delete_db_connection(
        self,
        base_id: str
    ) -> bool:
        """
        Delete a database connection.
        
        Args:
            base_id: ID of the base
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._make_request(
            'DELETE',
            f"base/{base_id}/connection"
        )
        return True

    def get_db_connection(
        self,
        base_id: str
    ) -> Dict[str, Any]:
        """
        Get database connection information.
        
        Args:
            base_id: ID of the base
            
        Returns:
            Dict[str, Any]: Connection information containing:
                - dsn: Database connection details
                - connection: Connection pool stats
                - url: Connection URL
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request(
            'GET',
            f"base/{base_id}/connection"
        )
        return response

    def accept_invitation_link(
        self,
        invitation_code: str,
        invitation_id: str
    ) -> Dict[str, Optional[str]]:
        """
        Accept invitation link.
        
        Args:
            invitation_code: Code from the invitation
            invitation_id: ID of the invitation
            
        Returns:
            Dict[str, Optional[str]]: Response containing:
                - spaceId: ID of the space (if space invitation)
                - baseId: ID of the base (if base invitation)
            
        Raises:
            APIError: If accepting invitation fails
        """
        response = self._make_request(
            'POST',
            "invitation/link/accept",
            json={
                'invitationCode': invitation_code,
                'invitationId': invitation_id
            }
        )
        return response

    def get_user_info(self) -> User:
        """
        Get user information.
        
        Returns:
            User: User information
            
        Raises:
            APIError: If the request fails
        """
        response = self._make_request('GET', "auth/user/me")
        return User.from_api_response(response)

    def get_field_plan(
        self,
        table_id: str,
        field_id: str
    ) -> Dict[str, Any]:
        """
        Generate calculation plan for the field.
        
        Args:
            table_id: ID of the table
            field_id: ID of the field
            
        Returns:
            Dict[str, Any]: Field calculation plan containing:
                - estimateTime: Estimated time for calculation
                - graph: Dependency graph with nodes, edges, and combos
                - updateCellCount: Number of cells to update
            
        Raises:
            APIError: If the request fails
        """
        return self._make_request(
            'GET',
            f"table/{table_id}/field/{field_id}/plan"
        )

    def put_field_plan(
        self,
        table_id: str,
        field_id: str,
        field_type: str,
        name: Optional[str] = None,
        unique: Optional[bool] = None,
        not_null: Optional[bool] = None,
        db_field_name: Optional[str] = None,
        is_lookup: Optional[bool] = None,
        description: Optional[str] = None,
        lookup_options: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate calculation plan for converting the field.
        
        Args:
            table_id: ID of the table
            field_id: ID of the field
            field_type: New type for the field
            name: Optional new name for the field
            unique: Whether field should be unique
            not_null: Whether field should be not null
            db_field_name: Optional database field name
            is_lookup: Whether field is a lookup field
            description: Optional field description
            lookup_options: Optional lookup configuration
            options: Optional field type-specific options
            
        Returns:
            Dict[str, Any]: Field conversion plan containing:
                - estimateTime: Estimated time for conversion
                - graph: Dependency graph with nodes, edges, and combos
                - updateCellCount: Number of cells to update
                - skip: Whether conversion can be skipped
            
        Raises:
            APIError: If the request fails
        """
        data = {'type': field_type}
        if name is not None:
            data['name'] = name
        if unique is not None:
            data['unique'] = unique
        if not_null is not None:
            data['notNull'] = not_null
        if db_field_name is not None:
            data['dbFieldName'] = db_field_name
        if is_lookup is not None:
            data['isLookup'] = is_lookup
        if description is not None:
            data['description'] = description
        if lookup_options is not None:
            data['lookupOptions'] = lookup_options
        if options is not None:
            data['options'] = options
            
        return self._make_request(
            'PUT',
            f"table/{table_id}/field/{field_id}/plan",
            json=data
        )

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
            
        response = self._make_request(
            'GET',
            f"table/{table_id}/record/{record_id}/status",
            params=params
        )
        return RecordStatus.from_api_response(response)
