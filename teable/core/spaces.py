"""
Space and base management module.

This module handles space and base operations including creation, modification, and deletion.
"""

from typing import Any, Dict, List, Optional

from ..models.space import Space
from ..models.base import Base
from ..models.trash import ResourceType, TrashResponse
from .http import TeableHttpClient
from .cache import ResourceCache

class SpaceManager:
    """
    Handles space and base operations.
    
    This class manages:
    - Space creation and deletion
    - Space metadata updates
    - Base creation and deletion
    - Base metadata updates
    - Space/Base caching
    """
    
    def __init__(
        self,
        http_client: TeableHttpClient,
        space_cache: ResourceCache[Space],
        base_cache: ResourceCache[Base]
    ):
        """
        Initialize the space manager.
        
        Args:
            http_client: HTTP client for API communication
            space_cache: Resource cache for spaces
            base_cache: Resource cache for bases
        """
        self._http = http_client
        self._space_cache = space_cache
        self._base_cache = base_cache
        self._space_cache.add_resource_type('spaces')
        self._base_cache.add_resource_type('bases')
        
    def get_spaces(self) -> List[Space]:
        """
        Get all accessible spaces.
        
        Returns:
            List[Space]: List of spaces
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', "space")
        spaces = [Space.from_api_response(s, self) for s in response]
        
        # Update cache
        for space in spaces:
            self._space_cache.set('spaces', space.space_id, space)
            
        return spaces
        
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
        cached = self._space_cache.get('spaces', space_id)
        if cached:
            return cached
            
        response = self._http.request('GET', f"space/{space_id}")
        space = Space.from_api_response(response, self)
        self._space_cache.set('spaces', space_id, space)
        return space
        
    def create_space(self, name: str) -> Space:
        """
        Create a new space.
        
        Args:
            name: Display name for the space
            
        Returns:
            Space: The created space
            
        Raises:
            APIError: If the creation fails
        """
        response = self._http.request(
            'POST',
            "space",
            json={'name': name}
        )
        space = Space.from_api_response(response, self)
        self._space_cache.set('spaces', space.space_id, space)
        return space
        
    def get_bases(self) -> List[Base]:
        """
        Get all accessible bases.
        
        Returns:
            List[Base]: List of bases
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', "base/access/all")
        bases = [Base.from_api_response(b, self) for b in response]
        
        # Update cache
        for base in bases:
            self._base_cache.set('bases', base.base_id, base)
            
        return bases
        
    def get_shared_bases(self) -> List[Base]:
        """
        Get all shared bases.
        
        Returns:
            List[Base]: List of shared bases
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', "base/shared-base")
        bases = [Base.from_api_response(b, self) for b in response]
        
        # Update cache
        for base in bases:
            self._base_cache.set('bases', base.base_id, base)
            
        return bases
        
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
        cached = self._base_cache.get('bases', base_id)
        if cached:
            return cached
            
        response = self._http.request('GET', f"base/{base_id}")
        base = Base.from_api_response(response, self)
        self._base_cache.set('bases', base_id, base)
        return base
        
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
            
        Raises:
            APIError: If the creation fails
        """
        data: Dict[str, Any] = {'spaceId': space_id}
        if name:
            data['name'] = name
        if icon:
            data['icon'] = icon
            
        response = self._http.request(
            'POST',
            "base",
            json=data
        )
        base = Base.from_api_response(response, self)
        self._base_cache.set('bases', base.base_id, base)
        return base
        
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
            
        Raises:
            APIError: If the duplication fails
        """
        data: Dict[str, Any] = {
            'fromBaseId': from_base_id,
            'spaceId': space_id,
            'withRecords': with_records
        }
        if name:
            data['name'] = name
            
        response = self._http.request(
            'POST',
            "base/duplicate",
            json=data
        )
        base = Base.from_api_response(response, self)
        self._base_cache.set('bases', base.base_id, base)
        return base
        
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
            
        Raises:
            APIError: If the creation fails
        """
        response = self._http.request(
            'POST',
            "base/create-from-template",
            json={
                'spaceId': space_id,
                'templateId': template_id,
                'withRecords': with_records
            }
        )
        base = Base.from_api_response(response, self)
        self._base_cache.set('bases', base.base_id, base)
        return base
        
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
        response = self._http.request(
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
        params: Dict[str, Any] = {
            'resourceId': resource_id,
            'resourceType': resource_type.value
        }
        if cursor:
            params['cursor'] = cursor
            
        response = self._http.request(
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
        params: Dict[str, Any] = {
            'resourceId': resource_id,
            'resourceType': resource_type.value
        }
        if cursor:
            params['cursor'] = cursor
            
        self._http.request(
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
        self._http.request(
            'POST',
            f"trash/restore/{trash_id}"
        )
        return True
        
    def create_db_connection(self, base_id: str) -> Dict[str, Any]:
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
        return self._http.request(
            'POST',
            f"base/{base_id}/connection",
            json={'baseId': base_id}
        )
        
    def delete_db_connection(self, base_id: str) -> bool:
        """
        Delete a database connection.
        
        Args:
            base_id: ID of the base
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"base/{base_id}/connection"
        )
        return True
        
    def get_db_connection(self, base_id: str) -> Dict[str, Any]:
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
        return self._http.request(
            'GET',
            f"base/{base_id}/connection"
        )
