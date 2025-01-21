"""
Table management module.

This module handles table operations including creation, modification, and deletion.
"""

from typing import Any, Dict, List, Optional, Union

from ..models.table import Table
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
        
    def get_table(self, table_id: str) -> Table:
        """
        Get a table by ID.
        
        Args:
            table_id: ID of the table
            
        Returns:
            Table: The requested table
            
        Raises:
            APIError: If the request fails
        """
        cached = self._cache.get('tables', table_id)
        if cached:
            return cached
            
        response = self._http.request('GET', f"table/{table_id}")
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
        response = self._http.request('GET', "table")
        tables = [Table.from_api_response(t, self) for t in response]
        
        # Update cache
        for table in tables:
            self._cache.set('tables', table.table_id, table)
            
        return tables
        
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
            f"base/{base_id}/table/",
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
            f"base/{base_id}/table/{table_id}"
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
            f"base/{base_id}/table/{table_id}/permanent"
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
            f"base/{base_id}/table/{table_id}/name",
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
            f"base/{base_id}/table/{table_id}/icon",
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
            f"base/{base_id}/table/{table_id}/order",
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
            f"base/{base_id}/table/{table_id}/description",
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
            f"base/{base_id}/table/{table_id}/db-table-name",
            json={'dbTableName': db_table_name}
        )
        # Invalidate cache since table was modified
        self._cache.delete('tables', table_id)
        return True
        
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
            f"base/{base_id}/table/{table_id}/default-view-id"
        )
        return response['id']
