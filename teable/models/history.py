"""
History Models Module

This module defines the history-related models for the Teable API client.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

@dataclass
class HistoryEntry:
    """
    Represents a single history entry.
    
    Attributes:
        operation: Type of operation performed
        timestamp: When the operation occurred
        user_id: ID of the user who performed the operation
        changes: List of changes made in this operation
    """
    operation: str
    timestamp: datetime
    user_id: str
    changes: List[Dict[str, Any]]

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """
        Create a HistoryEntry instance from API response data.
        
        Args:
            data: Dictionary containing history entry data from API
            
        Returns:
            HistoryEntry: New history entry instance
        """
        return cls(
            operation=data['operation'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
            user_id=data['userId'],
            changes=data.get('changes', [])
        )

@dataclass
class HistoryUser:
    """
    Represents a user in history entries.
    
    Attributes:
        user_id: Unique identifier for the user
        name: Display name of the user
        email: Email address of the user
        avatar: Optional URL to user's avatar
    """
    user_id: str
    name: str
    email: str
    avatar: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'HistoryUser':
        """
        Create a HistoryUser instance from API response data.
        
        Args:
            data: Dictionary containing user data from API
            
        Returns:
            HistoryUser: New history user instance
        """
        return cls(
            user_id=data['id'],
            name=data['name'],
            email=data['email'],
            avatar=data.get('avatar')
        )

@dataclass
class HistoryResponse:
    """
    Represents a response containing history entries and user information.
    
    Attributes:
        entries: List of history entries
        users: Dictionary mapping user IDs to user information
    """
    entries: List[HistoryEntry]
    users: Dict[str, HistoryUser]

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'HistoryResponse':
        """
        Create a HistoryResponse instance from API response data.
        
        Args:
            data: Dictionary containing history response data from API
            
        Returns:
            HistoryResponse: New history response instance
        """
        entries = [
            HistoryEntry.from_api_response(entry)
            for entry in data.get('entries', [])
        ]
        users = {
            user_id: HistoryUser.from_api_response(user_data)
            for user_id, user_data in data.get('users', {}).items()
        }
        return cls(entries=entries, users=users)
