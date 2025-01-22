"""
OAuth management module.

This module handles operations for managing OAuth applications.
"""

from typing import List, Literal, Optional, TypedDict

from .http import TeableHttpClient

OAuthScope = Literal[
    'table|create', 'table|delete', 'table|export', 'table|import', 'table|read', 'table|update',
    'view|create', 'view|delete', 'view|read', 'view|update',
    'field|create', 'field|delete', 'field|read', 'field|update',
    'record|comment', 'record|create', 'record|delete', 'record|read', 'record|update',
    'automation|create', 'automation|delete', 'automation|read', 'automation|update',
    'user|email_read'
]

class OAuthDecision(TypedDict, total=False):
    """Type definition for OAuth decision response."""
    name: str
    description: Optional[str]
    homepage: str
    logo: Optional[str]
    scopes: Optional[List[str]]

class OAuthClientCreate(TypedDict, total=False):
    """Type definition for OAuth client creation request."""
    name: str
    description: Optional[str]
    homepage: str
    logo: Optional[str]
    scopes: Optional[List[OAuthScope]]
    redirectUris: List[str]

class OAuthAppCreator(TypedDict):
    """Type definition for OAuth app creator user."""
    name: str
    email: str

class AuthorizedOAuthClient(TypedDict, total=False):
    """Type definition for authorized OAuth client."""
    clientId: str
    name: str
    homepage: str
    logo: Optional[str]
    description: Optional[str]
    scopes: Optional[List[str]]
    lastUsedTime: Optional[str]
    createdUser: OAuthAppCreator

class OAuthClientListItem(TypedDict, total=False):
    """Type definition for OAuth client list item."""
    clientId: str
    name: str
    description: Optional[str]
    logo: Optional[str]
    homepage: str

class OAuthClientSecret(TypedDict, total=False):
    """Type definition for OAuth client secret."""
    id: str
    secret: str
    maskedSecret: str
    lastUsedTime: Optional[str]

class OAuthClient(TypedDict, total=False):
    """Type definition for OAuth client."""
    clientId: str
    name: str
    secrets: Optional[List[OAuthClientSecret]]
    scopes: Optional[List[str]]
    logo: Optional[str]
    homepage: str
    redirectUris: List[str]

class OAuthManager:
    """
    Handles OAuth operations.
    
    This class manages:
    - OAuth application registration and listing
    - Client credentials and secrets
    - Application configuration and scopes
    - Redirect URI management
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the OAuth manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def get_client(self, client_id: str) -> OAuthClient:
        """
        Get OAuth client details.
        
        Args:
            client_id: ID of the OAuth client
            
        Returns:
            OAuthClient: Client information including:
                - clientId: Client identifier
                - name: Application name
                - secrets: List of client secrets
                - scopes: List of authorized scopes
                - logo: Application logo URL
                - homepage: Application homepage URL
                - redirectUris: List of authorized redirect URIs
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/oauth/client/{client_id}"
        )
        
    def update_client(
        self,
        client_id: str,
        *,
        name: str,
        homepage: str,
        redirect_uris: List[str],
        secrets: Optional[List[OAuthClientSecret]] = None,
        scopes: Optional[List[str]] = None,
        logo: Optional[str] = None
    ) -> OAuthClient:
        """
        Update OAuth client configuration.
        
        Args:
            client_id: ID of the OAuth client
            name: Application name
            homepage: Application homepage URL
            redirect_uris: List of authorized redirect URIs
            secrets: Optional list of client secrets
            scopes: Optional list of authorized scopes
            logo: Optional application logo URL
            
        Returns:
            OAuthClient: Updated client information
            
        Raises:
            APIError: If the update fails
        """
        data: OAuthClient = {
            'clientId': client_id,
            'name': name,
            'homepage': homepage,
            'redirectUris': redirect_uris
        }
        
        if secrets is not None:
            data['secrets'] = secrets
        if scopes is not None:
            data['scopes'] = scopes
        if logo is not None:
            data['logo'] = logo
            
        return self._http.request(
            'PUT',
            f"/oauth/client/{client_id}",
            json=data
        )
        
    def delete_client(self, client_id: str) -> bool:
        """
        Delete an OAuth client.
        
        Args:
            client_id: ID of the OAuth client to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/oauth/client/{client_id}"
        )
        return True
        
    def list_authorized_clients(self) -> List[AuthorizedOAuthClient]:
        """
        Get list of authorized OAuth applications.
        
        Returns:
            List[AuthorizedOAuthClient]: List of authorized clients including:
                - clientId: Client identifier
                - name: Application name
                - homepage: Application homepage URL
                - logo: Optional application logo URL
                - description: Optional application description
                - scopes: Optional list of authorized scopes
                - lastUsedTime: Optional timestamp of last use
                - createdUser: Information about the app creator
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/oauth/client/authorized/list'
        )
        
    def revoke_access(self, client_id: str) -> bool:
        """
        Revoke access permissions for an OAuth client.
        
        Args:
            client_id: ID of the OAuth client
            
        Returns:
            bool: True if revocation successful
            
        Raises:
            APIError: If the revocation fails
        """
        self._http.request(
            'POST',
            f"/oauth/client/{client_id}/revoke-access"
        )
        return True
        
    def get_decision(self, transaction_id: str) -> OAuthDecision:
        """
        Get OAuth application details for authorization decision.
        
        Args:
            transaction_id: ID of the OAuth transaction
            
        Returns:
            OAuthDecision: Application information including:
                - name: Application name
                - description: Optional application description
                - homepage: Application homepage URL
                - logo: Optional application logo URL
                - scopes: Optional list of requested scopes
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/oauth/decision/{transaction_id}"
        )
        
    def generate_client_secret(self, client_id: str) -> OAuthClientSecret:
        """
        Generate a new OAuth client secret.
        
        Args:
            client_id: ID of the OAuth client
            
        Returns:
            OAuthClientSecret: Generated secret information including:
                - id: Secret identifier
                - secret: The generated secret
                - maskedSecret: Masked version of the secret
                - lastUsedTime: Optional timestamp of last use
            
        Raises:
            APIError: If the generation fails
        """
        return self._http.request(
            'POST',
            f"/oauth/client/{client_id}/secret"
        )
        
    def list_clients(self) -> List[OAuthClientListItem]:
        """
        Get list of OAuth clients.
        
        Returns:
            List[OAuthClientListItem]: List of client information including:
                - clientId: Client identifier
                - name: Application name
                - description: Optional application description
                - logo: Optional application logo URL
                - homepage: Application homepage URL
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/oauth/client'
        )
        
    def create_client(
        self,
        name: str,
        homepage: str,
        redirect_uris: List[str],
        description: Optional[str] = None,
        logo: Optional[str] = None,
        scopes: Optional[List[OAuthScope]] = None
    ) -> OAuthClient:
        """
        Create a new OAuth client.
        
        Args:
            name: Application name
            homepage: Application homepage URL
            redirect_uris: List of authorized redirect URIs
            description: Optional application description
            logo: Optional application logo URL
            scopes: Optional list of authorized scopes
            
        Returns:
            OAuthClient: Created client information
            
        Raises:
            APIError: If the creation fails
        """
        data: OAuthClientCreate = {
            'name': name,
            'homepage': homepage,
            'redirectUris': redirect_uris
        }
        
        if description is not None:
            data['description'] = description
        if logo is not None:
            data['logo'] = logo
        if scopes is not None:
            data['scopes'] = scopes
            
        return self._http.request(
            'POST',
            '/oauth/client',
            json=data
        )
        
    def delete_client_secret(self, client_id: str, secret_id: str) -> bool:
        """
        Delete an OAuth client secret.
        
        Args:
            client_id: ID of the OAuth client
            secret_id: ID of the secret to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        self._http.request(
            'DELETE',
            f"/oauth/client/{client_id}/secret/{secret_id}"
        )
        return True
