"""
Invitation Models Module

This module defines the invitation-related models for the Teable API client.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Base
    from .space import Space, SpaceRole
else:
    from .space import SpaceRole

ParentType = Union['Space', 'Base']


@dataclass
class Invitation:
    """
    Represents an invitation link in a Teable space.
    
    Attributes:
        invitation_id (str): Unique identifier for the invitation
        role (SpaceRole): Role to be granted to invitees
        invite_url (str): URL for accepting the invitation
        invitation_code (str): Code for accepting the invitation
        created_by (str): User who created the invitation
        created_time (datetime): When the invitation was created
    """
    invitation_id: str
    role: SpaceRole
    invite_url: str
    invitation_code: str
    created_by: str
    created_time: datetime
    _parent: Optional[ParentType] = None

    @classmethod
    def from_api_response(
        cls,
        data: Dict[str, Any],
        parent: Optional[ParentType] = None
    ) -> 'Invitation':
        """
        Create an Invitation instance from API response data.
        
        Args:
            data: Dictionary containing invitation data from API
            
        Returns:
            Invitation: New invitation instance
        """
        invitation = cls(
            invitation_id=data['invitationId'],
            role=SpaceRole(data['role']),
            invite_url=data['inviteUrl'],
            invitation_code=data['invitationCode'],
            created_by=data['createdBy'],
            created_time=datetime.fromisoformat(data['createdTime'].replace('Z', '+00:00')),
            _parent=parent
        )
        return invitation

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert invitation to dictionary format for API requests.
        
        Returns:
            dict: Invitation data as dictionary
        """
        return {
            'invitationId': self.invitation_id,
            'role': self.role.value,
            'inviteUrl': self.invite_url,
            'invitationCode': self.invitation_code,
            'createdBy': self.created_by,
            'createdTime': self.created_time.isoformat()
        }

    def update(self, role: SpaceRole) -> 'Invitation':
        """
        Update the invitation's role.
        
        Args:
            role: New role for invitees
            
        Returns:
            Invitation: Updated invitation instance
            
        Raises:
            APIError: If the update fails
        """
        if not hasattr(self, '_parent') or not self._parent:
            raise ValueError("Invitation instance not connected to parent")
            
        from .space import Space
        endpoint = (
            f"space/{self._parent.space_id}"
            if isinstance(self._parent, Space)
            else f"base/{self._parent.base_id}"
        )
        
        response = self._parent._client._make_request(
            'PATCH',
            f"{endpoint}/invitation/link/{self.invitation_id}",
            json={'role': role.value}
        )
        
        # Update local attributes
        self.role = SpaceRole(response['role'])
        return self

    def delete(self) -> bool:
        """
        Delete this invitation link.
        
        Returns:
            bool: True if deletion successful
            
        Raises:
            APIError: If the deletion fails
        """
        if not hasattr(self, '_parent') or not self._parent:
            raise ValueError("Invitation instance not connected to parent")
            
        from .space import Space
        endpoint = (
            f"space/{self._parent.space_id}"
            if isinstance(self._parent, Space)
            else f"base/{self._parent.base_id}"
        )
        
        self._parent._client._make_request(
            'DELETE',
            f"{endpoint}/invitation/link/{self.invitation_id}"
        )
        return True
