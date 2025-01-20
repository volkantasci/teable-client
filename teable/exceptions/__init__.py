"""
Teable Client Exceptions Module

This module defines the exception hierarchy used throughout the Teable client library.
All custom exceptions inherit from TeableError to allow for specific error handling.
"""

from typing import Optional


class TeableError(Exception):
    """Base exception class for all Teable-related errors."""
    pass


class APIError(TeableError):
    """
    Exception raised when the Teable API returns an error response.
    
    Attributes:
        message (str): Human-readable error description
        status_code (Optional[int]): HTTP status code if available
        response_body (Optional[str]): Raw response body if available
    """
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_body: Optional[str] = None
    ):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class ValidationError(TeableError):
    """
    Exception raised when data validation fails.
    
    This could be due to:
    - Invalid field types
    - Missing required fields
    - Value constraints violations
    """
    pass


class ConfigurationError(TeableError):
    """
    Exception raised when there are issues with client configuration.
    
    This could be due to:
    - Missing API credentials
    - Invalid API URL
    - Missing required configuration parameters
    """
    pass


class RateLimitError(APIError):
    """
    Exception raised when API rate limits are exceeded.
    
    Attributes:
        reset_time (Optional[float]): Unix timestamp when the rate limit resets
        limit (Optional[int]): The rate limit ceiling for the given endpoint
    """
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = 429,
        reset_time: Optional[float] = None,
        limit: Optional[int] = None
    ):
        self.reset_time = reset_time
        self.limit = limit
        super().__init__(message, status_code)


class ResourceNotFoundError(APIError):
    """
    Exception raised when a requested resource is not found.
    
    This could be due to:
    - Invalid record ID
    - Invalid table ID
    - Invalid view ID
    - Invalid field ID
    """
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: str,
        status_code: Optional[int] = 404
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            f"{message} ({resource_type}: {resource_id})",
            status_code
        )


class AuthenticationError(APIError):
    """
    Exception raised when authentication fails.
    
    This could be due to:
    - Invalid API key
    - Expired credentials
    - Insufficient permissions
    """
    def __init__(self, message: str, status_code: Optional[int] = 401):
        super().__init__(message, status_code)


class NetworkError(TeableError):
    """
    Exception raised when network-related issues occur.
    
    This could be due to:
    - Connection timeouts
    - DNS resolution failures
    - SSL/TLS errors
    """
    pass


class BatchOperationError(TeableError):
    """
    Exception raised when a batch operation partially fails.
    
    Attributes:
        successful_operations (list): List of successfully processed items
        failed_operations (list): List of failed operations with their errors
    """
    def __init__(
        self,
        message: str,
        successful_operations: list,
        failed_operations: list
    ):
        self.successful_operations = successful_operations
        self.failed_operations = failed_operations
        super().__init__(message)
