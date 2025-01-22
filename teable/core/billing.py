"""
Billing management module.

This module handles operations for managing billing and subscriptions.
"""

from typing import List, Literal, TypedDict

from .http import TeableHttpClient

class SubscriptionSummary(TypedDict):
    """Type definition for subscription summary response."""
    spaceId: str
    status: Literal[
        'active', 'canceled', 'incomplete', 'incomplete_expired',
        'trialing', 'past_due', 'unpaid', 'paused', 'seat_limit_exceeded'
    ]
    level: Literal['free', 'plus', 'pro', 'enterprise']

class BillingManager:
    """
    Handles billing operations.
    
    This class manages:
    - Subscription information
    - Billing status
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the billing manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def get_subscription_summary(self, space_id: str) -> SubscriptionSummary:
        """
        Get subscription summary for a space.
        
        Args:
            space_id: ID of the space to get subscription info for
            
        Returns:
            SubscriptionSummary: Subscription information including:
                - spaceId: ID of the space
                - status: Current subscription status
                - level: Subscription tier level
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            f"/space/{space_id}/billing/subscription/summary"
        )
        
    def list_subscription_summaries(self) -> List[SubscriptionSummary]:
        """
        Get subscription summaries for all spaces.
        
        Returns:
            List[SubscriptionSummary]: List of subscription information, each containing:
                - spaceId: ID of the space
                - status: Current subscription status
                - level: Subscription tier level
            
        Raises:
            APIError: If the request fails
        """
        return self._http.request(
            'GET',
            '/billing/subscription/summary'
        )
