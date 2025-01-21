"""
Field management module.

This module handles field operations including creation, modification, and type conversion.
"""

from typing import Any, Dict, List, Optional

from ..models.field import Field
from .http import TeableHttpClient
from .cache import ResourceCache

class FieldManager:
    """
    Handles field operations.
    
    This class manages:
    - Field creation and deletion
    - Field metadata updates
    - Field type conversion
    - Field caching
    """
    
    def __init__(self, http_client: TeableHttpClient, cache: ResourceCache[Field]):
        """
        Initialize the field manager.
        
        Args:
            http_client: HTTP client for API communication
            cache: Resource cache for fields
        """
        self._http = http_client
        self._cache = cache
        self._cache.add_resource_type('fields')
        
    def get_field(self, table_id: str, field_id: str) -> Field:
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
        cache_key = f"{table_id}_{field_id}"
        cached = self._cache.get('fields', cache_key)
        if cached:
            return cached
            
        response = self._http.request(
            'GET',
            f"table/{table_id}/field/{field_id}"
        )
        field = Field.from_api_response(response)
        self._cache.set('fields', cache_key, field)
        return field
        
    def get_table_fields(self, table_id: str) -> List[Field]:
        """
        Get all fields for a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[Field]: List of fields
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', f"table/{table_id}/field")
        fields = [Field.from_api_response(f) for f in response]
        
        # Update cache
        for field in fields:
            cache_key = f"{table_id}_{field.field_id}"
            self._cache.set('fields', cache_key, field)
            
        return fields
        
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
        data: Dict[str, Any] = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if db_field_name is not None:
            data['dbFieldName'] = db_field_name
            
        self._http.request(
            'PATCH',
            f"table/{table_id}/field/{field_id}",
            json=data
        )
        # Invalidate cache since field was modified
        cache_key = f"{table_id}_{field_id}"
        self._cache.delete('fields', cache_key)
        
    def delete_field(self, table_id: str, field_id: str) -> bool:
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
        self._http.request(
            'DELETE',
            f"table/{table_id}/field/{field_id}"
        )
        # Remove from cache
        cache_key = f"{table_id}_{field_id}"
        self._cache.delete('fields', cache_key)
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
        data: Dict[str, Any] = {'type': field_type}
        
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
            
        response = self._http.request(
            'PUT',
            f"table/{table_id}/field/{field_id}/convert",
            json=data
        )
        
        field = Field.from_api_response(response)
        # Update cache
        cache_key = f"{table_id}_{field_id}"
        self._cache.set('fields', cache_key, field)
        return field
        
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
        return self._http.request(
            'GET',
            f"table/{table_id}/field/{field_id}/filter-link-records"
        )
        
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
        return self._http.request(
            'GET',
            f"table/{table_id}/field/{field_id}/plan"
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
        data: Dict[str, Any] = {'type': field_type}
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
            
        return self._http.request(
            'POST',
            f"table/{table_id}/field/plan",
            json=data
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
        data: Dict[str, Any] = {'type': field_type}
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
            
        return self._http.request(
            'PUT',
            f"table/{table_id}/field/{field_id}/plan",
            json=data
        )
