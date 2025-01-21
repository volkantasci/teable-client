"""
Rate limit handling module.

This module provides functionality for tracking and enforcing API rate limits.
"""

import time
from typing import Optional

from ..exceptions import RateLimitError
from ..models.config import TeableConfig

class RateLimitHandler:
    """
    Handles API rate limit tracking and enforcement.
    
    This class manages:
    - Rate limit state tracking
    - Rate limit enforcement
    - Retry behavior
    """
    
    def __init__(self, config: TeableConfig):
        """
        Initialize the rate limit handler.
        
        Args:
            config: Client configuration
        """
        self.config = config
        self._remaining = 100  # Default rate limit
        self._reset_time = 0
        
    @property
    def remaining(self) -> int:
        """Get remaining API calls allowed."""
        return self._remaining
        
    @property
    def reset_time(self) -> int:
        """Get rate limit reset timestamp."""
        return self._reset_time
        
    def update(self, remaining: Optional[str], reset: Optional[str]) -> None:
        """
        Update rate limit state from response headers.
        
        Args:
            remaining: X-RateLimit-Remaining header value
            reset: X-RateLimit-Reset header value
        """
        if remaining is not None:
            self._remaining = int(remaining)
        if reset is not None:
            self._reset_time = int(reset)
            
    def check(self) -> None:
        """
        Check rate limit and handle if exceeded.
        
        This method will either:
        - Do nothing if within limits
        - Sleep if configured for retries
        - Raise RateLimitError if limits exceeded and no retries
        
        Raises:
            RateLimitError: If rate limit exceeded and retries not configured
        """
        if self._remaining <= 0:
            reset_time = self._reset_time - time.time()
            if reset_time > 0:
                if self.config.retry_delay is not None:
                    time.sleep(min(reset_time, self.config.retry_delay))
                else:
                    raise RateLimitError(
                        "Rate limit exceeded",
                        reset_time=self._reset_time
                    )
                    
    def handle_429(self, retry_count: int, reset_time: float) -> bool:
        """
        Handle a 429 Too Many Requests response.
        
        Args:
            retry_count: Current retry attempt number
            reset_time: Rate limit reset time from response
            
        Returns:
            bool: True if should retry, False if should raise error
            
        Raises:
            RateLimitError: If should not retry
        """
        if (self.config.max_retries is not None and
            retry_count < self.config.max_retries):
            time.sleep(self.config.retry_delay or 1)
            return True
        else:
            raise RateLimitError(
                "Rate limit exceeded",
                reset_time=reset_time
            )
