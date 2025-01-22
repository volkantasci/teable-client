"""
Integrity management module.

This module handles operations for data integrity checks.
"""

from typing import List, Literal, Optional, TypedDict

from .http import TeableHttpClient

LinkIssueType = Literal[
    'ForeignTableNotFound',
    'ForeignKeyNotFound',
    'SelfKeyNotFound',
    'SymmetricFieldNotFound',
    'MissingRecordReference',
    'InvalidLinkReference',
    'ForeignKeyHostTableNotFound'
]

class LinkIssue(TypedDict):
    """Type definition for link issue."""
    type: LinkIssueType
    message: str

class LinkFieldIssue(TypedDict, total=False):
    """Type definition for link field issue."""
    baseId: Optional[str]
    baseName: Optional[str]
    fieldId: str
    fieldName: str
    tableId: str
    tableName: str
    issues: List[LinkIssue]

class IntegrityCheckResponse(TypedDict):
    """Type definition for integrity check response."""
    hasIssues: bool
    linkFieldIssues: List[LinkFieldIssue]

class IntegrityManager:
    """
    Handles integrity operations.
    
    This class manages:
    - Link field integrity checks
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the integrity manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def check_link_integrity(self, base_id: str) -> IntegrityCheckResponse:
        """
        Check integrity of link fields in a base.
        
        Args:
            base_id: ID of the base to check
            
        Returns:
            IntegrityCheckResponse: Check results including:
                - hasIssues: Flag indicating if any issues were found
                - linkFieldIssues: List of issues found in link fields
            
        Raises:
            APIError: If the check fails
        """
        return self._http.request(
            'GET',
            f"/integrity/base/{base_id}/link-check"
        )
        
    def fix_link_integrity(self, base_id: str) -> List[LinkIssue]:
        """
        Fix integrity issues in link fields of a base.
        
        Args:
            base_id: ID of the base to fix
            
        Returns:
            List[LinkIssue]: List of remaining issues that could not be fixed
            
        Raises:
            APIError: If the fix operation fails
        """
        return self._http.request(
            'POST',
            f"/integrity/base/{base_id}/link-fix"
        )
