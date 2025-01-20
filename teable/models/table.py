"""
Table Models Module

This module defines the table-related models and operations for the Teable API client.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from ..exceptions import ResourceNotFoundError, ValidationError
from .field import Field
from .record import Record, RecordBatch
from .view import QueryBuilder, View


@dataclass
class Table:
    """
    Represents a table in Teable and provides methods for interacting with it.
    
    This class serves as the main interface for table operations including:
    - Record CRUD operations
    - Field management
    - View operations
    - Querying and filtering
    
    Attributes:
        table_id (str): Unique identifier for the table
        name (str): Display name of the table
        description (Optional[str]): Table description
        client: TeableClient instance for API communication
    """
    table_id: str
    name: str
    description: Optional[str] = None
    _client: Any = None  # Avoid circular import with TeableClient
    _fields: Optional[List[Field]] = None
    _views: Optional[List[View]] = None

    @property
    def fields(self) -> List[Field]:
        """Get all fields in the table, with caching."""
        if self._fields is None:
            self._fields = self._client.get_table_fields(self.table_id)
        return self._fields

    @property
    def views(self) -> List[View]:
        """Get all views in the table, with caching."""
        if self._views is None:
            self._views = self._client.get_table_views(self.table_id)
        return self._views

    def get_field(self, field_id: str) -> Field:
        """
        Get a specific field by ID.
        
        Args:
            field_id: ID of the field to retrieve
            
        Returns:
            Field: The requested field
            
        Raises:
            ResourceNotFoundError: If field not found
        """
        for field in self.fields:
            if field.field_id == field_id:
                return field
        raise ResourceNotFoundError(
            "Field not found", "field", field_id
        )

    def get_view(self, view_id: str) -> View:
        """
        Get a specific view by ID.
        
        Args:
            view_id: ID of the view to retrieve
            
        Returns:
            View: The requested view
            
        Raises:
            ResourceNotFoundError: If view not found
        """
        for view in self.views:
            if view.view_id == view_id:
                return view
        raise ResourceNotFoundError(
            "View not found", "view", view_id
        )

    def validate_record_fields(self, fields: Dict[str, Any]) -> None:
        """
        Validate field values for a record.
        
        Args:
            fields: Dictionary of field values to validate
            
        Raises:
            ValidationError: If any field values are invalid
        """
        table_fields = {f.field_id: f for f in self.fields}
        
        # Check for required fields
        required_fields = [
            f.field_id for f in self.fields
            if f.is_required and not f.is_computed
        ]
        missing_fields = [
            f_id for f_id in required_fields
            if f_id not in fields
        ]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {missing_fields}"
            )
        
        # Validate each provided field value
        for field_id, value in fields.items():
            if field_id not in table_fields:
                raise ValidationError(f"Unknown field: {field_id}")
            
            field = table_fields[field_id]
            try:
                field.validate_value(value)
            except ValidationError as e:
                raise ValidationError(
                    f"Invalid value for field '{field.name}': {str(e)}"
                )

    def get_records(
        self,
        query: Optional[Union[QueryBuilder, Dict[str, Any]]] = None
    ) -> List[Record]:
        """
        Get records from the table.
        
        Args:
            query: Query parameters or QueryBuilder instance
            
        Returns:
            List[Record]: Retrieved records
        """
        if isinstance(query, QueryBuilder):
            query = query.build()
        elif query is None:
            query = {}
            
        records_data = self._client.get_records(self.table_id, query)
        return [Record.from_api_response(r) for r in records_data]

    def get_record(self, record_id: str) -> Record:
        """
        Get a single record by ID.
        
        Args:
            record_id: ID of the record to retrieve
            
        Returns:
            Record: The requested record
            
        Raises:
            ResourceNotFoundError: If record not found
        """
        try:
            record_data = self._client.get_record(self.table_id, record_id)
            return Record.from_api_response(record_data)
        except Exception as e:
            raise ResourceNotFoundError(
                str(e), "record", record_id
            )

    def create_record(self, fields: Dict[str, Any]) -> Record:
        """
        Create a new record.
        
        Args:
            fields: Field values for the new record
            
        Returns:
            Record: The created record
        """
        self.validate_record_fields(fields)
        record_data = self._client.create_record(self.table_id, fields)
        return Record.from_api_response(record_data)

    def update_record(
        self,
        record_id: str,
        fields: Dict[str, Any]
    ) -> bool:
        """
        Update an existing record.
        
        Args:
            record_id: ID of the record to update
            fields: New field values
            
        Returns:
            bool: True if update successful
        """
        self.validate_record_fields(fields)
        return self._client.update_record(self.table_id, record_id, fields)

    def delete_record(self, record_id: str) -> bool:
        """
        Delete a record.
        
        Args:
            record_id: ID of the record to delete
            
        Returns:
            bool: True if deletion successful
        """
        return self._client.delete_record(self.table_id, record_id)

    def batch_create_records(
        self,
        records: List[Dict[str, Any]],
        field_key_type: str = 'name',
        typecast: bool = False
    ) -> RecordBatch:
        """
        Create multiple records in a single request.
        
        Args:
            records: List of record field values
            field_key_type: Key type for record fields ('id' or 'name')
            typecast: Whether to enable automatic data conversion
            
        Returns:
            RecordBatch: Results of the batch operation
        """
        for fields in records:
            self.validate_record_fields(fields)
            
        return self._client.batch_create_records(
            self.table_id,
            records,
            field_key_type,
            typecast
        )

    def batch_update_records(
        self,
        updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Update multiple records in a single request.
        
        Args:
            updates: List of record updates with IDs and new field values
            
        Returns:
            bool: True if all updates successful
        """
        for update in updates:
            if 'fields' in update:
                self.validate_record_fields(update['fields'])
                
        return self._client.batch_update_records(self.table_id, updates)

    def batch_delete_records(
        self,
        record_ids: List[str]
    ) -> bool:
        """
        Delete multiple records in a single request.
        
        Args:
            record_ids: List of record IDs to delete
            
        Returns:
            bool: True if all deletions successful
        """
        return self._client.batch_delete_records(self.table_id, record_ids)

    def query(self) -> QueryBuilder:
        """
        Create a new query builder for this table.
        
        Returns:
            QueryBuilder: New query builder instance
        """
        return QueryBuilder()

    @classmethod
    def from_api_response(
        cls,
        data: Dict[str, Any],
        client: Any
    ) -> 'Table':
        """
        Create a Table instance from API response data.
        
        Args:
            data: Dictionary containing table data from API
            client: TeableClient instance for API communication
            
        Returns:
            Table: New table instance
        """
        return cls(
            table_id=data['id'],
            name=data['name'],
            description=data.get('description'),
            _client=client
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert table to dictionary format for API requests.
        
        Returns:
            dict: Table data as dictionary
        """
        result = {
            'id': self.table_id,
            'name': self.name
        }
        
        if self.description:
            result['description'] = self.description
            
        return result

    def clear_cache(self) -> None:
        """Clear the cached fields and views."""
        self._fields = None
        self._views = None
