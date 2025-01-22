"""
Export management module.

This module handles operations for exporting data from tables.
"""

from typing import Optional

from .http import TeableHttpClient

class ExportManager:
    """
    Handles export operations.
    
    This class manages:
    - Table data exports
    - Export configuration
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the export manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def export_table_to_csv(
        self,
        table_id: str,
        *,
        view_id: Optional[str] = None
    ) -> bytes:
        """
        Export table data to CSV format.
        
        Args:
            table_id: ID of the table to export
            view_id: Optional ID of specific view to export from
            
        Returns:
            bytes: CSV file content as bytes
            
        Raises:
            APIError: If the export fails
        """
        params = {}
        if view_id is not None:
            params['viewId'] = view_id
            
        return self._http.request(
            'GET',
            f"/export/{table_id}",
            params=params,
            response_type='bytes'
        )
