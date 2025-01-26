"""User model module."""
from typing import Dict, Any, Optional


class Organization:
    """Organization model."""

    def __init__(
        self,
        id: str,
        name: str,
        is_admin: Optional[bool] = None
    ):
        """
        Initialize Organization.
        
        Args:
            id: Organization ID
            name: Organization name
            is_admin: Whether user is admin of organization
        """
        self.id = id
        self.name = name
        self.is_admin = is_admin

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'Organization':
        """
        Create Organization from API response.
        
        Args:
            response: API response data
            
        Returns:
            Organization: Created organization
        """
        return cls(
            id=response['id'],
            name=response['name'],
            is_admin=response.get('isAdmin')
        )


class User:
    """User model."""

    def __init__(
        self,
        id: str,
        name: str,
        email: str,
        notify_meta: Optional[Dict[str, bool]] = None,
        has_password: Optional[bool] = None,
        avatar: Optional[str] = None,
        phone: Optional[str] = None,
        is_admin: Optional[bool] = None,
        organization: Optional[Organization] = None
    ):
        """
        Initialize User.
        
        Args:
            id: User ID
            name: User name
            email: User email
            notify_meta: Optional notification settings
            has_password: Optional whether user has password
            avatar: Optional avatar URL
            phone: Optional phone number
            is_admin: Whether user is admin
            organization: Optional organization info
        """
        self.id = id
        self.name = name
        self.email = email
        self.notify_meta = notify_meta
        self.has_password = has_password
        self.avatar = avatar
        self.phone = phone
        self.is_admin = is_admin
        self.organization = organization

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'User':
        """
        Create User from API response.
        
        Args:
            response: API response data
            
        Returns:
            User: Created user
        """
        return cls(
            id=response['id'],
            name=response['name'],
            email=response['email'],
            notify_meta=response.get('notifyMeta'),
            has_password=response.get('hasPassword'),
            avatar=response.get('avatar'),
            phone=response.get('phone'),
            is_admin=response.get('isAdmin'),
            organization=Organization.from_api_response(response['organization'])
            if 'organization' in response else None
        )
