"""
Configuration Models Module

This module defines the configuration models used to initialize and manage
the Teable client settings.
"""

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from ..exceptions import ConfigurationError


@dataclass
class TeableConfig:
    """
    Configuration class for Teable API connection settings.
    
    Attributes:
        api_url (str): Base URL for the Teable API
        api_key (str): Authentication token for API access
        default_table_id (Optional[str]): Default table ID for operations
        default_view_id (Optional[str]): Default view ID for operations
        timeout (Optional[float]): Request timeout in seconds
        max_retries (Optional[int]): Maximum number of retry attempts
        retry_delay (Optional[float]): Delay between retries in seconds
    """
    api_url: str
    api_key: str
    default_table_id: Optional[str] = None
    default_view_id: Optional[str] = None
    timeout: Optional[float] = 30.0
    max_retries: Optional[int] = 3
    retry_delay: Optional[float] = 1.0

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate the configuration settings.
        
        Raises:
            ConfigurationError: If any configuration values are invalid
        """
        if not self.api_url:
            raise ConfigurationError("API URL is required")
        if not self.api_key:
            raise ConfigurationError("API key is required")
        if not self.api_key.strip().startswith('teable_'):
            raise ConfigurationError("API key must start with 'teable_'")
        
        # Validate URL format
        try:
            parsed_url = urlparse(self.api_url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise ValueError("Invalid URL format")
            if not parsed_url.scheme in ['http', 'https']:
                raise ValueError("URL scheme must be http or https")
            # Remove trailing slashes and normalize URL
            base = f"{parsed_url.scheme}://{parsed_url.netloc.rstrip('/')}{parsed_url.path.rstrip('/')}"
            # Ensure /api is in the path
            if not base.endswith('/api'):
                base = f"{base}/api"
            self.api_url = base
        except Exception as e:
            raise ConfigurationError(f"Invalid API URL: {str(e)}")
        
        # Validate timeout
        if self.timeout is not None and self.timeout <= 0:
            raise ConfigurationError("Timeout must be positive")
        
        # Validate retry settings
        if self.max_retries is not None and self.max_retries < 0:
            raise ConfigurationError("Max retries cannot be negative")
        if self.retry_delay is not None and self.retry_delay < 0:
            raise ConfigurationError("Retry delay cannot be negative")

    @property
    def base_url(self) -> str:
        """
        Get the normalized base URL for API requests.
        
        Returns:
            str: Normalized base URL without trailing slash
        """
        return self.api_url.rstrip('/')

    @classmethod
    def from_dict(cls, config_dict: dict) -> 'TeableConfig':
        """
        Create a TeableConfig instance from a dictionary.
        
        Args:
            config_dict (dict): Dictionary containing configuration values
            
        Returns:
            TeableConfig: New configuration instance
            
        Raises:
            ConfigurationError: If required fields are missing
        """
        try:
            return cls(**{
                k: v for k, v in config_dict.items()
                if k in cls.__annotations__
            })
        except TypeError as e:
            raise ConfigurationError(f"Invalid configuration: {str(e)}")

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary format.
        
        Returns:
            dict: Configuration as dictionary
        """
        return {
            'api_url': self.api_url,
            'api_key': self.api_key,
            'default_table_id': self.default_table_id,
            'default_view_id': self.default_view_id,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay
        }
