"""
Dashboard plugin model module.

This module defines the data model for dashboard plugins.
"""

from typing import Any, Dict, Optional

class DashboardPlugin:
    """
    Represents a plugin installed in a dashboard.
    """
    
    def __init__(
        self,
        plugin_id: str,
        plugin_install_id: str,
        name: str,
        base_id: Optional[str] = None,
        storage: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a dashboard plugin.
        
        Args:
            plugin_id: ID of the plugin
            plugin_install_id: ID of the plugin installation
            name: Display name of the plugin
            base_id: Optional ID of the base
            storage: Optional plugin storage data
        """
        self.plugin_id = plugin_id
        self.plugin_install_id = plugin_install_id
        self.name = name
        self.base_id = base_id
        self.storage = storage or {}
        
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'DashboardPlugin':
        """
        Create a DashboardPlugin instance from an API response.
        
        Args:
            response: API response data
            
        Returns:
            DashboardPlugin: New dashboard plugin instance
        """
        return cls(
            plugin_id=response['pluginId'],
            plugin_install_id=response['pluginInstallId'],
            name=response['name'],
            base_id=response.get('baseId'),
            storage=response.get('storage')
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dashboard plugin to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the dashboard plugin
        """
        data: Dict[str, Any] = {
            'pluginId': self.plugin_id,
            'pluginInstallId': self.plugin_install_id,
            'name': self.name
        }
        
        if self.base_id:
            data['baseId'] = self.base_id
        if self.storage:
            data['storage'] = self.storage
            
        return data
