"""
Usage management module.

This module handles operations for retrieving usage information.
"""

from typing import Literal, TypedDict

from .http import TeableHttpClient

class UsageLimits(TypedDict):
    """Type definition for usage limits."""
    maxRows: int
    maxSizeAttachments: int
    maxNumDatabaseConnections: int
    maxRevisionHistoryDays: int
    maxAutomationHistoryDays: int
    automationEnable: bool
    auditLogEnable: bool
    adminPanelEnable: bool
    rowColoringEnable: bool
    buttonFieldEnable: bool
    userGroupEnable: bool
    advancedExtensionsEnable: bool
    advancedPermissionsEnable: bool
    passwordRestrictedSharesEnable: bool
    authenticationEnable: bool
    domainVerificationEnable: bool
    organizationEnable: bool

class SpaceUsage(TypedDict):
    """Type definition for space usage information."""
    level: Literal['free', 'plus', 'pro', 'enterprise']
    limit: UsageLimits

class UsageManager:
    """
    Handles usage operations.
    
    This class manages:
    - Space, base, and instance usage information
    - Feature limits and quotas
    - Subscription level tracking
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the usage manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def get_space_usage(self, space_id: str) -> SpaceUsage:
        """
        Get usage information for a space.
        
        Args:
            space_id: ID of the space to get usage for
            
        Returns:
            SpaceUsage: Usage information including:
                - level: Subscription level
                - limit: Feature limits including:
                    - maxRows: Maximum number of rows
                    - maxSizeAttachments: Maximum attachment size
                    - maxNumDatabaseConnections: Maximum database connections
                    - maxRevisionHistoryDays: Maximum revision history days
                    - maxAutomationHistoryDays: Maximum automation history days
                    - automationEnable: Whether automation is enabled
                    - auditLogEnable: Whether audit logging is enabled
                    - adminPanelEnable: Whether admin panel is enabled
                    - rowColoringEnable: Whether row coloring is enabled
                    - buttonFieldEnable: Whether button fields are enabled
                    - userGroupEnable: Whether user groups are enabled
                    - advancedExtensionsEnable: Whether advanced extensions are enabled
                    - advancedPermissionsEnable: Whether advanced permissions are enabled
                    - passwordRestrictedSharesEnable: Whether password shares are enabled
                    - authenticationEnable: Whether authentication is enabled
                    - domainVerificationEnable: Whether domain verification is enabled
                    - organizationEnable: Whether organization features are enabled
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/space/{space_id}/usage"
        )
        
    def get_instance_usage(self) -> SpaceUsage:
        """
        Get usage information for the entire instance.
        
        Returns:
            SpaceUsage: Usage information including:
                - level: Instance subscription level
                - limit: Feature limits including:
                    - maxRows: Maximum number of rows
                    - maxSizeAttachments: Maximum attachment size
                    - maxNumDatabaseConnections: Maximum database connections
                    - maxRevisionHistoryDays: Maximum revision history days
                    - maxAutomationHistoryDays: Maximum automation history days
                    - automationEnable: Whether automation is enabled
                    - auditLogEnable: Whether audit logging is enabled
                    - adminPanelEnable: Whether admin panel is enabled
                    - rowColoringEnable: Whether row coloring is enabled
                    - buttonFieldEnable: Whether button fields are enabled
                    - userGroupEnable: Whether user groups are enabled
                    - advancedExtensionsEnable: Whether advanced extensions are enabled
                    - advancedPermissionsEnable: Whether advanced permissions are enabled
                    - passwordRestrictedSharesEnable: Whether password shares are enabled
                    - authenticationEnable: Whether authentication is enabled
                    - domainVerificationEnable: Whether domain verification is enabled
                    - organizationEnable: Whether organization features are enabled
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/instance/usage'
        )
        
    def get_base_usage(self, base_id: str) -> SpaceUsage:
        """
        Get usage information for a base.
        
        Args:
            base_id: ID of the base to get usage for
            
        Returns:
            SpaceUsage: Usage information including:
                - level: Base subscription level
                - limit: Feature limits including:
                    - maxRows: Maximum number of rows
                    - maxSizeAttachments: Maximum attachment size
                    - maxNumDatabaseConnections: Maximum database connections
                    - maxRevisionHistoryDays: Maximum revision history days
                    - maxAutomationHistoryDays: Maximum automation history days
                    - automationEnable: Whether automation is enabled
                    - auditLogEnable: Whether audit logging is enabled
                    - adminPanelEnable: Whether admin panel is enabled
                    - rowColoringEnable: Whether row coloring is enabled
                    - buttonFieldEnable: Whether button fields are enabled
                    - userGroupEnable: Whether user groups are enabled
                    - advancedExtensionsEnable: Whether advanced extensions are enabled
                    - advancedPermissionsEnable: Whether advanced permissions are enabled
                    - passwordRestrictedSharesEnable: Whether password shares are enabled
                    - authenticationEnable: Whether authentication is enabled
                    - domainVerificationEnable: Whether domain verification is enabled
                    - organizationEnable: Whether organization features are enabled
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/base/{base_id}/usage"
        )
