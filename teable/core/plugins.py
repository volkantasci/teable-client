"""
Plugin management module.

This module handles operations for managing plugins.
"""

from typing import Dict, List, Literal, Optional, TypedDict

from .http import TeableHttpClient

PluginPosition = Literal['dashboard', 'view']
PluginStatus = Literal['developing', 'reviewing', 'published']

class PluginI18nContent(TypedDict):
    """Type definition for plugin i18n content."""
    title: str
    description: str

class PluginUser(TypedDict, total=False):
    """Type definition for plugin user."""
    id: str
    name: str
    email: str
    avatar: Optional[str]

class PluginSecretResponse(TypedDict):
    """Type definition for plugin secret regeneration response."""
    id: str
    secret: str

class AuthCodeRequest(TypedDict):
    """Type definition for auth code request."""
    baseId: str

class AuthCodeResponse(TypedDict):
    """Type definition for auth code response."""
    code: str

class RefreshTokenRequest(TypedDict):
    """Type definition for refresh token request."""
    refreshToken: str
    secret: str

class PluginTokenRequest(TypedDict):
    """Type definition for plugin token request."""
    baseId: str
    secret: str
    scopes: List[str]
    authCode: str

class PluginToken(TypedDict):
    """Type definition for plugin token response."""
    accessToken: str
    refreshToken: str
    scopes: List[str]
    expiresIn: int
    refreshExpiresIn: int

class PluginCreate(TypedDict, total=False):
    """Type definition for plugin creation request."""
    name: str
    description: Optional[str]
    detailDesc: Optional[str]
    logo: str
    url: Optional[str]
    helpUrl: Optional[str]
    positions: List[PluginPosition]
    i18n: Optional[Dict[str, PluginI18nContent]]

class PluginCenterItem(TypedDict, total=False):
    """Type definition for plugin center item."""
    id: str
    name: str
    description: Optional[str]
    detailDesc: Optional[str]
    logo: str
    helpUrl: Optional[str]
    i18n: Dict[str, PluginI18nContent]
    url: Optional[str]
    createdTime: str
    lastModifiedTime: Optional[str]
    createdBy: PluginUser

class Plugin(TypedDict, total=False):
    """Type definition for plugin response."""
    id: str
    name: str
    description: Optional[str]
    detailDesc: Optional[str]
    logo: str
    url: Optional[str]
    helpUrl: Optional[str]
    positions: List[PluginPosition]
    i18n: Dict[str, PluginI18nContent]
    secret: Optional[str]
    status: PluginStatus
    pluginUser: PluginUser
    createdTime: str
    lastModifiedTime: Optional[str]

class PluginManager:
    """
    Handles plugin operations.
    
    This class manages:
    - Plugin registration and listing
    - Plugin configuration and status
    - Plugin localization
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the plugin manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def create_plugin(
        self,
        name: str,
        logo: str,
        positions: List[PluginPosition],
        description: Optional[str] = None,
        detail_desc: Optional[str] = None,
        url: Optional[str] = None,
        help_url: Optional[str] = None,
        i18n: Optional[Dict[str, PluginI18nContent]] = None
    ) -> Plugin:
        """
        Create a new plugin.
        
        Args:
            name: Plugin name (1-20 characters)
            logo: Plugin logo URL
            positions: List of plugin positions ('dashboard' or 'view')
            description: Optional plugin description (max 150 characters)
            detail_desc: Optional detailed description (max 3000 characters)
            url: Optional plugin URL
            help_url: Optional help documentation URL
            i18n: Optional localization content
            
        Returns:
            Plugin: Created plugin information
            
        Raises:
            APIError: If the creation fails
            ValueError: If input validation fails
        """
        if not 1 <= len(name) <= 20:
            raise ValueError("name must be between 1 and 20 characters")
        if description and len(description) > 150:
            raise ValueError("description must not exceed 150 characters")
        if detail_desc and len(detail_desc) > 3000:
            raise ValueError("detail_desc must not exceed 3000 characters")
        if not positions:
            raise ValueError("at least one position must be specified")
            
        data: PluginCreate = {
            'name': name,
            'logo': logo,
            'positions': positions
        }
        
        if description is not None:
            data['description'] = description
        if detail_desc is not None:
            data['detailDesc'] = detail_desc
        if url is not None:
            data['url'] = url
        if help_url is not None:
            data['helpUrl'] = help_url
        if i18n is not None:
            data['i18n'] = i18n
            
        return self._http.request(
            'POST',
            '/plugin',
            json=data
        )
        
    def list_plugins(self) -> List[Plugin]:
        """
        Get list of plugins.
        
        Returns:
            List[Plugin]: List of plugins including:
                - Basic info (id, name, logo, etc.)
                - Configuration (positions, i18n)
                - Status and timestamps
                - Creator information
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/plugin'
        )
        
    def get_plugin(self, plugin_id: str) -> Plugin:
        """
        Get details of a specific plugin.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin: Plugin information including:
                - Basic info (id, name, logo, etc.)
                - Configuration (positions, i18n)
                - Status and timestamps
                - Creator information
                - Secret
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/plugin/{plugin_id}"
        )
        
    def update_plugin(
        self,
        plugin_id: str,
        name: str,
        logo: str,
        positions: List[PluginPosition],
        description: Optional[str] = None,
        detail_desc: Optional[str] = None,
        url: Optional[str] = None,
        help_url: Optional[str] = None,
        i18n: Optional[Dict[str, PluginI18nContent]] = None
    ) -> Plugin:
        """
        Update a plugin.
        
        Args:
            plugin_id: ID of the plugin to update
            name: Plugin name (1-20 characters)
            logo: Plugin logo URL
            positions: List of plugin positions ('dashboard' or 'view')
            description: Optional plugin description (max 150 characters)
            detail_desc: Optional detailed description (max 3000 characters)
            url: Optional plugin URL
            help_url: Optional help documentation URL
            i18n: Optional localization content
            
        Returns:
            Plugin: Updated plugin information
            
        Raises:
            APIError: If the update fails
            ValueError: If input validation fails
        """
        if not 1 <= len(name) <= 20:
            raise ValueError("name must be between 1 and 20 characters")
        if description and len(description) > 150:
            raise ValueError("description must not exceed 150 characters")
        if detail_desc and len(detail_desc) > 3000:
            raise ValueError("detail_desc must not exceed 3000 characters")
        if not positions:
            raise ValueError("at least one position must be specified")
            
        data: PluginCreate = {
            'name': name,
            'logo': logo,
            'positions': positions
        }
        
        if description is not None:
            data['description'] = description
        if detail_desc is not None:
            data['detailDesc'] = detail_desc
        if url is not None:
            data['url'] = url
        if help_url is not None:
            data['helpUrl'] = help_url
        if i18n is not None:
            data['i18n'] = i18n
            
        return self._http.request(
            'PUT',
            f"/plugin/{plugin_id}",
            json=data
        )
        
    def delete_plugin(self, plugin_id: str) -> bool:
        """
        Delete a plugin.
        
        Args:
            plugin_id: ID of the plugin to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/plugin/{plugin_id}"
        )
        return True
        
    def get_auth_code(self, plugin_id: str, base_id: str) -> AuthCodeResponse:
        """
        Get an authorization code for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            base_id: ID of the base
            
        Returns:
            AuthCodeResponse: Auth code information including:
                - code: Authorization code for token requests
            
        Raises:
            APIError: If the request fails
        """
        data: AuthCodeRequest = {
            'baseId': base_id
        }
        
        return self._http.request(
            'POST',
            f"/plugin/{plugin_id}/authCode",
            json=data
        )
        
    def refresh_token(
        self,
        plugin_id: str,
        refresh_token: str,
        secret: str
    ) -> PluginToken:
        """
        Refresh an access token for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            refresh_token: Refresh token from previous token response
            secret: Plugin secret
            
        Returns:
            PluginToken: Token information including:
                - accessToken: New access token for API requests
                - refreshToken: New refresh token
                - scopes: Granted scopes
                - expiresIn: Access token expiration in seconds
                - refreshExpiresIn: Refresh token expiration in seconds
            
        Raises:
            APIError: If the refresh fails
        """
        data: RefreshTokenRequest = {
            'refreshToken': refresh_token,
            'secret': secret
        }
        
        return self._http.request(
            'POST',
            f"/plugin/{plugin_id}/refreshToken",
            json=data
        )
        
    def get_token(
        self,
        plugin_id: str,
        base_id: str,
        secret: str,
        scopes: List[str],
        auth_code: str
    ) -> PluginToken:
        """
        Get an access token for a plugin.
        
        Args:
            plugin_id: ID of the plugin
            base_id: ID of the base
            secret: Plugin secret
            scopes: List of requested scopes
            auth_code: Authorization code
            
        Returns:
            PluginToken: Token information including:
                - accessToken: Access token for API requests
                - refreshToken: Token for refreshing access token
                - scopes: Granted scopes
                - expiresIn: Access token expiration in seconds
                - refreshExpiresIn: Refresh token expiration in seconds
            
        Raises:
            APIError: If the token request fails
        """
        data: PluginTokenRequest = {
            'baseId': base_id,
            'secret': secret,
            'scopes': scopes,
            'authCode': auth_code
        }
        
        return self._http.request(
            'GET',
            f"/plugin/{plugin_id}/token",
            json=data
        )
        
    def regenerate_secret(self, plugin_id: str) -> PluginSecretResponse:
        """
        Regenerate a plugin's secret.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            PluginSecretResponse: New secret information including:
                - id: Plugin identifier
                - secret: New plugin secret
            
        Raises:
            APIError: If the regeneration fails
        """
        return self._http.request(
            'POST',
            f"/plugin/{plugin_id}/regenerate-secret"
        )
        
    def list_plugin_center(self, positions: Optional[List[PluginPosition]] = None) -> List[PluginCenterItem]:
        """
        Get list of plugins from the plugin center.
        
        Args:
            positions: Optional list of positions to filter by ('dashboard' or 'view')
            
        Returns:
            List[PluginCenterItem]: List of plugins including:
                - Basic info (id, name, logo, etc.)
                - Configuration (i18n)
                - Timestamps
                - Creator information
            
        Raises:
            APIError: If the request fails
        """
        params = {}
        if positions:
            params['positions'] = ','.join(positions)
            
        return self._http.request(
            'GET',
            '/plugin/center/list',
            params=params
        )
        
    def submit_plugin(self, plugin_id: str) -> bool:
        """
        Submit a plugin for review.
        
        Args:
            plugin_id: ID of the plugin to submit
            
        Returns:
            bool: True if submission successful
            
        Raises:
            APIError: If the submission fails
        """
        self._http.request(
            'PATCH',
            f"/plugin/{plugin_id}/submit"
        )
        return True
