"""Dashboard Model Module

This module provides the Dashboard class for representing
dashboard data returned by the API.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class DashboardLayout:
    """
    Represents a dashboard widget layout.
    
    Attributes:
        plugin_install_id: ID of the installed plugin
        x: X coordinate of the widget
        y: Y coordinate of the widget
        w: Width of the widget
        h: Height of the widget
    """
    
    plugin_install_id: str
    x: float
    y: float
    w: float
    h: float
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'DashboardLayout':
        """
        Create a DashboardLayout instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            DashboardLayout: Created instance
        """
        return cls(
            plugin_install_id=response['pluginInstallId'],
            x=response['x'],
            y=response['y'],
            w=response['w'],
            h=response['h']
        )


@dataclass
class DashboardPlugin:
    """
    Represents a plugin installed in a dashboard.
    
    Attributes:
        id: ID of the plugin installation
        plugin_id: ID of the plugin
        plugin_install_id: ID of the plugin installation
        base_id: ID of the base
        name: Display name of the plugin
        url: Optional URL for the plugin
        storage: Optional storage data
    """
    
    id: str
    plugin_id: str
    plugin_install_id: str
    base_id: str
    name: str
    url: Optional[str] = None
    storage: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'DashboardPlugin':
        """
        Create a DashboardPlugin instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            DashboardPlugin: Created instance
        """
        return cls(
            id=response['id'],
            plugin_id=response['pluginId'],
            plugin_install_id=response['pluginInstallId'],
            base_id=response['baseId'],
            name=response['name'],
            url=response.get('url'),
            storage=response.get('storage')
        )


@dataclass
class Dashboard:
    """
    Represents a dashboard in a base.
    
    Attributes:
        id: Unique identifier for the dashboard
        name: Display name of the dashboard
        layout: Optional list of widget layouts
        plugin_map: Optional mapping of plugin IDs to plugin details
    """
    
    id: str
    name: str
    layout: Optional[List[DashboardLayout]] = None
    plugin_map: Optional[Dict[str, DashboardPlugin]] = None
    
    @classmethod
    def from_api_response(cls, response: dict) -> 'Dashboard':
        """
        Create a Dashboard instance from API response data.
        
        Args:
            response: API response dictionary
            
        Returns:
            Dashboard: Created instance
        """
        layout = None
        if 'layout' in response:
            layout = [DashboardLayout.from_api_response(l) for l in response['layout']]
            
        plugin_map = None
        if 'pluginMap' in response:
            plugin_map = {
                k: DashboardPlugin.from_api_response(v)
                for k, v in response['pluginMap'].items()
            }
            
        return cls(
            id=response['id'],
            name=response['name'],
            layout=layout,
            plugin_map=plugin_map
        )
