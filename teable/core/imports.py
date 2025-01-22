"""
Import management module.

This module handles operations for importing data from external files.
"""

from typing import Dict, List, Literal, Optional, TypedDict, Union

from .http import TeableHttpClient

class InsertConfig(TypedDict):
    """Type definition for table insert configuration."""
    sourceWorkSheetKey: str
    excludeFirstRow: bool
    sourceColumnMap: Dict[str, Optional[int]]

class TableImportConfig(TypedDict, total=False):
    """Type definition for importing into existing table."""
    attachmentUrl: str
    fileType: Literal['csv', 'excel']
    insertConfig: InsertConfig
    notification: Optional[bool]

class ImportColumnConfig(TypedDict):
    """Type definition for import column configuration."""
    type: Literal[
        'singleLineText', 'longText', 'user', 'attachment', 'checkbox',
        'multipleSelect', 'singleSelect', 'date', 'number', 'duration',
        'rating', 'formula', 'rollup', 'count', 'link', 'createdTime',
        'lastModifiedTime', 'createdBy', 'lastModifiedBy', 'autoNumber',
        'button'
    ]
    name: str
    sourceColumnIndex: int

class WorksheetConfig(TypedDict):
    """Type definition for worksheet import configuration."""
    name: str
    columns: List[ImportColumnConfig]
    useFirstRowAsHeader: bool
    importData: bool

class ImportConfig(TypedDict, total=False):
    """Type definition for import configuration."""
    worksheets: Dict[str, WorksheetConfig]
    attachmentUrl: str
    fileType: Literal['csv', 'excel']
    notification: Optional[bool]
    tz: str

class CreatedTable(TypedDict, total=False):
    """Type definition for created table response."""
    id: str
    name: str
    dbTableName: str
    description: Optional[str]
    icon: Optional[str]
    order: Optional[int]
    lastModifiedTime: Optional[str]
    defaultViewId: Optional[str]

class ImportColumn(TypedDict):
    """Type definition for an analyzed column."""
    type: Literal[
        'singleLineText', 'longText', 'user', 'attachment', 'checkbox',
        'multipleSelect', 'singleSelect', 'date', 'number', 'duration',
        'rating', 'formula', 'rollup', 'count', 'link', 'createdTime',
        'lastModifiedTime', 'createdBy', 'lastModifiedBy', 'autoNumber',
        'button'
    ]
    name: str

class WorksheetInfo(TypedDict):
    """Type definition for worksheet information."""
    name: str
    columns: List[ImportColumn]

class ImportAnalysis(TypedDict):
    """Type definition for import analysis response."""
    worksheets: Dict[str, WorksheetInfo]

class ImportManager:
    """
    Handles import operations.
    
    This class manages:
    - File analysis and column type detection
    - Creating new tables from files
    - Importing data into existing tables
    - Import configuration and validation
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the import manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def analyze_file(
        self,
        attachment_url: str,
        file_type: Literal['csv', 'excel']
    ) -> ImportAnalysis:
        """
        Analyze a file to determine column types for import.
        
        Args:
            attachment_url: URL of the file to analyze
            file_type: Type of file ('csv' or 'excel')
            
        Returns:
            ImportAnalysis: Analysis results containing:
                - worksheets: Dictionary mapping worksheet names to their info:
                    - name: Worksheet name
                    - columns: List of columns with:
                        - type: Detected field type
                        - name: Column name
            
        Raises:
            APIError: If the analysis fails
            ValueError: If file_type is invalid
        """
        if file_type not in ('csv', 'excel'):
            raise ValueError("file_type must be either 'csv' or 'excel'")
            
        return self._http.request(
            'GET',
            '/import/analyze',
            params={
                'attachmentUrl': attachment_url,
                'fileType': file_type
            }
        )
        
    def create_table_from_file(
        self,
        base_id: str,
        attachment_url: str,
        file_type: Literal['csv', 'excel'],
        worksheets: Dict[str, WorksheetConfig],
        tz: str,
        *,
        notification: Optional[bool] = None
    ) -> CreatedTable:
        """
        Create a new table by importing data from a file.
        
        Args:
            base_id: ID of the base to create the table in
            attachment_url: URL of the file to import
            file_type: Type of file ('csv' or 'excel')
            worksheets: Configuration for each worksheet to import:
                - name: Name for the new table
                - columns: List of columns with:
                    - type: Field type to use
                    - name: Column name
                    - sourceColumnIndex: Index of column in source file
                - useFirstRowAsHeader: Whether to use first row as headers
                - importData: Whether to import the data rows
            tz: Timezone to use for date formatting
            notification: Optional flag to enable notifications
            
        Returns:
            CreatedTable: Information about the created table:
                - id: Table ID
                - name: Table name
                - dbTableName: Database table name
                - description: Table description (if provided)
                - icon: Table icon (if provided)
                - order: Table order (if provided)
                - lastModifiedTime: Last modification time (if provided)
                - defaultViewId: Default view ID (if provided)
            
        Raises:
            APIError: If the import fails
            ValueError: If file_type is invalid
        """
        if file_type not in ('csv', 'excel'):
            raise ValueError("file_type must be either 'csv' or 'excel'")
            
        data: ImportConfig = {
            'worksheets': worksheets,
            'attachmentUrl': attachment_url,
            'fileType': file_type,
            'tz': tz
        }
        
        if notification is not None:
            data['notification'] = notification
            
        return self._http.request(
            'POST',
            f"/import/{base_id}",
            json=data
        )
        
    def import_into_table(
        self,
        base_id: str,
        table_id: str,
        attachment_url: str,
        file_type: Literal['csv', 'excel'],
        source_worksheet_key: str,
        exclude_first_row: bool,
        source_column_map: Dict[str, Optional[int]],
        *,
        notification: Optional[bool] = None
    ) -> bool:
        """
        Import data from a file into an existing table.
        
        Args:
            base_id: ID of the base containing the table
            table_id: ID of the table to import into
            attachment_url: URL of the file to import
            file_type: Type of file ('csv' or 'excel')
            source_worksheet_key: Key of the worksheet to import from
            exclude_first_row: Whether to skip the first row
            source_column_map: Mapping of field IDs to source column indices
            notification: Optional flag to enable notifications
            
        Returns:
            bool: True if import successful
            
        Raises:
            APIError: If the import fails
            ValueError: If file_type is invalid
        """
        if file_type not in ('csv', 'excel'):
            raise ValueError("file_type must be either 'csv' or 'excel'")
            
        data: TableImportConfig = {
            'attachmentUrl': attachment_url,
            'fileType': file_type,
            'insertConfig': {
                'sourceWorkSheetKey': source_worksheet_key,
                'excludeFirstRow': exclude_first_row,
                'sourceColumnMap': source_column_map
            }
        }
        
        if notification is not None:
            data['notification'] = notification
            
        self._http.request(
            'PATCH',
            f"/import/{base_id}/{table_id}",
            json=data
        )
        return True
