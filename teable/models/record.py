"""
Record Models Module

This module defines the record-related models and operations for the Teable API client.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .field import Field


@dataclass
class RecordStatus:
    """
    Represents a record's visibility and deletion status.
    
    Attributes:
        is_visible (bool): Whether the record is visible
        is_deleted (bool): Whether the record is deleted
    """
    is_visible: bool
    is_deleted: bool

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'RecordStatus':
        """
        Create a RecordStatus instance from API response data.
        
        Args:
            data: Dictionary containing status data from API
            
        Returns:
            RecordStatus: New status instance
        """
        return cls(
            is_visible=data['isVisible'],
            is_deleted=data['isDeleted']
        )


@dataclass
class Record:
    """
    Represents a record in a Teable table.
    
    Attributes:
        record_id (str): Unique identifier for the record
        fields (Dict[str, Any]): Field values keyed by field name or ID
        name (Optional[str]): Primary field value
        auto_number (Optional[int]): Auto-incrementing number
        created_time (Optional[datetime]): Record creation timestamp
        last_modified_time (Optional[datetime]): Last modification timestamp
        created_by (Optional[str]): User ID who created the record
        last_modified_by (Optional[str]): User ID who last modified the record
    """
    record_id: str
    fields: Dict[str, Any]
    name: Optional[str] = None
    auto_number: Optional[int] = None
    created_time: Optional[datetime] = None
    last_modified_time: Optional[datetime] = None
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None

    def get_field_value(
        self,
        field: Union[str, Field],
        cell_format: str = 'json'
    ) -> Any:
        """
        Get the value of a specific field in this record.
        
        Args:
            field: Field name/ID or Field object
            cell_format: Response format ('json' or 'text')
            
        Returns:
            The field value
            
        Raises:
            KeyError: If field not found in record
        """
        field_id = field.field_id if isinstance(field, Field) else field
        if field_id not in self.fields:
            raise KeyError(f"Field '{field_id}' not found in record")
        return self.fields[field_id]

    def set_field_value(
        self,
        field: Union[str, Field],
        value: Any,
        typecast: bool = False
    ) -> None:
        """
        Set the value of a specific field in this record.
        
        Args:
            field: Field name/ID or Field object
            value: New value for the field
            typecast: Enable automatic type conversion
            
        Note:
            This method only updates the local record object.
            Use Table.update_record() to persist changes to the API.
        """
        field_id = field.field_id if isinstance(field, Field) else field
        self.fields[field_id] = value

    @classmethod
    def from_api_response(cls, data: Union[Dict[str, Any], 'Record']) -> 'Record':
        """
        Create a Record instance from API response data.
        
        Args:
            data: Dictionary containing record data from API
            
        Returns:
            Record: New record instance
        """
        if isinstance(data, Record):
            return data
        else:
            return cls(
                record_id=data['id'],
                fields=data['fields'],
                name=data.get('name'),
                auto_number=data.get('autoNumber'),
                created_time=datetime.fromisoformat(data['createdTime'].replace('Z', '+00:00'))
                if 'createdTime' in data else None,
                last_modified_time=datetime.fromisoformat(data['lastModifiedTime'].replace('Z', '+00:00'))
                if 'lastModifiedTime' in data else None,
                created_by=data.get('createdBy'),
                last_modified_by=data.get('lastModifiedBy')
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert record to dictionary format for API requests.
        
        Returns:
            dict: Record data as dictionary
        """
        result = {
            'id': self.record_id,
            'fields': self.fields
        }
        
        if self.name:
            result['name'] = self.name
        if self.auto_number is not None:
            result['autoNumber'] = self.auto_number
        if self.created_time:
            result['createdTime'] = self.created_time.isoformat()
        if self.last_modified_time:
            result['lastModifiedTime'] = self.last_modified_time.isoformat()
        if self.created_by:
            result['createdBy'] = self.created_by
        if self.last_modified_by:
            result['lastModifiedBy'] = self.last_modified_by
            
        return result


@dataclass
class RecordBatch:
    """
    Represents a batch of records for bulk operations.
    
    This class helps manage bulk create/update/delete operations
    by tracking successful and failed operations.
    
    Attributes:
        successful (List[Record]): Successfully processed records
        failed (List[Dict]): Failed operations with error details
        total (int): Total number of records in the batch
    """
    successful: List[Record]
    failed: List[Dict[str, Any]]
    total: int

    @property
    def success_count(self) -> int:
        """Number of successful operations."""
        return len(self.successful)

    @property
    def failure_count(self) -> int:
        """Number of failed operations."""
        return len(self.failed)

    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        return (self.success_count / self.total) * 100 if self.total > 0 else 0

    def __str__(self) -> str:
        """String representation of batch results."""
        return (
            f"RecordBatch(total={self.total}, "
            f"successful={self.success_count}, "
            f"failed={self.failure_count}, "
            f"success_rate={self.success_rate:.1f}%)"
        )

    @classmethod
    def from_api_response(
        cls, response: Dict[str, Any], total: int
    ) -> 'RecordBatch':
        """
        Create a RecordBatch instance from API response data.
        
        Args:
            response: Dictionary containing batch operation results
            total: Total number of records in the batch
            
        Returns:
            RecordBatch: New batch instance
        """
        # API response'da records key'i varsa, onları successful olarak kabul et
        if 'records' in response:
            successful = [Record.from_api_response(r) for r in response['records']]
            failed = []
        else:
            successful = [
                Record.from_api_response(r)
                for r in response.get('successful', [])
            ]
            failed = response.get('failed', [])
        
        return cls(
            successful=successful,
            failed=failed,
            total=total
        )
