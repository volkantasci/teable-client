"""
History Models Module

This module defines the history-related models for the Teable API client.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class FieldType(str, Enum):
    """Enumeration of field types."""
    SINGLE_LINE_TEXT = "singleLineText"
    LONG_TEXT = "longText"
    USER = "user"
    ATTACHMENT = "attachment"
    CHECKBOX = "checkbox"
    MULTIPLE_SELECT = "multipleSelect"
    SINGLE_SELECT = "singleSelect"
    DATE = "date"
    NUMBER = "number"
    DURATION = "duration"
    RATING = "rating"
    FORMULA = "formula"
    ROLLUP = "rollup"
    COUNT = "count"
    LINK = "link"
    CREATED_TIME = "createdTime"
    LAST_MODIFIED_TIME = "lastModifiedTime"
    CREATED_BY = "createdBy"
    LAST_MODIFIED_BY = "lastModifiedBy"
    AUTO_NUMBER = "autoNumber"
    BUTTON = "button"


class CellValueType(str, Enum):
    """Enumeration of cell value types."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATETIME = "dateTime"


@dataclass
class FieldMeta:
    """
    Represents field metadata in history.
    
    Attributes:
        name (str): Display name of the field
        type (FieldType): Type of field
        cell_value_type (CellValueType): Type of cell value
        options (Optional[Any]): Field-specific options
    """
    name: str
    type: FieldType
    cell_value_type: CellValueType
    options: Optional[Any] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'FieldMeta':
        """
        Create a FieldMeta instance from API response data.
        
        Args:
            data: Dictionary containing field metadata from API
            
        Returns:
            FieldMeta: New field metadata instance
        """
        return cls(
            name=data['name'],
            type=FieldType(data['type']),
            cell_value_type=CellValueType(data['cellValueType']),
            options=data.get('options')
        )


@dataclass
class FieldState:
    """
    Represents field state in history.
    
    Attributes:
        meta (FieldMeta): Field metadata
        data (Optional[Any]): Field data
    """
    meta: FieldMeta
    data: Optional[Any] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'FieldState':
        """
        Create a FieldState instance from API response data.
        
        Args:
            data: Dictionary containing field state from API
            
        Returns:
            FieldState: New field state instance
        """
        return cls(
            meta=FieldMeta.from_api_response(data['meta']),
            data=data.get('data')
        )


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
class RecordHistory:
    """
    Represents a record history entry.
    
    Attributes:
        history_id (str): Unique identifier for the history entry
        table_id (str): ID of the table
        record_id (str): ID of the record
        field_id (str): ID of the field
        before (FieldState): Field state before change
        after (FieldState): Field state after change
        created_time (datetime): When the change occurred
        created_by (str): ID of user who made the change
    """
    history_id: str
    table_id: str
    record_id: str
    field_id: str
    before: FieldState
    after: FieldState
    created_time: datetime
    created_by: str

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'RecordHistory':
        """
        Create a RecordHistory instance from API response data.
        
        Args:
            data: Dictionary containing history data from API
            
        Returns:
            RecordHistory: New history instance
        """
        return cls(
            history_id=data['id'],
            table_id=data['tableId'],
            record_id=data['recordId'],
            field_id=data['fieldId'],
            before=FieldState.from_api_response(data['before']),
            after=FieldState.from_api_response(data['after']),
            created_time=datetime.fromisoformat(data['createdTime'].replace('Z', '+00:00')),
            created_by=data['createdBy']
        )


@dataclass
class HistoryResponse:
    """
    Response from record history endpoint.
    
    Attributes:
        history_list (List[RecordHistory]): List of history entries
        users (Dict[str, User]): Map of user IDs to users
        next_cursor (Optional[str]): Cursor for pagination
    """
    history_list: List[RecordHistory]
    users: Dict[str, User]
    next_cursor: Optional[str] = None

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'HistoryResponse':
        """
        Create a HistoryResponse instance from API response data.
        
        Args:
            data: Dictionary containing history response data from API
            
        Returns:
            HistoryResponse: New history response instance
        """
        history_list = [
            RecordHistory.from_api_response(h)
            for h in data['historyList']
        ]
        
        users = {
            user_id: User.from_api_response(user_data)
            for user_id, user_data in data['userMap'].items()
        }
        
        return cls(
            history_list=history_list,
            users=users,
            next_cursor=data.get('nextCursor')
        )
