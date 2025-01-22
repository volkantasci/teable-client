"""
Undo/redo management module.

This module handles operations for managing undo/redo operations.
"""

from typing import Literal, Optional, TypedDict

from .http import TeableHttpClient

OperationStatus = Literal['fulfilled', 'failed', 'empty']

class OperationResult(TypedDict, total=False):
    """Type definition for operation result."""
    status: OperationStatus
    errorMessage: Optional[str]

class UndoRedoManager:
    """
    Handles undo/redo operations.
    
    This class manages:
    - Operation history
    - Undo/redo functionality
    - Operation status tracking
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the undo/redo manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def undo(self, table_id: str) -> OperationResult:
        """
        Undo the last operation in a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            OperationResult: Operation result including:
                - status: Operation status ('fulfilled', 'failed', 'empty')
                - errorMessage: Optional error message if operation failed
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'POST',
            f"/table/{table_id}/undo-redo/undo"
        )
        
    def redo(self, table_id: str) -> OperationResult:
        """
        Redo the last undone operation in a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            OperationResult: Operation result including:
                - status: Operation status ('fulfilled', 'failed', 'empty')
                - errorMessage: Optional error message if operation failed
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'POST',
            f"/table/{table_id}/undo-redo/redo"
        )
