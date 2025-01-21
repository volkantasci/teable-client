"""
Selection Models Module

This module provides models for handling selections in Teable.
"""

from typing import Dict, List, Any, Optional, Literal


class SelectionRange:
    """
    Model representing selection range information.
    
    Attributes:
        record_ids (List[str]): List of record IDs in the selection
        field_ids (List[str]): List of field IDs in the selection
    """
    
    def __init__(self, record_ids: List[str], field_ids: List[str]):
        """
        Initialize selection range.
        
        Args:
            record_ids: List of record IDs
            field_ids: List of field IDs
        """
        self.record_ids = record_ids
        self.field_ids = field_ids
        
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'SelectionRange':
        """
        Create a SelectionRange instance from API response data.
        
        Args:
            response: API response data
            
        Returns:
            SelectionRange: Created instance
        """
        return cls(
            record_ids=response.get('recordIds', []),
            field_ids=response.get('fieldIds', [])
        )
