"""
Core Client Module

This module provides the main TeableClient class that handles
API communication and serves as the primary interface for the library.
"""

import time
from typing import Any, Dict, List, Optional, Union
import requests

from ..exceptions import (
    APIError,
    AuthenticationError,
    BatchOperationError,
    ConfigurationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError
)
from ..models.config import TeableConfig
from ..models.field import Field
from ..models.record import Record, RecordBatch
from ..models.table import Table
from ..models.view import View


class TeableClient:
    """
    Main client class for interacting with the Teable API.
    
    This class handles:
    - API authentication and configuration
    - HTTP request management
    - Rate limiting and retries
    - Resource caching
    - High-level operations on tables, records, fields, and views
    
    Attributes:
        config (TeableConfig): Client configuration
    """
    
    def __init__(self, config: Union[TeableConfig, Dict[str, Any]]):
        """
        Initialize the client with configuration.
        
        Args:
            config: Configuration instance or dictionary
        """
        if isinstance(config, dict):
            self.config = TeableConfig.from_dict(config)
        else:
            self.config = config
            
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Rate limiting state
        self._rate_limit_remaining = 100
        self._rate_limit_reset = 0
        
        # Cache for resources
        self._cache = {
            'tables': {},
            'fields': {},
            'views': {}
        }

    def _check_rate_limit(self) -> None:
        """
        Check and enforce rate limits.
        
        Raises:
            RateLimitError: If rate limit exceeded
        """
        if self._rate_limit_remaining <= 0:
            reset_time = self._rate_limit_reset - time.time()
            if reset_time > 0:
                if self.config.retry_delay is not None:
                    time.sleep(min(reset_time, self.config.retry_delay))
                else:
                    raise RateLimitError(
                        "Rate limit exceeded",
                        reset_time=self._rate_limit_reset
                    )

    def _update_rate_limits(self, headers: Dict[str, str]) -> None:
        """Update rate limit tracking from response headers."""
        if 'X-RateLimit-Remaining' in headers:
            self._rate_limit_remaining = int(headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in headers:
            self._rate_limit_reset = int(headers['X-RateLimit-Reset'])

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Any:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data
            
        Raises:
            Various exceptions based on response
        """
        self._check_rate_limit()
        
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        retries = 0
        
        while True:
            try:
                response = self.session.request(
                    method,
                    url,
                    timeout=self.config.timeout,
                    **kwargs
                )
                self._update_rate_limits(response.headers)
                
                if response.status_code == 429:  # Rate limit exceeded
                    if (self.config.max_retries is not None and
                        retries < self.config.max_retries):
                        retries += 1
                        time.sleep(self.config.retry_delay or 1)
                        continue
                    else:
                        raise RateLimitError(
                            "Rate limit exceeded",
                            response.status_code,
                            reset_time=float(response.headers.get('X-RateLimit-Reset', 0))
                        )
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError(
                        "Authentication failed",
                        e.response.status_code
                    )
                elif e.response.status_code == 404:
                    raise ResourceNotFoundError(
                        "Resource not found",
                        endpoint,
                        str(kwargs.get('params', {})),
                        e.response.status_code
                    )
                else:
                    raise APIError(
                        f"HTTP {e.response.status_code}: {e.response.text}",
                        e.response.status_code,
                        e.response.text
                    )
            except requests.exceptions.RequestException as e:
                raise NetworkError(f"Request failed: {str(e)}")

    def get_table(self, table_id: str) -> Table:
        """
        Get a table by ID.
        
        Args:
            table_id: ID of the table
            
        Returns:
            Table: The requested table
        """
        if table_id in self._cache['tables']:
            return self._cache['tables'][table_id]
            
        response = self._make_request('GET', f"table/{table_id}")
        table = Table.from_api_response(response, self)
        self._cache['tables'][table_id] = table
        return table

    def get_tables(self) -> List[Table]:
        """
        Get all accessible tables.
        
        Returns:
            List[Table]: List of tables
        """
        response = self._make_request('GET', "table")
        tables = [Table.from_api_response(t, self) for t in response]
        
        # Update cache
        for table in tables:
            self._cache['tables'][table.table_id] = table
            
        return tables

    def get_table_fields(self, table_id: str) -> List[Field]:
        """
        Get all fields for a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[Field]: List of fields
        """
        cache_key = f"{table_id}_fields"
        if cache_key in self._cache['fields']:
            return self._cache['fields'][cache_key]
            
        response = self._make_request('GET', f"table/{table_id}/field")
        fields = [Field.from_api_response(f) for f in response]
        self._cache['fields'][cache_key] = fields
        return fields

    def get_table_views(self, table_id: str) -> List[View]:
        """
        Get all views for a table.
        
        Args:
            table_id: ID of the table
            
        Returns:
            List[View]: List of views
        """
        cache_key = f"{table_id}_views"
        if cache_key in self._cache['views']:
            return self._cache['views'][cache_key]
            
        response = self._make_request('GET', f"table/{table_id}/view")
        views = [View.from_api_response(v) for v in response]
        self._cache['views'][cache_key] = views
        return views

    def get_records(
        self,
        table_id: str,
        query: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get records from a table.
        
        Args:
            table_id: ID of the table
            query: Optional query parameters
            
        Returns:
            List[Dict]: List of record data
        """
        response = self._make_request(
            'GET',
            f"table/{table_id}/record",
            params=query
        )
        return response['records']

    def get_record(
        self,
        table_id: str,
        record_id: str
    ) -> Dict[str, Any]:
        """
        Get a single record by ID.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            
        Returns:
            Dict: Record data
        """
        return self._make_request(
            'GET',
            f"table/{table_id}/record/{record_id}"
        )

    def create_record(
        self,
        table_id: str,
        fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new record.
        
        Args:
            table_id: ID of the table
            fields: Field values for the record
            
        Returns:
            Dict: Created record data
        """
        response = self._make_request(
            'POST',
            f"table/{table_id}/record",
            json={'records': [{'fields': fields}]}
        )
        return response['records'][0]

    def update_record(
        self,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any]
    ) -> bool:
        """
        Update an existing record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            fields: New field values
            
        Returns:
            bool: True if successful
        """
        self._make_request(
            'PATCH',
            f"table/{table_id}/record/{record_id}",
            json={'record': {'fields': fields}}
        )
        return True

    def delete_record(
        self,
        table_id: str,
        record_id: str
    ) -> bool:
        """
        Delete a record.
        
        Args:
            table_id: ID of the table
            record_id: ID of the record
            
        Returns:
            bool: True if successful
        """
        self._make_request(
            'DELETE',
            f"table/{table_id}/record/{record_id}"
        )
        return True

    def batch_create_records(
        self,
        table_id: str,
        records: List[Dict[str, Any]],
        field_key_type: str = 'name',
        typecast: bool = False
    ) -> RecordBatch:
        """
        Create multiple records in a batch.
        
        Args:
            table_id: ID of the table
            records: List of record field values
            field_key_type: Key type for fields
            typecast: Enable automatic type conversion
            
        Returns:
            RecordBatch: Batch operation results
        """
        data = {
            'fieldKeyType': field_key_type,
            'typecast': typecast,
            'records': [{'fields': r} for r in records]
        }
        
        response = self._make_request(
            'POST',
            f"table/{table_id}/record",
            json=data
        )
        
        return RecordBatch.from_api_response(response, len(records))

    def batch_update_records(
        self,
        table_id: str,
        updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Update multiple records in a batch.
        
        Args:
            table_id: ID of the table
            updates: List of record updates
            
        Returns:
            bool: True if successful
        """
        self._make_request(
            'PATCH',
            f"table/{table_id}/record",
            json={'records': updates}
        )
        return True

    def batch_delete_records(
        self,
        table_id: str,
        record_ids: List[str]
    ) -> bool:
        """
        Delete multiple records in a batch.
        
        Args:
            table_id: ID of the table
            record_ids: List of record IDs
            
        Returns:
            bool: True if successful
        """
        self._make_request(
            'DELETE',
            f"table/{table_id}/record",
            json={'recordIds': record_ids}
        )
        return True

    def clear_cache(self) -> None:
        """Clear all cached resources."""
        self._cache = {
            'tables': {},
            'fields': {},
            'views': {}
        }
