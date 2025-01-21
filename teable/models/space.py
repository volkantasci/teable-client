"""
Space Models Module

This module defines the space-related models and operations for the Teable API client.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Base
    from .invitation import Invitation
    from .collaborator import Collaborator, PrincipalType


class SpaceRole(str, Enum):
    """Enumeration of possible roles in a space."""
    OWNER = "owner"
    CREATOR = "creator"
    EDITOR = "editor"
    COMMENTER = "commenter"
    VIEWER = "viewer"


@dataclass
class Organization:
    """
    Represents an organization in Teable.
    
    Attributes:
        org_id (str): Unique identifier for the organization
        name (str): Display name of the organization
    """
    org_id: str
    name: str

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'Organization':
        """
        Create an Organization instance from API response data.
        
        Args:
            data: Dictionary containing organization data from API
            
        Returns:
            Organization: New organization instance
        """
        return cls(
            org_id=data['id'],
            name=data['name']
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert organization to dictionary format for API requests.
        
        Returns:
            dict: Organization data as dictionary
        """
        return {
            'id': self.org_id,
            'name': self.name
        }


@dataclass
class Space:
    """
    Represents a space in Teable.
    
    A space is a container for tables and other resources.
    
    Attributes:
        space_id (str): Unique identifier for the space
        name (str): Display name of the space
        role (SpaceRole): User's role in the space
        organization (Optional[Organization]): Associated organization
        _client: TeableClient instance for API communication
    """
    space_id: str
    name: str
    role: SpaceRole
    organization: Optional[Organization] = None
    _client: Any = None  # Avoid circular import with TeableClient

    @classmethod
    def from_api_response(
        cls,
        data: Dict[str, Any],
        client: Any = None
    ) -> 'Space':
        """
        Create a Space instance from API response data.
        
        Args:
            data: Dictionary containing space data from API
            client: Optional TeableClient instance for API communication
            
        Returns:
            Space: New space instance
        """
        return cls(
            space_id=data['id'],
            name=data['name'],
            role=SpaceRole(data['role']),
            organization=Organization.from_api_response(data['organization'])
            if 'organization' in data else None,
            _client=client
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert space to dictionary format for API requests.
        
        Returns:
            dict: Space data as dictionary
        """
        data: Dict[str, Any] = {
            'id': self.space_id,
            'name': self.name,
            'role': self.role.value
        }
        
        if self.organization:
            data['organization'] = {
                'id': self.organization.org_id,
                'name': self.organization.name
            }
            
        return data

    def update(self, name: str) -> 'Space':
        """
        Update the space's information.
        
        Args:
            name: New display name for the space
            
        Returns:
            Space: Updated space instance
            
        Raises:
            APIError: If the update fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        response = self._client._make_request(
            'PATCH',
            f"space/{self.space_id}",
            json={'name': name}
        )
        
        # Update local attributes
        self.name = response['name']
        return self

    def delete(self) -> bool:
        """
        Delete this space.
        
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        self._client._make_request(
            'DELETE',
            f"space/{self.space_id}"
        )
        return True

    def delete_permanent(self) -> bool:
        """
        Permanently delete this space.
        
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        self._client._make_request(
            'DELETE',
            f"space/{self.space_id}/permanent"
        )
        return True

    def get_invitation_links(self) -> List['Invitation']:
        """
        Get all invitation links for this space.
        
        Returns:
            List[Invitation]: List of invitation links
            
        Raises:
            APIError: If the request fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        response = self._client._make_request(
            'GET',
            f"space/{self.space_id}/invitation/link"
        )
        
        # Import here to avoid circular import
        from .invitation import Invitation
        return [Invitation.from_api_response(i, self) for i in response]

    def create_invitation_link(self, role: SpaceRole) -> 'Invitation':
        """
        Create a new invitation link.
        
        Args:
            role: Role to be granted to invitees
            
        Returns:
            Invitation: The created invitation link
            
        Raises:
            APIError: If the creation fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        response = self._client._make_request(
            'POST',
            f"space/{self.space_id}/invitation/link",
            json={'role': role.value}
        )
        
        # Import here to avoid circular import
        from .invitation import Invitation
        return Invitation.from_api_response(response, self)

    def invite_by_email(
        self,
        emails: List[str],
        role: SpaceRole
    ) -> Dict[str, Dict[str, str]]:
        """
        Send invitations by email.
        
        Args:
            emails: List of email addresses to invite
            role: Role to be granted to invitees
            
        Returns:
            Dict[str, Dict[str, str]]: Map of email to invitation info
            
        Raises:
            APIError: If the invitation fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        response = self._client._make_request(
            'POST',
            f"space/{self.space_id}/invitation/email",
            json={
                'emails': emails,
                'role': role.value
            }
        )
        return response

    def get_collaborators(
        self,
        include_system: Optional[bool] = None,
        include_base: Optional[bool] = None,
        skip: Optional[int] = None,
        take: Optional[int] = None,
        search: Optional[str] = None,
        collaborator_type: Optional['PrincipalType'] = None
    ) -> Tuple[List['Collaborator'], int]:
        """
        Get all collaborators in this space.
        
        Args:
            include_system: Whether to include system collaborators
            include_base: Whether to include base collaborators
            skip: Number of collaborators to skip
            take: Number of collaborators to take
            search: Search term for filtering collaborators
            collaborator_type: Filter by collaborator type
            
        Returns:
            Tuple[List[Collaborator], int]: List of collaborators and total count
            
        Raises:
            APIError: If the request fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        params = {}
        if include_system is not None:
            params['includeSystem'] = include_system
        if include_base is not None:
            params['includeBase'] = include_base
        if skip is not None:
            params['skip'] = skip
        if take is not None:
            params['take'] = take
        if search:
            params['search'] = search
        if collaborator_type:
            params['type'] = collaborator_type.value
            
        response = self._client._make_request(
            'GET',
            f"space/{self.space_id}/collaborators",
            params=params
        )
        
        # Import here to avoid circular import
        from .collaborator import collaborator_from_api_response
        collaborators = [
            collaborator_from_api_response(c)
            for c in response['collaborators']
        ]
        return collaborators, response['total']

    def update_collaborator(
        self,
        principal_id: str,
        principal_type: 'PrincipalType',
        role: SpaceRole
    ) -> None:
        """
        Update a collaborator's role.
        
        Args:
            principal_id: ID of the user or department
            principal_type: Type of principal (user/department)
            role: New role to assign
            
        Raises:
            APIError: If the update fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        self._client._make_request(
            'PATCH',
            f"space/{self.space_id}/collaborators",
            json={
                'principalId': principal_id,
                'principalType': principal_type.value,
                'role': role.value
            }
        )

    def delete_collaborator(
        self,
        principal_id: str,
        principal_type: 'PrincipalType'
    ) -> None:
        """
        Delete a collaborator from this space.
        
        Args:
            principal_id: ID of the user or department
            principal_type: Type of principal (user/department)
            
        Raises:
            APIError: If the deletion fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        self._client._make_request(
            'DELETE',
            f"space/{self.space_id}/collaborators",
            params={
                'principalId': principal_id,
                'principalType': principal_type.value
            }
        )

    def create_base(
        self,
        name: Optional[str] = None,
        icon: Optional[str] = None
    ) -> 'Base':
        """
        Create a new base in this space.
        
        Args:
            name: Optional display name for the base
            icon: Optional icon for the base
            
        Returns:
            Base: The created base
            
        Raises:
            APIError: If the creation fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        return self._client.create_base(
            self.space_id,
            name=name,
            icon=icon
        )

    def get_bases(self) -> List['Base']:
        """
        Get all bases in this space.
        
        Returns:
            List[Base]: List of bases
            
        Raises:
            APIError: If the request fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        response = self._client._make_request(
            'GET',
            f"space/{self.space_id}/base"
        )
        
        # Import here to avoid circular import
        from .base import Base
        return [Base.from_api_response(b, self._client) for b in response]

    def add_collaborators(
        self,
        collaborators: List[Dict[str, str]],
        role: SpaceRole
    ) -> None:
        """
        Add collaborators to this space.
        
        Args:
            collaborators: List of collaborator info dicts with 'principalId' and 'principalType'
            role: Role to assign to collaborators
            
        Raises:
            APIError: If adding collaborators fails
        """
        if not self._client:
            raise ValueError("Space instance not connected to client")
            
        self._client._make_request(
            'POST',
            f"space/{self.space_id}/collaborator",
            json={
                'collaborators': collaborators,
                'role': role.value
            }
        )
