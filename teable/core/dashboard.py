"""
Dashboard management module.

This module handles dashboard operations including creation, modification, and deletion.
"""

from typing import Any, Dict, List, Optional

from ..models.dashboard import Dashboard
from ..models.dashboard_plugin import DashboardPlugin
from .http import TeableHttpClient
from .cache import ResourceCache

class DashboardManager:
    """
    Handles dashboard operations.
    
    This class manages:
    - Dashboard creation and deletion
    - Dashboard configuration updates
    - Dashboard layout management
    """
    
    def __init__(self, http_client: TeableHttpClient, cache: ResourceCache[Dashboard]):
        """
        Initialize the dashboard manager.
        
        Args:
            http_client: HTTP client for API communication
            cache: Resource cache for dashboards
        """
        self._http = http_client
        self._cache = cache
        self._cache.add_resource_type('dashboards')
        
    def get_dashboards(self, base_id: str) -> List[Dashboard]:
        """
        Get all dashboards in a base.
        
        Args:
            base_id: ID of the base
            
        Returns:
            List[List[Dict[str, str]]]: List of dashboard groups, each containing:
                - id: Dashboard ID
                - name: Dashboard name
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request(
            'GET',
            f"/base/{base_id}/dashboard"
        )
        return [Dashboard.from_api_response(d) for group in response for d in group]
        
    def create_dashboard(
        self,
        base_id: str,
        name: str
    ) -> Dashboard:
        """
        Create a new dashboard.
        
        Args:
            base_id: ID of the base
            name: Name for the dashboard
            
        Returns:
            Dict[str, str]: Created dashboard info containing:
                - id: Dashboard ID
                - name: Dashboard name
            
        Raises:
            APIError: If the creation fails
        """
        response = self._http.request(
            'POST',
            f"/base/{base_id}/dashboard",
            json={'name': name}
        )
        
        cache_key = f"{base_id}_{response['id']}"
        self._cache.delete('dashboards', cache_key)
        return Dashboard.from_api_response(response)
        
    def install_plugin(
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
            DashboardPlugin: Installed plugin information
            
        Raises:
            APIError: If the installation fails
        """
        response = self._http.request(
            'POST',
            f"/base/{base_id}/dashboard/{dashboard_id}/plugin",
            json={
                'pluginId': plugin_id,
                'name': name
            }
        )
        return DashboardPlugin.from_api_response(response)
        
    def remove_plugin(
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
            plugin_install_id: ID of the plugin installation
            
        Returns:
            bool: True if removal successful
            
        Raises:
            APIError: If the removal fails
        """
        self._http.request(
            'DELETE',
            f"/base/{base_id}/dashboard/{dashboard_id}/plugin/{plugin_install_id}"
        )
        return True
        
    def rename_plugin(
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
            plugin_install_id: ID of the plugin installation
            name: New name for the plugin
            
        Returns:
            DashboardPlugin: Updated plugin information
            
        Raises:
            APIError: If the rename fails
        """
        response = self._http.request(
            'PATCH',
            f"/base/{base_id}/dashboard/{dashboard_id}/plugin/{plugin_install_id}/rename",
            json={'name': name}
        )
        return DashboardPlugin.from_api_response(response)
        
    def get_plugin(
        self,
        base_id: str,
        dashboard_id: str,
        plugin_install_id: str
    ) -> DashboardPlugin:
        """
        Get details of an installed plugin.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            plugin_install_id: ID of the plugin installation
            
        Returns:
            DashboardPlugin: Plugin information including:
                - pluginId: ID of the plugin
                - pluginInstallId: ID of the installation
                - baseId: ID of the base
                - name: Display name
                - storage: Plugin storage data
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request(
            'GET',
            f"/base/{base_id}/dashboard/{dashboard_id}/plugin/{plugin_install_id}"
        )
        return DashboardPlugin.from_api_response(response)
        
    def update_plugin_storage(
        self,
        base_id: str,
        dashboard_id: str,
        plugin_install_id: str,
        storage: Dict[str, Any]
    ) -> DashboardPlugin:
        """
        Update storage data for a plugin.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            plugin_install_id: ID of the plugin installation
            storage: New storage data
            
        Returns:
            DashboardPlugin: Updated plugin information
            
        Raises:
            APIError: If the update fails
        """
        response = self._http.request(
            'PATCH',
            f"/base/{base_id}/dashboard/{dashboard_id}/plugin/{plugin_install_id}/update-storage",
            json={'storage': storage}
        )
        return DashboardPlugin.from_api_response(response)

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
            Dict[str, Any]: Dashboard information containing:
                - id: Dashboard ID
                - name: Dashboard name
                - layout: List of plugin layouts
                - pluginMap: Mapping of plugin IDs to configurations
            
        Raises:
            APIError: If the request fails
        """
        cache_key = f"{base_id}_{dashboard_id}"
        response = self._http.request(
            'GET',
            f"/base/{base_id}/dashboard/{dashboard_id}"
        )
        
        dashboard = Dashboard.from_api_response(response)
        self._cache.set('dashboards', cache_key, response)
        return dashboard
        
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
        self._http.request(
            'DELETE',
            f"/base/{base_id}/dashboard/{dashboard_id}"
        )
        
        cache_key = f"{base_id}_{dashboard_id}"
        self._cache.delete('dashboards', cache_key)
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
            Dict[str, str]: Updated dashboard info containing:
                - id: Dashboard ID
                - name: New dashboard name
            
        Raises:
            APIError: If the rename fails
        """
        response = self._http.request(
            'PATCH',
            f"/base/{base_id}/dashboard/{dashboard_id}/rename",
            json={'name': name}
        )
        
        cache_key = f"{base_id}_{dashboard_id}"
        self._cache.delete('dashboards', cache_key)
        return Dashboard.from_api_response(response)
        
    def update_dashboard_layout(
        self,
        base_id: str,
        dashboard_id: str,
        layout: List[Dict[str, Any]]
    ) -> Dashboard:
        """
        Update a dashboard's layout.
        
        Args:
            base_id: ID of the base
            dashboard_id: ID of the dashboard
            layout: List of plugin layout configurations, each containing:
                - pluginInstallId: ID of installed plugin
                - x: X coordinate
                - y: Y coordinate
                - w: Width
                - h: Height
            
        Returns:
            Dict[str, Any]: Updated dashboard info containing:
                - id: Dashboard ID
                - layout: New layout configuration
            
        Raises:
            APIError: If the update fails
        """
        response = self._http.request(
            'PATCH',
            f"/base/{base_id}/dashboard/{dashboard_id}/layout",
            json={'layout': layout}
        )
        
        cache_key = f"{base_id}_{dashboard_id}"
        self._cache.delete('dashboards', cache_key)
        return Dashboard.from_api_response(response)
