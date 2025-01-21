"""
Dashboard model module.

This module defines the data model for dashboards.
"""

from typing import Any, Dict, List, Optional

class Dashboard:
    """
    Represents a dashboard in Teable.
    
    A dashboard is a collection of plugins arranged in a grid layout.
    """
    
    def __init__(
        self,
        dashboard_id: str,
        name: str,
        layout: Optional[List[Dict[str, Any]]] = None,
        plugin_map: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        """
        Initialize a dashboard.
        
        Args:
            dashboard_id: Unique identifier for the dashboard
            name: Display name of the dashboard
            layout: Optional list of plugin layout configurations
            plugin_map: Optional mapping of plugin IDs to configurations
        """
        self.dashboard_id = dashboard_id
        self.name = name
        self.layout = layout or []
        self.plugin_map = plugin_map or {}
        
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'Dashboard':
        """
        Create a Dashboard instance from an API response.
        
        Args:
            response: API response data
            
        Returns:
            Dashboard: New dashboard instance
        """
        return cls(
            dashboard_id=response['id'],
            name=response['name'],
            layout=response.get('layout'),
            plugin_map=response.get('pluginMap')
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dashboard to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the dashboard
        """
        data: Dict[str, Any] = {
            'id': self.dashboard_id,
            'name': self.name
        }
        
        if self.layout:
            data['layout'] = self.layout
        if self.plugin_map:
            data['pluginMap'] = self.plugin_map
            
        return data
