"""Plugin Model Module

This module provides the PluginInstallation class for representing
plugin installation data returned by the API.
"""

from dataclasses import dataclass


@dataclass
class PluginInstallation:
    """
    Represents a plugin installation in a view.
    
    Attributes:
        plugin_id: ID of the installed plugin
        plugin_install_id: ID of the plugin installation
        name: Display name of the plugin view
        view_id: ID of the view containing the plugin
    """
    
    plugin_id: str
    plugin_install_id: str
    name: str
    view_id: str
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'PluginInstallation':
        """
        Create a PluginInstallation instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            PluginInstallation: Created instance
        """
        return cls(
            plugin_id=response['pluginId'],
            plugin_install_id=response['pluginInstallId'],
            name=response['name'],
            view_id=response['viewId']
        )
