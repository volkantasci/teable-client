"""
Trash Models Module

This module defines the trash-related models for the Teable API client.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ResourceType(str, Enum):
    """Enumeration of resource types."""
    SPACE = "space"
    BASE = "base"
    TABLE = "table"
    VIEW = "view"
    FIELD = "field"
    RECORD = "record"


@dataclass
class User:
    """
    Represents a user in Teable.
    
    Attributes:
        user_id (str): Unique identifier for the user
        name (str): Display name of the user
        email (str): Email address of the user
        avatar (Optional[str]): URL to user's avatar image
    """
    user_id: str
    name: str
    email: str
    avatar: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a User instance from API response data.
        
        Args:
            data: Dictionary containing user data from API
            
        Returns:
            User: New user instance
        """
        return cls(
            user_id=data['id'],
            name=data['name'],
            email=data['email'],
            avatar=data.get('avatar')
        )


@dataclass
class Resource:
    """
    Represents a resource in Teable.
    
    Attributes:
        resource_id (str): Unique identifier for the resource
        name (str): Display name of the resource
        resource_type (ResourceType): Type of resource
        space_id (Optional[str]): ID of containing space (for bases)
    """
    resource_id: str
    name: str
    resource_type: ResourceType
    space_id: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any], resource_type: ResourceType) -> 'Resource':
        """
        Create a Resource instance from API response data.
        
        Args:
            data: Dictionary containing resource data from API
            resource_type: Type of resource
            
        Returns:
            Resource: New resource instance
        """
        return cls(
            resource_id=data['id'],
            name=data['name'],
            resource_type=resource_type,
            space_id=data.get('spaceId')
        )


@dataclass
class TrashItem:
    """
    Represents an item in the trash.
    
    Attributes:
        trash_id (str): Unique identifier for the trash item
        resource_type (ResourceType): Type of resource
        deleted_time (datetime): When the item was deleted
        deleted_by (str): ID of user who deleted the item
        resource_id (Optional[str]): ID of single resource
        resource_ids (Optional[List[str]]): IDs of multiple resources
    """
    trash_id: str
    resource_type: ResourceType
    deleted_time: datetime
    deleted_by: str
    resource_id: Optional[str] = None
    resource_ids: Optional[List[str]] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'TrashItem':
        """
        Create a TrashItem instance from API response data.
        
        Args:
            data: Dictionary containing trash item data from API
            
        Returns:
            TrashItem: New trash item instance
        """
        return cls(
            trash_id=data['id'],
            resource_type=ResourceType(data['resourceType']),
            deleted_time=datetime.fromisoformat(data['deletedTime'].replace('Z', '+00:00')),
            deleted_by=data['deletedBy'],
            resource_id=data.get('resourceId'),
            resource_ids=data.get('resourceIds')
        )


@dataclass
class TrashResponse:
    """
    Response from trash listing endpoint.
    
    Attributes:
        items (List[TrashItem]): List of trash items
        users (Dict[str, User]): Map of user IDs to users
        resources (Dict[str, Resource]): Map of resource IDs to resources
        next_cursor (Optional[str]): Cursor for pagination
    """
    items: List[TrashItem]
    users: Dict[str, User]
    resources: Dict[str, Resource]
    next_cursor: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'TrashResponse':
        """
        Create a TrashResponse instance from API response data.
        
        Args:
            data: Dictionary containing trash response data from API
            
        Returns:
            TrashResponse: New trash response instance
        """
        items = [TrashItem.from_api_response(i) for i in data['trashItems']]
        
        users = {
            user_id: User.from_api_response(user_data)
            for user_id, user_data in data['userMap'].items()
        }
        
        resources = {}
        for resource_id, resource_data in data['resourceMap'].items():
            # Determine resource type from data structure
            if 'spaceId' in resource_data:
                resource_type = ResourceType.BASE
            elif 'type' in resource_data:
                if resource_data['type'] in ['grid', 'calendar', 'kanban', 'form', 'gallery', 'gantt', 'plugin']:
                    resource_type = ResourceType.VIEW
                else:
                    resource_type = ResourceType.FIELD
            else:
                # Default to SPACE for basic id/name resources
                resource_type = ResourceType.SPACE
                
            resources[resource_id] = Resource.from_api_response(
                resource_data,
                resource_type
            )
            
        return cls(
            items=items,
            users=users,
            resources=resources,
            next_cursor=data.get('nextCursor')
        )
