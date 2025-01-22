"""
Organization management module.

This module handles operations for managing organizations.
"""

from typing import List, Optional, TypedDict, Dict, Any, Union

from .http import TeableHttpClient

class UserDepartment(TypedDict, total=False):
    """Type definition for user's department info."""
    id: str
    name: str
    path: Optional[List[str]]
    pathName: Optional[List[str]]

class DepartmentUser(TypedDict, total=False):
    """Type definition for department user."""
    id: str
    name: str
    email: str
    avatar: Optional[str]
    departments: Optional[List[UserDepartment]]

class DepartmentUserListResponse(TypedDict):
    """Type definition for department user list response."""
    users: List[DepartmentUser]
    total: int

class Department(TypedDict, total=False):
    """Type definition for department response."""
    id: str
    name: str
    parentId: Optional[str]
    path: Optional[List[str]]
    pathName: Optional[List[str]]
    hasChildren: bool

class Organization(TypedDict):
    """Type definition for organization response."""
    id: str
    name: str
    isAdmin: bool

class OrganizationManager:
    """
    Handles organization operations.
    
    This class manages:
    - Organization information
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the organization manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def get_my_organization(self) -> Optional[Organization]:
        """
        Get current user's organization.
        
        Returns:
            Optional[Organization]: Organization information if exists, None otherwise
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/organization/me'
        )
        
    def list_department_users(
        self,
        organization_id: str,
        *,
        department_id: Optional[str] = None,
        include_children_department: Optional[str] = None,
        skip: Optional[Union[int, str]] = None,
        take: Optional[Union[int, str]] = None,
        search: Optional[str] = None
    ) -> DepartmentUserListResponse:
        """
        Get list of users in a department.
        
        Args:
            organization_id: ID of the organization
            department_id: Optional ID of department to filter by
            include_children_department: Optional flag to include child departments
            skip: Optional number of users to skip
            take: Optional number of users to take
            search: Optional search term to filter users
            
        Returns:
            DepartmentUserListResponse: List response including:
                - users: List of users with their departments
                - total: Total number of users
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        if department_id is not None:
            params['departmentId'] = department_id
        if include_children_department is not None:
            params['includeChildrenDepartment'] = include_children_department
        if skip is not None:
            params['skip'] = skip
        if take is not None:
            params['take'] = take
        if search is not None:
            params['search'] = search
            
        return self._http.request(
            'GET',
            f"/organization/department-user",
            params=params
        )
        
    def list_departments(
        self,
        organization_id: str,
        *,
        parent_id: Optional[str] = None,
        search: Optional[str] = None,
        include_children_department: Optional[str] = None
    ) -> List[Department]:
        """
        Get list of departments in an organization.
        
        Args:
            organization_id: ID of the organization
            parent_id: Optional ID of parent department to filter by
            search: Optional search term to filter departments
            include_children_department: Optional flag to include child departments
            
        Returns:
            List[Department]: List of departments including:
                - Basic info (id, name)
                - Hierarchy info (parentId, path, pathName)
                - hasChildren flag
            
        Raises:
            APIError: If the request fails
        """
        params: Dict[str, Any] = {}
        if parent_id is not None:
            params['parentId'] = parent_id
        if search is not None:
            params['search'] = search
        if include_children_department is not None:
            params['includeChildrenDepartment'] = include_children_department
            
        return self._http.request(
            'GET',
            f"/organization/department",
            params=params
        )
