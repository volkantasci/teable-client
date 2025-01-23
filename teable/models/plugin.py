"""Plugin Model Module

This module provides the PluginInstallation class for representing
plugin installation data returned by the API.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Union, TYPE_CHECKING

from ..exceptions import ValidationError

if TYPE_CHECKING:
    from ..core.client import TeableClient

class ClientProtocol(Protocol):
    """Protocol defining the required client interface."""
    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Any: ...

def _validate_plugin_id(plugin_id: str) -> None:
    """Validate plugin ID."""
    if not isinstance(plugin_id, str) or not plugin_id:
        raise ValidationError("Plugin ID must be a non-empty string")

def _validate_plugin_install_id(plugin_install_id: str) -> None:
    """Validate plugin installation ID."""
    if not isinstance(plugin_install_id, str) or not plugin_install_id:
        raise ValidationError("Plugin installation ID must be a non-empty string")

def _validate_name(name: str) -> None:
    """Validate plugin name."""
    if not isinstance(name, str):
        raise ValidationError("Plugin name must be a string")
    if not name.strip():
        raise ValidationError("Plugin name cannot be empty")
    if len(name) > 255:
        raise ValidationError("Plugin name cannot exceed 255 characters")

def _validate_view_id(view_id: str) -> None:
    """Validate view ID."""
    if not isinstance(view_id, str) or not view_id:
        raise ValidationError("View ID must be a non-empty string")

@dataclass
class PluginInstallation:
    """
    Represents a plugin installation in a view.
    
    Attributes:
        plugin_id: ID of the installed plugin
        plugin_install_id: ID of the plugin installation
        name: Display name of the plugin view
        view_id: ID of the view containing the plugin
        _client: Optional client instance for API communication
    """
    
    plugin_id: str
    plugin_install_id: str
    name: str
    view_id: str
    _client: Optional[Union['TeableClient', ClientProtocol]] = None
    
    def __post_init__(self):
        """Validate attributes after initialization."""
        _validate_plugin_id(self.plugin_id)
        _validate_plugin_install_id(self.plugin_install_id)
        _validate_name(self.name)
        _validate_view_id(self.view_id)
    
    @classmethod
    def from_api_response(
        cls,
        response: Dict[str, Any],
        client: Optional[Union['TeableClient', ClientProtocol]] = None
    ) -> 'PluginInstallation':
        """
        Create a PluginInstallation instance from API response data.
        
        Args:
            response: API response dictionary
            client: Optional client instance for API communication
            
        Returns:
            PluginInstallation: Created instance
            
        Raises:
            ValidationError: If input validation fails
        """
        if not isinstance(response, dict):
            raise ValidationError("Response must be a dictionary")
        if not all(k in response for k in ('pluginId', 'pluginInstallId', 'name', 'viewId')):
            raise ValidationError("Response must contain 'pluginId', 'pluginInstallId', 'name', and 'viewId'")
            
        return cls(
            plugin_id=response['pluginId'],
            plugin_install_id=response['pluginInstallId'],
            name=response['name'],
            view_id=response['viewId'],
            _client=client
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format for API requests.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            'pluginId': self.plugin_id,
            'pluginInstallId': self.plugin_install_id,
            'name': self.name,
            'viewId': self.view_id
        }

    def delete(self) -> bool:
        """
        Delete this plugin installation.
        
        Returns:
            bool: True if deletion successful
            
        Raises:
            RuntimeError: If plugin is not connected to client
            APIError: If the deletion fails
        """
        if not self._client:
            raise RuntimeError("Plugin installation not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'DELETE',
            f"view/{self.view_id}/plugin/{self.plugin_install_id}"
        )
        return True
