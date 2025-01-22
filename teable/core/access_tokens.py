"""
Access token management module.

This module handles operations for managing API access tokens.
"""

from typing import List, Optional, TypedDict

from .http import TeableHttpClient

class RefreshedToken(TypedDict):
    """Type definition for refreshed token response."""
    id: str
    expiredTime: str
    token: str

class AccessTokenUpdate(TypedDict, total=False):
    """Type definition for access token update request."""
    name: str
    description: Optional[str]
    scopes: List[str]
    spaceIds: Optional[List[str]]
    baseIds: Optional[List[str]]

class AccessTokenCreate(TypedDict, total=False):
    """Type definition for access token creation request."""
    name: str
    description: Optional[str]
    scopes: List[str]
    spaceIds: Optional[List[str]]
    baseIds: Optional[List[str]]
    expiredTime: str

class AccessToken(TypedDict, total=False):
    """Type definition for access token response."""
    id: str
    name: str
    description: Optional[str]
    scopes: List[str]
    spaceIds: Optional[List[str]]
    baseIds: Optional[List[str]]
    expiredTime: str
    token: Optional[str]  # Only present in create response
    createdTime: str
    lastUsedTime: Optional[str]

class AccessTokenManager:
    """
    Handles access token operations.
    
    This class manages:
    - Access token creation and deletion
    - Access token listing and retrieval
    - Access token updates and refreshing
    - Access token configuration
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the access token manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def create_access_token(
        self,
        name: str,
        scopes: List[str],
        expired_time: str,
        *,
        description: Optional[str] = None,
        space_ids: Optional[List[str]] = None,
        base_ids: Optional[List[str]] = None
    ) -> AccessToken:
        """
        Create a new access token.
        
        Args:
            name: Name for the access token
            scopes: List of permission scopes
            expired_time: Expiration date (e.g. '2024-03-25')
            description: Optional description
            space_ids: Optional list of space IDs to restrict access to
            base_ids: Optional list of base IDs to restrict access to
            
        Returns:
            AccessToken: Created access token information including:
                - id: Token ID
                - name: Token name
                - description: Token description (if provided)
                - scopes: Permission scopes
                - spaceIds: Restricted space IDs (if provided)
                - baseIds: Restricted base IDs (if provided)
                - expiredTime: Expiration date
                - token: The actual access token string
                - createdTime: Creation timestamp
                - lastUsedTime: Last usage timestamp
            
        Raises:
            APIError: If the creation fails
            ValueError: If name is empty or scopes list is empty
        """
        if not name:
            raise ValueError("Name cannot be empty")
        if not scopes:
            raise ValueError("At least one scope must be provided")
            
        data: AccessTokenCreate = {
            'name': name,
            'scopes': scopes,
            'expiredTime': expired_time
        }
        
        if description is not None:
            data['description'] = description
        if space_ids is not None:
            data['spaceIds'] = space_ids
        if base_ids is not None:
            data['baseIds'] = base_ids
            
        return self._http.request(
            'POST',
            '/access-token',
            json=data
        )
        
    def list_access_tokens(self) -> List[AccessToken]:
        """
        List all access tokens.
        
        Returns:
            List[AccessToken]: List of access tokens, each containing:
                - id: Token ID
                - name: Token name
                - description: Token description (if provided)
                - scopes: Permission scopes
                - spaceIds: Restricted space IDs (if provided)
                - baseIds: Restricted base IDs (if provided)
                - expiredTime: Expiration date
                - createdTime: Creation timestamp
                - lastUsedTime: Last usage timestamp (if used)
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/access-token'
        )
        
    def refresh_access_token(
        self,
        token_id: str,
        expired_time: str
    ) -> RefreshedToken:
        """
        Refresh an access token with a new expiration time.
        
        Args:
            token_id: ID of the token to refresh
            expired_time: New expiration date (e.g. '2024-03-25')
            
        Returns:
            RefreshedToken: Refreshed token information including:
                - id: Token ID
                - expiredTime: New expiration date
                - token: The new access token string
            
        Raises:
            APIError: If the refresh fails
        """
        return self._http.request(
            'POST',
            f"/access-token/{token_id}/refresh",
            json={'expiredTime': expired_time}
        )
        
    def get_access_token(self, token_id: str) -> AccessToken:
        """
        Get information about a specific access token.
        
        Args:
            token_id: ID of the token to get
            
        Returns:
            AccessToken: Token information including:
                - id: Token ID
                - name: Token name
                - description: Token description (if provided)
                - scopes: Permission scopes
                - spaceIds: Restricted space IDs (if provided)
                - baseIds: Restricted base IDs (if provided)
                - expiredTime: Expiration date
                - createdTime: Creation timestamp
                - lastUsedTime: Last usage timestamp (if used)
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/access-token/{token_id}"
        )
        
    def update_access_token(
        self,
        token_id: str,
        name: str,
        scopes: List[str],
        *,
        description: Optional[str] = None,
        space_ids: Optional[List[str]] = None,
        base_ids: Optional[List[str]] = None
    ) -> AccessToken:
        """
        Update an access token's configuration.
        
        Args:
            token_id: ID of the token to update
            name: New name for the token
            scopes: New list of permission scopes
            description: Optional new description
            space_ids: Optional new list of space IDs to restrict access to
            base_ids: Optional new list of base IDs to restrict access to
            
        Returns:
            AccessToken: Updated token information including:
                - id: Token ID
                - name: Token name
                - description: Token description (if provided)
                - scopes: Permission scopes
                - spaceIds: Restricted space IDs (if provided)
                - baseIds: Restricted base IDs (if provided)
            
        Raises:
            APIError: If the update fails
            ValueError: If name is empty or scopes list is empty
        """
        if not name:
            raise ValueError("Name cannot be empty")
        if not scopes:
            raise ValueError("At least one scope must be provided")
            
        data: AccessTokenUpdate = {
            'name': name,
            'scopes': scopes
        }
        
        if description is not None:
            data['description'] = description
        if space_ids is not None:
            data['spaceIds'] = space_ids
        if base_ids is not None:
            data['baseIds'] = base_ids
            
        return self._http.request(
            'PUT',
            f"/access-token/{token_id}",
            json=data
        )
        
    def delete_access_token(self, token_id: str) -> bool:
        """
        Delete an access token.
        
        Args:
            token_id: ID of the token to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/access-token/{token_id}"
        )
        return True
