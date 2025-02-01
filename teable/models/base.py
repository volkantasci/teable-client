"""
Base Models Module

This module defines the base-related models for the Teable API client.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .collaborator import Collaborator, PrincipalType
    from .invitation import Invitation
    from ..core.client import TeableClient

class ClientProtocol(Protocol):
    """Protocol defining the required client interface."""
    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Any: ...



class CollaboratorType(str, Enum):
    """Enumeration of collaborator types."""
    SPACE = "space"
    BASE = "base"


class Position(str, Enum):
    """Enumeration of position options."""
    BEFORE = "before"
    AFTER = "after"


@dataclass
class Base:
    """
    Represents a base in Teable.
    
    A base is a container for tables and other resources within a space.
    
    Attributes:
        base_id (str): Unique identifier for the base
        name (str): Display name of the base
        space_id (str): ID of the space containing this base
        icon (Optional[str]): Icon for the base
        _client: TeableClient instance for API communication
    """
    base_id: str
    name: str
    space_id: str
    icon: Optional[str] = None
    _client: Optional[Union['TeableClient', ClientProtocol]] = None
    collaborator_type: Optional[CollaboratorType] = None
    is_unrestricted: bool = False

    @classmethod
    def from_api_response(
        cls,
        data: Dict[str, Any],
        client: Optional[Union['TeableClient', ClientProtocol]] = None
    ) -> 'Base':
        """
        Create a Base instance from API response data.
        
        Args:
            data: Dictionary containing base data from API
            client: Optional TeableClient instance for API communication
            
        Returns:
            Base: New base instance
        """
        return cls(
            base_id=data['id'],
            name=data['name'],
            space_id=data['spaceId'],
            icon=data.get('icon'),
            _client=client,
            collaborator_type=CollaboratorType(data['collaboratorType']) if 'collaboratorType' in data else None,
            is_unrestricted=data.get('isUnrestricted', False)
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert base to dictionary format for API requests.
        
        Returns:
            dict: Base data as dictionary
        """
        data = {
            'id': self.base_id,
            'name': self.name,
            'spaceId': self.space_id,
            'icon': self.icon,
            'isUnrestricted': self.is_unrestricted
        }
        
        if self.collaborator_type:
            data['collaboratorType'] = self.collaborator_type.value
            
        return data

    def update(
        self,
        name: Optional[str] = None,
        icon: Optional[str] = None
    ) -> 'Base':
        """
        Update this base's information.
        
        Args:
            name: Optional new display name
            icon: Optional new icon
            
        Returns:
            Base: Updated base instance
            
        Raises:
            APIError: If the update fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        data = {}
        if name:
            data['name'] = name
        if icon:
            data['icon'] = icon
            
        response = self._client._make_request(
            'PATCH',
            f"base/{self.base_id}",
            json=data
        )
        
        # Update local attributes
        if 'name' in response:
            self.name = response['name']
        if 'icon' in response:
            self.icon = response['icon']
            
        return self

    def delete(self) -> bool:
        """
        Delete this base.
        
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'DELETE',
            f"base/{self.base_id}"
        )
        return True

    def delete_permanent(self) -> bool:
        """
        Permanently delete this base.
        
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'DELETE',
            f"base/{self.base_id}/permanent"
        )
        return True

    def update_order(
        self,
        anchor_id: str,
        position: Position
    ) -> None:
        """
        Update this base's position relative to another base.
        
        Args:
            anchor_id: ID of the base to position relative to
            position: Position relative to anchor base
            
        Raises:
            APIError: If the update fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'PUT',
            f"base/{self.base_id}/order",
            json={
                'anchorId': anchor_id,
                'position': position.value
            }
        )

    def duplicate(
        self,
        space_id: str,
        name: Optional[str] = None,
        with_records: bool = False
    ) -> 'Base':
        """
        Create a duplicate of this base.
        
        Args:
            space_id: ID of the space to create the duplicate in
            name: Optional name for the duplicated base
            with_records: Whether to include records in the duplicate
            
        Returns:
            Base: The duplicated base
            
        Raises:
            APIError: If the duplication fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        return self._client.duplicate_base(
            self.base_id,
            space_id,
            name=name,
            with_records=with_records
        )

    def get_collaborators(
        self,
        include_system: Optional[bool] = None,
        skip: Optional[int] = None,
        take: Optional[int] = None,
        search: Optional[str] = None,
        collaborator_type: Optional['PrincipalType'] = None
    ) -> Tuple[List['Collaborator'], int]:
        """
        Get all collaborators in this base.
        
        Args:
            include_system: Whether to include system collaborators
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
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        params = {}
        if include_system is not None:
            params['includeSystem'] = include_system
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
            f"base/{self.base_id}/collaborators",
            params=params
        )
        
        # Import here to avoid circular import
        from .collaborator import collaborator_from_api_response
        collaborators = [
            collaborator_from_api_response(c, self._client)
            for c in response['collaborators']
        ]
        return collaborators, response['total']

    def update_collaborator(
        self,
        principal_id: str,
        principal_type: 'PrincipalType',
        role: str
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
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'PATCH',
            f"base/{self.base_id}/collaborators",
            json={
                'principalId': principal_id,
                'principalType': principal_type.value,
                'role': role
            }
        )

    def delete_collaborator(
        self,
        principal_id: str,
        principal_type: 'PrincipalType'
    ) -> None:
        """
        Delete a collaborator from this base.
        
        Args:
            principal_id: ID of the user or department
            principal_type: Type of principal (user/department)
            
        Raises:
            APIError: If the deletion fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'DELETE',
            f"base/{self.base_id}/collaborators",
            params={
                'principalId': principal_id,
                'principalType': principal_type.value
            }
        )

    def get_permissions(self) -> Dict[str, bool]:
        """
        Get permissions for this base.
        
        Returns:
            Dict[str, bool]: Map of permission names to boolean values
            
        Raises:
            APIError: If the request fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        return self._client._make_request(
            'GET',
            f"base/{self.base_id}/permission"
        )

    def get_tables(self) -> List['Table']:
        """
        Get all tables in this base.
        
        Returns:
            List[Table]: List of tables in the base
            
        Raises:
            APIError: If the request fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client")
            
        response = self._client._make_request(
            'GET',
            f"base/{self.base_id}/table"
        )
        
        # Import here to avoid circular import
        from .table import Table
        return [Table.from_api_response(t, self._client) for t in response]

    def query(
        self,
        query: str,
        cell_format: str = 'text'
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query on this base.
        
        Args:
            query: SQL query to execute
            cell_format: Format for cell values ('json' or 'text')
            
        Returns:
            List[Dict[str, Any]]: Query results
            
        Raises:
            APIError: If the query fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        return self._client._make_request(
            'GET',
            f"base/{self.base_id}/query",
            params={
                'query': query,
                'cellFormat': cell_format
            }
        )

    def get_invitation_links(self) -> List['Invitation']:
        """
        Get all invitation links for this base.
        
        Returns:
            List[Invitation]: List of invitation links
            
        Raises:
            APIError: If the request fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        response = self._client._make_request(
            'GET',
            f"base/{self.base_id}/invitation/link"
        )
        
        # Import here to avoid circular import
        from .invitation import Invitation
        return [Invitation.from_api_response(i, self) for i in response]

    def create_invitation_link(self, role: str) -> 'Invitation':
        """
        Create a new invitation link.
        
        Args:
            role: Role to be granted to invitees ('creator', 'editor', 'commenter', 'viewer')
            
        Returns:
            Invitation: The created invitation link
            
        Raises:
            APIError: If the creation fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        response = self._client._make_request(
            'POST',
            f"base/{self.base_id}/invitation/link",
            json={'role': role}
        )
        
        # Import here to avoid circular import
        from .invitation import Invitation
        return Invitation.from_api_response(response, self)

    def send_email_invitations(
        self,
        emails: List[str],
        role: str
    ) -> Dict[str, Dict[str, str]]:
        """
        Send invitation emails to multiple recipients.
        
        Args:
            emails: List of email addresses to invite
            role: Role to be granted to invitees ('creator', 'editor', 'commenter', 'viewer')
            
        Returns:
            Dict[str, Dict[str, str]]: Map of email addresses to invitation IDs
            
        Raises:
            APIError: If sending invitations fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        return self._client._make_request(
            'POST',
            f"base/{self.base_id}/invitation/email",
            json={
                'emails': emails,
                'role': role
            }
        )

    def add_collaborators(
        self,
        collaborators: List[Dict[str, str]],
        role: str
    ) -> None:
        """
        Add collaborators to this base.
        
        Args:
            collaborators: List of collaborator info dicts with 'principalId' and 'principalType'
            role: Role to assign to collaborators ('creator', 'editor', 'commenter', 'viewer')
            
        Raises:
            APIError: If adding collaborators fails
        """
        if not self._client:
            raise RuntimeError("Base instance not connected to client. Did you create this instance directly instead of through TeableClient?")
            
        self._client._make_request(
            'POST',
            f"base/{self.base_id}/collaborator",
            json={
                'collaborators': collaborators,
                'role': role
            }
        )
