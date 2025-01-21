"""
View plugin model module.

This module defines the data model for view plugins.
"""

from typing import Any, Dict, Optional

class ViewPlugin:
    """
    Represents a plugin installed in a view.
    """
    
    def __init__(
        self,
        plugin_id: str,
        plugin_install_id: str,
        name: str,
        base_id: Optional[str] = None,
        url: Optional[str] = None,
        storage: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a view plugin.
        
        Args:
            plugin_id: ID of the plugin
            plugin_install_id: ID of the plugin installation
            name: Display name of the plugin
            base_id: Optional ID of the base
            url: Optional URL for the plugin
            storage: Optional plugin storage data
        """
        self.plugin_id = plugin_id
        self.plugin_install_id = plugin_install_id
        self.name = name
        self.base_id = base_id
        self.url = url
        self.storage = storage or {}
        
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'ViewPlugin':
        """
        Create a ViewPlugin instance from an API response.
        
        Args:
            response: API response data
            
        Returns:
            ViewPlugin: New view plugin instance
        """
        return cls(
            plugin_id=response['pluginId'],
            plugin_install_id=response['pluginInstallId'],
            name=response['name'],
            base_id=response.get('baseId'),
            url=response.get('url'),
            storage=response.get('storage')
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the view plugin to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the view plugin
        """
        data: Dict[str, Any] = {
            'pluginId': self.plugin_id,
            'pluginInstallId': self.plugin_install_id,
            'name': self.name
        }
        
        if self.base_id:
            data['baseId'] = self.base_id
        if self.url:
            data['url'] = self.url
        if self.storage:
            data['storage'] = self.storage
            
        return data
