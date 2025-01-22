"""
View management module.

This module handles view operations including creation, modification, and configuration.
"""

from typing import Any, Dict, List, Literal, Optional, Union

from ..models.view import View
from ..models.plugin import PluginInstallation
from ..models.view_plugin import ViewPlugin
from .http import TeableHttpClient
from .cache import ResourceCache

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
            APIError: If the request fails
        """
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
            APIError: If the request fails
        """
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
            APIError: If the installation fails
        """
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
            APIError: If the request fails
        """
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
            APIError: If the update fails
        """
        response = self._http.request(
            'PATCH',
            f"/table/{table_id}/view/{view_id}/plugin/{plugin_install_id}",
            json={'storage': storage}
        )
        return ViewPlugin.from_api_response(response)
