"""
Admin management module.

This module handles operations for managing instance-wide admin settings.
"""

from typing import List, Literal, Optional, TypedDict

from .http import TeableHttpClient

class PublicLlmProvider(TypedDict):
    """Type definition for public LLM provider information."""
    type: Literal['openai', 'anthropic', 'google', 'azure', 'cohere', 'mistral']
    name: str
    models: Optional[str]

class PublicAiConfig(TypedDict):
    """Type definition for public AI configuration."""
    enable: bool
    llmProviders: List[PublicLlmProvider]

class PublicAdminSettings(TypedDict):
    """Type definition for public admin settings."""
    instanceId: str
    disallowSignUp: Optional[bool]
    disallowSpaceCreation: Optional[bool]
    disallowSpaceInvitation: Optional[bool]
    enableEmailVerification: Optional[bool]
    aiConfig: Optional[PublicAiConfig]

class LlmProvider(TypedDict, total=False):
    """Type definition for LLM provider configuration."""
    type: Literal['openai', 'anthropic', 'google', 'azure', 'cohere', 'mistral']
    name: str
    apiKey: Optional[str]
    baseUrl: Optional[str]
    models: Optional[str]

class AiConfig(TypedDict, total=False):
    """Type definition for AI configuration."""
    enable: bool
    llmProviders: List[LlmProvider]
    embeddingModel: Optional[str]
    translationModel: Optional[str]
    codingModel: Optional[str]

class AdminSettings(TypedDict, total=False):
    """Type definition for admin settings."""
    instanceId: str
    disallowSignUp: Optional[bool]
    disallowSpaceCreation: Optional[bool]
    disallowSpaceInvitation: Optional[bool]
    enableEmailVerification: Optional[bool]
    aiConfig: Optional[AiConfig]

class AdminSettingsUpdate(TypedDict, total=False):
    """Type definition for admin settings update request."""
    disallowSignUp: bool
    disallowSpaceCreation: bool
    disallowSpaceInvitation: bool
    enableEmailVerification: bool
    aiConfig: AiConfig

class AdminManager:
    """
    Handles admin operations.
    
    This class manages:
    - Instance settings and configuration
    - Public and private settings
    - Plugin administration
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the admin manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def get_settings(self) -> AdminSettings:
        """
        Get instance settings.
        
        Returns:
            AdminSettings: Instance settings including:
                - instanceId: Instance identifier
                - disallowSignUp: Whether to disable sign ups
                - disallowSpaceCreation: Whether to disable space creation
                - disallowSpaceInvitation: Whether to disable space invitations
                - enableEmailVerification: Whether to enable email verification
                - aiConfig: AI feature configuration
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/admin/setting'
        )
        
    def update_settings(
        self,
        *,
        disallow_signup: Optional[bool] = None,
        disallow_space_creation: Optional[bool] = None,
        disallow_space_invitation: Optional[bool] = None,
        enable_email_verification: Optional[bool] = None,
        ai_config: Optional[AiConfig] = None
    ) -> bool:
        """
        Update instance settings.
        
        Args:
            disallow_signup: Whether to disable sign ups
            disallow_space_creation: Whether to disable space creation
            disallow_space_invitation: Whether to disable space invitations
            enable_email_verification: Whether to enable email verification
            ai_config: AI feature configuration
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        data: AdminSettingsUpdate = {}
        
        if disallow_signup is not None:
            data['disallowSignUp'] = disallow_signup
        if disallow_space_creation is not None:
            data['disallowSpaceCreation'] = disallow_space_creation
        if disallow_space_invitation is not None:
            data['disallowSpaceInvitation'] = disallow_space_invitation
        if enable_email_verification is not None:
            data['enableEmailVerification'] = enable_email_verification
        if ai_config is not None:
            data['aiConfig'] = ai_config
            
        self._http.request(
            'PATCH',
            '/admin/setting',
            json=data
        )
        return True
        
    def get_public_settings(self) -> PublicAdminSettings:
        """
        Get public instance settings.
        
        Returns:
            PublicAdminSettings: Public instance settings including:
                - instanceId: Instance identifier
                - disallowSignUp: Whether sign ups are disabled
                - disallowSpaceCreation: Whether space creation is disabled
                - disallowSpaceInvitation: Whether space invitations are disabled
                - enableEmailVerification: Whether email verification is enabled
                - aiConfig: Public AI feature configuration
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/admin/setting/public'
        )
        
    def publish_plugin(self, plugin_id: str) -> bool:
        """
        Publish a plugin.
        
        Args:
            plugin_id: ID of the plugin to publish
            
        Returns:
            bool: True if publish successful
            
        Raises:
            APIError: If the publish fails
        """
        self._http.request(
            'PATCH',
            f"/admin/plugin/{plugin_id}/publish"
        )
        return True
