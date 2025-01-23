"""
HTTP client module handling API communication.
"""

import time
from typing import Any, Dict, Optional
import requests

from ..exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError
)
from ..models.config import TeableConfig

class TeableHttpClient:
    """
    Handles HTTP communication with the Teable API.
    
    This class manages:
    - HTTP request execution
    - Authentication headers
    - Error handling
    - Rate limit tracking
    """
    
    def __init__(self, config: TeableConfig):
        """
        Initialize the HTTP client.
        
        Args:
            config: Client configuration
        """
        self.config = config
        self.session = requests.Session()
        # Ensure API key is properly formatted
        api_key = self.config.api_key.strip()
        if not api_key.startswith('teable_'):
            raise AuthenticationError("Invalid API key format. Must start with 'teable_'")
            
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Rate limiting state
        self._rate_limit_remaining = 100
        self._rate_limit_reset = 0

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
        """
        Update rate limit tracking from response headers.
        
        Args:
            headers: Response headers
        """
        try:
            if 'X-RateLimit-Remaining' in headers:
                self._rate_limit_remaining = int(headers['X-RateLimit-Remaining'])
            if 'X-RateLimit-Reset' in headers:
                # Convert UTC timestamp to local time
                reset_timestamp = int(headers['X-RateLimit-Reset'])
                self._rate_limit_reset = reset_timestamp + time.timezone
        except (ValueError, TypeError) as e:
            # If headers contain invalid values, keep current limits
            pass

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
