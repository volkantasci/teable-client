"""
View management module.

This module handles view operations including creation, modification, and configuration.
"""

from typing import Any, Dict, List, Literal, Optional, Union

from ..exceptions import ValidationError
from ..models.view import View
from ..models.plugin import PluginInstallation
from ..models.view_plugin import ViewPlugin
from .http import TeableHttpClient
from .cache import ResourceCache

def _validate_table_id(table_id: str) -> None:
    """Validate table ID."""
    if not isinstance(table_id, str) or not table_id:
        raise ValidationError("Table ID must be a non-empty string")

def _validate_view_id(view_id: str) -> None:
    """Validate view ID."""
    if not isinstance(view_id, str) or not view_id:
        raise ValidationError("View ID must be a non-empty string")

def _validate_plugin_id(plugin_id: str) -> None:
    """Validate plugin ID."""
    if not isinstance(plugin_id, str) or not plugin_id:
        raise ValidationError("Plugin ID must be a non-empty string")

def _validate_plugin_install_id(plugin_install_id: str) -> None:
    """Validate plugin installation ID."""
    if not isinstance(plugin_install_id, str) or not plugin_install_id:
        raise ValidationError("Plugin installation ID must be a non-empty string")

def _validate_storage_data(storage: Dict[str, Any]) -> None:
    """Validate plugin storage data."""
    if not isinstance(storage, dict):
        raise ValidationError("Storage data must be a dictionary")

def _validate_plugin_name(name: str) -> None:
    """Validate plugin name."""
    if not isinstance(name, str):
        raise ValidationError("Plugin name must be a string")
    if not name.strip():
        raise ValidationError("Plugin name cannot be empty")
    if len(name) > 255:
        raise ValidationError("Plugin name cannot exceed 255 characters")

ViewPosition = Literal['before', 'after']

class ViewManager:
    """
    Handles view operations.
    
    This class manages:
    - View creation and deletion
    - View configuration updates
    - View sharing settings
    - View plugins
    - View caching
    """
    
    def __init__(self, http_client: TeableHttpClient, cache: ResourceCache[View]):
        """
        Initialize the view manager.
        
        Args:
            http_client: HTTP client for API communication
            cache: Resource cache for views
        """
        self._http = http_client
        self._cache = cache
        self._cache.add_resource_type('views')
        
    def get_view(self, table_id: str, view_id: str) -> View:
        """
        Get a view by ID.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            View: The requested view
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the request fails
        """
        _validate_table_id(table_id)
        _validate_view_id(view_id)
        
        cache_key = f"{table_id}_{view_id}"
        cached = self._cache.get('views', cache_key)
        if cached:
            return cached
            
        response = self._http.request(
            'GET',
            f"/table/{table_id}/view/{view_id}"
        )
        view = View.from_api_response(response, self)
        self._cache.set('views', cache_key, view)
        return view
        
    def get_table_views(self, table_id: str) -> List[View]:
        """
        Get all views for a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[View]: List of views
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the request fails
        """
        _validate_table_id(table_id)
        
        response = self._http.request('GET', f"/table/{table_id}/view")
        views = [View.from_api_response(v, self) for v in response]
        
        # Update cache
        for view in views:
            cache_key = f"{table_id}_{view.view_id}"
            self._cache.set('views', cache_key, view)
            
        return views
        
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
            ValidationError: If input validation fails
            APIError: If the installation fails
        """
        _validate_table_id(table_id)
        _validate_plugin_id(plugin_id)
        
        if name is not None:
            _validate_plugin_name(name)
            
        data: Dict[str, Any] = {'pluginId': plugin_id}
        if name is not None:
            data['name'] = name
            
        response = self._http.request(
            'POST',
            f"/table/{table_id}/view/plugin",
            json=data
        )
        return PluginInstallation.from_api_response(response)
        
    def get_view_plugin(
        self,
        table_id: str,
        view_id: str
    ) -> ViewPlugin:
        """
        Get details of a plugin installed in a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            
        Returns:
            ViewPlugin: Plugin information including:
                - pluginId: ID of the plugin
                - pluginInstallId: ID of the installation
                - baseId: ID of the base
                - name: Display name
                - url: Plugin URL
                - storage: Plugin storage data
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the request fails
        """
        _validate_table_id(table_id)
        _validate_view_id(view_id)
        
        response = self._http.request(
            'GET',
            f"/table/{table_id}/view/{view_id}/plugin"
        )
        return ViewPlugin.from_api_response(response)
        
    def update_view_plugin_storage(
        self,
        table_id: str,
        view_id: str,
        plugin_install_id: str,
        storage: Dict[str, Any]
    ) -> ViewPlugin:
        """
        Update storage data for a plugin in a view.
        
        Args:
            table_id: ID of the table
            view_id: ID of the view
            plugin_install_id: ID of the plugin installation
            storage: New storage data
            
        Returns:
            ViewPlugin: Updated plugin information
            
        Raises:
            ValidationError: If input validation fails
            APIError: If the update fails
        """
        _validate_table_id(table_id)
        _validate_view_id(view_id)
        _validate_plugin_install_id(plugin_install_id)
        _validate_storage_data(storage)
        
        response = self._http.request(
            'PATCH',
            f"/table/{table_id}/view/{view_id}/plugin/{plugin_install_id}",
            json={'storage': storage}
        )
        return ViewPlugin.from_api_response(response)
