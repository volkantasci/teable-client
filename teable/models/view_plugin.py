"""
View plugin model module.

This module defines the data model for view plugins.
"""

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

def _validate_url(url: str) -> None:
    """Validate URL format."""
    if not isinstance(url, str):
        raise ValidationError("URL must be a string")
    if not url.startswith(('http://', 'https://')):
        raise ValidationError("URL must start with http:// or https://")

def _validate_storage(storage: Dict[str, Any]) -> None:
    """Validate storage data."""
    if not isinstance(storage, dict):
        raise ValidationError("Storage must be a dictionary")

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
        storage: Optional[Dict[str, Any]] = None,
        _client: Optional[Union['TeableClient', ClientProtocol]] = None
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
            _client: Optional client instance for API communication
            
        Raises:
            ValidationError: If input validation fails
        """
        _validate_plugin_id(plugin_id)
        _validate_plugin_install_id(plugin_install_id)
        _validate_name(name)
        if url is not None:
            _validate_url(url)
        if storage is not None:
            _validate_storage(storage)
            
        self.plugin_id = plugin_id
        self.plugin_install_id = plugin_install_id
        self.name = name
        self.base_id = base_id
        self.url = url
        self.storage = storage or {}
        self._client = _client
        
    @classmethod
    def from_api_response(
        cls,
        response: Dict[str, Any],
        client: Optional[Union['TeableClient', ClientProtocol]] = None
    ) -> 'ViewPlugin':
        """
        Create a ViewPlugin instance from an API response.
        
        Args:
            response: API response data
            client: Optional client instance for API communication
            
        Returns:
            ViewPlugin: New view plugin instance
            
        Raises:
            ValidationError: If input validation fails
        """
        if not isinstance(response, dict):
            raise ValidationError("Response must be a dictionary")
        if not all(k in response for k in ('pluginId', 'pluginInstallId', 'name')):
            raise ValidationError("Response must contain 'pluginId', 'pluginInstallId', and 'name'")
            
        return cls(
            plugin_id=response['pluginId'],
            plugin_install_id=response['pluginInstallId'],
            name=response['name'],
            base_id=response.get('baseId'),
            url=response.get('url'),
            storage=response.get('storage'),
            _client=client
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

    def update_storage(self, storage: Dict[str, Any]) -> None:
        """
        Update the plugin's storage data.
        
        Args:
            storage: New storage data
            
        Raises:
            RuntimeError: If plugin is not connected to client
            ValidationError: If input validation fails
            APIError: If the update fails
        """
        if not self._client:
            raise RuntimeError("Plugin instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        _validate_storage(storage)
            
        self._client._make_request(
            'PATCH',
            f"view/plugin/{self.plugin_install_id}/storage",
            json={'storage': storage}
        )
        self.storage = storage

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
            raise RuntimeError("Plugin instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'DELETE',
            f"view/plugin/{self.plugin_install_id}"
        )
        return True
