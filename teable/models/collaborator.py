"""
Collaborator Models Module

This module defines the collaborator-related models for the Teable API client.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from .space import SpaceRole


class PrincipalType(str, Enum):
    """Enumeration of principal types."""
    USER = "user"
    DEPARTMENT = "department"


class ResourceType(str, Enum):
    """Enumeration of resource types."""
    SPACE = "space"
    BASE = "base"


@dataclass
class Base:
    """
    Represents a base in Teable.
    
    Attributes:
        base_id (str): Unique identifier for the base
        name (str): Display name of the base
    """
    base_id: str
    name: str

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Base':
        """Create a Base instance from API response data."""
        return cls(
            base_id=data['id'],
            name=data['name']
        )


@dataclass
class UserCollaborator:
    """
    Represents a user collaborator in a space.
    
    Attributes:
        user_id (str): Unique identifier for the user
        user_name (str): Display name of the user
        email (str): Email address of the user
        role (SpaceRole): User's role in the space
        avatar (Optional[str]): URL to user's avatar
        created_time (datetime): When the collaboration was created
        type (PrincipalType): Always USER for this class
        resource_type (ResourceType): Type of resource being collaborated on
        is_system (bool): Whether this is a system user
        base (Optional[Base]): Associated base if any
    """
    user_id: str
    user_name: str
    email: str
    role: SpaceRole
    avatar: Optional[str]
    created_time: datetime
    type: PrincipalType = PrincipalType.USER
    resource_type: ResourceType = ResourceType.SPACE
    is_system: bool = False
    base: Optional[Base] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'UserCollaborator':
        """Create a UserCollaborator instance from API response data."""
        return cls(
            user_id=data['userId'],
            user_name=data['userName'],
            email=data['email'],
            role=SpaceRole(data['role']),
            avatar=data['avatar'],
            created_time=datetime.fromisoformat(data['createdTime'].replace('Z', '+00:00')),
            type=PrincipalType(data['type']),
            resource_type=ResourceType(data['resourceType']),
            is_system=data.get('isSystem', False),
            base=Base.from_api_response(data['base']) if 'base' in data else None
        )


@dataclass
class DepartmentCollaborator:
    """
    Represents a department collaborator in a space.
    
    Attributes:
        department_id (str): Unique identifier for the department
        department_name (str): Display name of the department
        role (SpaceRole): Department's role in the space
        created_time (datetime): When the collaboration was created
        type (PrincipalType): Always DEPARTMENT for this class
        resource_type (ResourceType): Type of resource being collaborated on
        base (Optional[Base]): Associated base if any
    """
    department_id: str
    department_name: str
    role: SpaceRole
    created_time: datetime
    type: PrincipalType = PrincipalType.DEPARTMENT
    resource_type: ResourceType = ResourceType.SPACE
    base: Optional[Base] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'DepartmentCollaborator':
        """Create a DepartmentCollaborator instance from API response data."""
        return cls(
            department_id=data['departmentId'],
            department_name=data['departmentName'],
            role=SpaceRole(data['role']),
            created_time=datetime.fromisoformat(data['createdTime'].replace('Z', '+00:00')),
            type=PrincipalType(data['type']),
            resource_type=ResourceType(data['resourceType']),
            base=Base.from_api_response(data['base']) if 'base' in data else None
        )


Collaborator = Union[UserCollaborator, DepartmentCollaborator]


def collaborator_from_api_response(data: Dict[str, Any], client: Any = None) -> Collaborator:
    """
    Create a Collaborator instance from API response data.
    
    Args:
        data: Dictionary containing collaborator data from API
        client: Optional client instance for API communication
        
    Returns:
        Collaborator: Either UserCollaborator or DepartmentCollaborator
    """
    if data['type'] == PrincipalType.USER:
        return UserCollaborator.from_api_response(data)
    else:
        return DepartmentCollaborator.from_api_response(data)
