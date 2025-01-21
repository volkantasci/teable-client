"""
Resource caching module.

This module provides caching functionality for API resources to reduce network requests.
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')

class ResourceCache(Generic[T]):
    """
    Caches API resources to reduce network requests.
    
    This class manages:
    - In-memory caching of resources
    - Cache invalidation
    - Resource lookup
    """
    
    def __init__(self):
        """Initialize an empty resource cache."""
        self._cache: Dict[str, Dict[str, T]] = {}
        
    def add_resource_type(self, resource_type: str) -> None:
        """
        Add a new resource type to the cache.
        
        Args:
            resource_type: Type of resource to cache (e.g., 'tables', 'fields')
        """
        if resource_type not in self._cache:
            self._cache[resource_type] = {}
            
    def get(self, resource_type: str, resource_id: str) -> Optional[T]:
        """
        Get a cached resource by type and ID.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            
        Returns:
            Optional[T]: Cached resource if found, None otherwise
        """
        return self._cache.get(resource_type, {}).get(resource_id)
        
    def set(self, resource_type: str, resource_id: str, resource: T) -> None:
        """
        Cache a resource.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            resource: Resource to cache
        """
        if resource_type not in self._cache:
            self._cache[resource_type] = {}
        self._cache[resource_type][resource_id] = resource
        
    def delete(self, resource_type: str, resource_id: str) -> None:
        """
        Remove a resource from the cache.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
        """
        if resource_type in self._cache:
            self._cache[resource_type].pop(resource_id, None)
            
    def clear_type(self, resource_type: str) -> None:
        """
        Clear all cached resources of a specific type.
        
        Args:
            resource_type: Type of resources to clear
        """
        if resource_type in self._cache:
            self._cache[resource_type].clear()
            
    def clear_all(self) -> None:
        """Clear all cached resources."""
        self._cache.clear()
        
    def get_all(self, resource_type: str) -> List[T]:
        """
        Get all cached resources of a specific type.
        
        Args:
            resource_type: Type of resources to retrieve
            
        Returns:
            List[T]: List of cached resources
        """
        return list(self._cache.get(resource_type, {}).values())
        
    def get_multiple(self, resource_type: str, resource_ids: List[str]) -> List[Optional[T]]:
        """
        Get multiple cached resources by their IDs.
        
        Args:
            resource_type: Type of resources
            resource_ids: List of resource IDs
            
        Returns:
            List[Optional[T]]: List of cached resources (None for uncached resources)
        """
        cache = self._cache.get(resource_type, {})
        return [cache.get(rid) for rid in resource_ids]
        
    def set_multiple(self, resource_type: str, resources: Dict[str, T]) -> None:
        """
        Cache multiple resources.
        
        Args:
            resource_type: Type of resources
            resources: Dictionary mapping resource IDs to resources
        """
        if resource_type not in self._cache:
            self._cache[resource_type] = {}
        self._cache[resource_type].update(resources)
        
    def delete_multiple(self, resource_type: str, resource_ids: List[str]) -> None:
        """
        Remove multiple resources from the cache.
        
        Args:
            resource_type: Type of resources
            resource_ids: List of resource IDs to remove
        """
        if resource_type in self._cache:
            for rid in resource_ids:
                self._cache[resource_type].pop(rid, None)
                
    def has_type(self, resource_type: str) -> bool:
        """
        Check if a resource type exists in the cache.
        
        Args:
            resource_type: Type of resource
            
        Returns:
            bool: True if resource type exists
        """
        return resource_type in self._cache
        
    def has_resource(self, resource_type: str, resource_id: str) -> bool:
        """
        Check if a specific resource is cached.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of the resource
            
        Returns:
            bool: True if resource is cached
        """
        return resource_id in self._cache.get(resource_type, {})
