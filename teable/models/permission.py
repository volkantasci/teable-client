"""
Permission Models Module

This module provides models for handling permissions in Teable.
"""

from typing import Dict, Any


class FieldPermission:
    """
    Model representing field-level permissions.
    
    Attributes:
        fields (Dict[str, Dict[str, bool]]): Field-specific permissions
        create (bool): Whether new fields can be created
    """
    
    def __init__(self, fields: Dict[str, Dict[str, bool]], create: bool):
        """
        Initialize field permissions.
        
        Args:
            fields: Field-specific permissions
            create: Whether new fields can be created
        """
        self.fields = fields
        self.create = create
        
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'FieldPermission':
        """
        Create a FieldPermission instance from API response data.
        
        Args:
            response: API response data
            
        Returns:
            FieldPermission: Created instance
        """
        return cls(
            fields=response['fields'],
            create=response['create']
        )


class TablePermission:
    """
    Model representing table-level permissions.
    
    Attributes:
        table (Dict[str, bool]): Table-level permissions
        view (Dict[str, bool]): View-level permissions
        record (Dict[str, bool]): Record-level permissions
        field (FieldPermission): Field-level permissions
    """
    
    def __init__(
        self,
        table: Dict[str, bool],
        view: Dict[str, bool],
        record: Dict[str, bool],
        field: FieldPermission
    ):
        """
        Initialize table permissions.
        
        Args:
            table: Table-level permissions
            view: View-level permissions
            record: Record-level permissions
            field: Field-level permissions
        """
        self.table = table
        self.view = view
        self.record = record
        self.field = field
        
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'TablePermission':
        """
        Create a TablePermission instance from API response data.
        
        Args:
            response: API response data
            
        Returns:
            TablePermission: Created instance
        """
        return cls(
            table=response['table'],
            view=response['view'],
            record=response['record'],
            field=FieldPermission.from_api_response(response['field'])
        )
