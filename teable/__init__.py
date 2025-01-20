"""
Teable Client Library

A professional Python client library for interacting with the Teable API.
Provides an object-oriented interface for managing tables, records, fields, and views.
"""

__version__ = "1.0.0"

from .core.client import TeableClient
from .exceptions import (
    TeableError,
    APIError,
    AuthenticationError,
    BatchOperationError,
    ConfigurationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError
)
from .models.config import TeableConfig
from .models.field import Field, FieldType
from .models.record import Record, RecordBatch
from .models.table import Table
from .models.view import (
    View,
    QueryBuilder,
    FilterOperator,
    SortDirection,
    FilterCondition,
    SortCondition
)

__all__ = [
    # Core
    'TeableClient',
    'TeableConfig',
    
    # Models
    'Table',
    'Record',
    'RecordBatch',
    'Field',
    'FieldType',
    'View',
    'QueryBuilder',
    'FilterOperator',
    'SortDirection',
    'FilterCondition',
    'SortCondition',
    
    # Exceptions
    'TeableError',
    'APIError',
    'AuthenticationError',
    'BatchOperationError',
    'ConfigurationError',
    'NetworkError',
    'RateLimitError',
    'ResourceNotFoundError',
    'ValidationError',
    
    # Version
    '__version__'
]
