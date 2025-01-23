"""
Dashboard model module.

This module defines the data model for dashboards.
"""

from typing import Any, Dict, List, Optional, Protocol, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.client import TeableClient

class ClientProtocol(Protocol):
    """Protocol defining the required client interface."""
    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Any: ...

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
        plugin_map: Optional[Dict[str, Dict[str, Any]]] = None,
        _client: Optional[Union['TeableClient', ClientProtocol]] = None
    ):
        """
        Initialize a dashboard.
        
        Args:
            dashboard_id: Unique identifier for the dashboard
            name: Display name of the dashboard
            layout: Optional list of plugin layout configurations
            plugin_map: Optional mapping of plugin IDs to configurations
            _client: Optional client instance for API communication
        """
        self.dashboard_id = dashboard_id
        self.name = name
        self.layout = layout or []
        self.plugin_map = plugin_map or {}
        self._client = _client
        
    @classmethod
    def from_api_response(
        cls,
        response: Dict[str, Any],
        client: Optional[Union['TeableClient', ClientProtocol]] = None
    ) -> 'Dashboard':
        """
        Create a Dashboard instance from an API response.
        
        Args:
            response: API response data
            client: Optional client instance for API communication
            
        Returns:
            Dashboard: New dashboard instance
        """
        return cls(
            dashboard_id=response['id'],
            name=response['name'],
            layout=response.get('layout'),
            plugin_map=response.get('pluginMap'),
            _client=client
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

    def update_layout(self, layout: List[Dict[str, Any]]) -> None:
        """
        Update the dashboard layout.
        
        Args:
            layout: New layout configuration
            
        Raises:
            RuntimeError: If dashboard is not connected to client
            APIError: If the update fails
        """
        if not self._client:
            raise RuntimeError("Dashboard instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'PATCH',
            f"dashboard/{self.dashboard_id}/layout",
            json={'layout': layout}
        )
        self.layout = layout

    def update_plugin_map(self, plugin_map: Dict[str, Dict[str, Any]]) -> None:
        """
        Update the dashboard plugin configurations.
        
        Args:
            plugin_map: New plugin configurations
            
        Raises:
            RuntimeError: If dashboard is not connected to client
            APIError: If the update fails
        """
        if not self._client:
            raise RuntimeError("Dashboard instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'PATCH',
            f"dashboard/{self.dashboard_id}/plugin-map",
            json={'pluginMap': plugin_map}
        )
        self.plugin_map = plugin_map

    def delete(self) -> bool:
        """
        Delete this dashboard.
        
        Returns:
            bool: True if deletion successful
            
        Raises:
            RuntimeError: If dashboard is not connected to client
            APIError: If the deletion fails
        """
        if not self._client:
            raise RuntimeError("Dashboard instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'DELETE',
            f"dashboard/{self.dashboard_id}"
        )
        return True
