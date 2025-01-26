"""
HTTP client module for making API requests.
"""

import time
import json
from typing import Any, Dict, Optional, Union
import requests
from ..models.config import TeableConfig
from ..exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError
)

class TeableHttpClient:
    """
    HTTP client for making API requests.
    
    This class handles:
    - API request execution
    - Rate limit tracking
    - Error handling and conversion to domain exceptions
    """
    
    def __init__(
        self,
        base_url: Union[str, TeableConfig],
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1
    ):
        """
        Initialize the HTTP client.
        
        Args:
            base_url: Base URL for API requests
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for rate limited requests
            retry_delay: Delay between retries in seconds
        """
        if isinstance(base_url, TeableConfig):
            self.config = Config(
                base_url=base_url.api_url,
                api_key=base_url.api_key,
                timeout=base_url.timeout,
                max_retries=base_url.max_retries,
                retry_delay=base_url.retry_delay
            )
        else:
            self.config = Config(
                base_url=base_url,
                api_key=api_key,
                timeout=timeout,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
        
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
            
        self._rate_limit = None
        self._rate_limit_remaining = None
        self._rate_limit_reset = None
        
    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
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
        
        # Handle request parameters
        if 'params' in kwargs:
            new_params = {}
            for key, value in kwargs['params'].items():
                if isinstance(value, str):
                    # If it's a string, try to parse it as JSON
                    try:
                        parsed_value = json.loads(value)
                        if key == 'search':
                            new_params[key] = parsed_value if isinstance(parsed_value, list) else [parsed_value]
                        elif key in ['recordIds', 'recordIds[]']:
                            new_params['recordIds'] = parsed_value if isinstance(parsed_value, list) else [parsed_value]
                        else:
                            new_params[key] = value
                    except json.JSONDecodeError:
                        new_params[key] = value
                elif isinstance(value, (list, dict)):
                    # Handle non-string complex values
                    if key == 'search':
                        # Convert search object to array format
                        if isinstance(value, list):
                            if all(isinstance(item, dict) for item in value):
                                # Convert dict format to array format
                                search_array = []
                                for item in value:
                                    search_array.append([
                                        str(item['value']),
                                        str(item['field']),
                                        str(item['exact']).lower()
                                    ])
                                new_params[key] = search_array
                            else:
                                # Already in array format
                                new_params[key] = value
                        else:
                            new_params[key] = [value]
                    elif key == 'filter':
                        new_params[key] = json.dumps(value)
                    elif key in ['recordIds', 'recordIds[]']:
                        new_params['recordIds'] = value if isinstance(value, list) else [value]
                    else:
                        new_params[key] = json.dumps(value)
                else:
                    new_params[key] = value
            kwargs['params'] = new_params

        # Convert json body if it contains lists or dicts
        if 'json' in kwargs:
            data = kwargs['json']
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        data[key] = list(value)  # Convert to proper list
        
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
                # Handle empty responses (like from signout)
                if not response.content:
                    return None
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
                raise APIError(str(e))
                
    def _update_rate_limits(self, headers: Dict[str, str]) -> None:
        """Update rate limit tracking from response headers."""
        self._rate_limit = headers.get('X-RateLimit-Limit')
        self._rate_limit_remaining = headers.get('X-RateLimit-Remaining')
        self._rate_limit_reset = headers.get('X-RateLimit-Reset')
        
    def _check_rate_limit(self) -> None:
        """Check if we are currently rate limited."""
        if (self._rate_limit_remaining is not None and
            int(self._rate_limit_remaining) <= 0):
            reset_time = float(self._rate_limit_reset or 0)
            raise RateLimitError(
                "Rate limit exceeded",
                429,
                reset_time=reset_time
            )
            
class Config:
    """Configuration for the HTTP client."""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: Optional[int] = 3,
        retry_delay: Optional[int] = 1
    ):
        """
        Initialize configuration.
        
        Args:
            base_url: Base URL for API requests
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for rate limited requests
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
