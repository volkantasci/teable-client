"""
Notification management module.

This module handles user notification operations including listing and managing notifications.
"""

from typing import Dict, List, Literal, Optional, TypedDict, Union

from .http import TeableHttpClient

class NotifyIcon(TypedDict, total=False):
    """Type definition for notification icon data."""
    iconUrl: str  # For system notifications
    userId: str  # For user notifications
    userName: str  # For user notifications
    userAvatarUrl: Optional[str]  # Optional user avatar URL

class Notification(TypedDict):
    """Type definition for a notification."""
    id: str
    notifyIcon: NotifyIcon
    notifyType: Literal['system', 'collaboratorCellTag', 'collaboratorMultiRowTag', 'comment']
    url: str
    message: str
    isRead: bool
    createdTime: str

class NotificationResponse(TypedDict):
    """Type definition for notification list response."""
    notifications: List[Notification]
    nextCursor: Optional[str]

class NotificationManager:
    """
    Handles notification operations.
    
    This class manages:
    - Listing notifications
    - Notification state management
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the notification manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def list_notifications(
        self,
        notify_states: Literal['unread', 'read'],
        cursor: Optional[str] = None
    ) -> NotificationResponse:
        """
        List user notifications.
        
        Args:
            notify_states: Filter notifications by state ('unread' or 'read')
            cursor: Optional cursor for pagination
            
        Returns:
            NotificationResponse: Object containing:
                - notifications: List of notifications, each containing:
                    - id: Notification ID
                    - notifyIcon: Icon data (system icon URL or user details)
                    - notifyType: Type of notification
                    - url: Associated URL
                    - message: Notification message
                    - isRead: Read status
                    - createdTime: Creation timestamp
                - nextCursor: Optional cursor for next page
            
        Raises:
            APIError: If the request fails
            ValueError: If notify_states is invalid
        """
        if notify_states not in ('unread', 'read'):
            raise ValueError("notify_states must be either 'unread' or 'read'")
            
        params: Dict[str, str] = {'notifyStates': notify_states}
        if cursor is not None:
            params['cursor'] = cursor
            
        return self._http.request(
            'GET',
            '/notifications',
            params=params
        )
        
    def update_notification_status(
        self,
        notification_id: str,
        is_read: bool
    ) -> bool:
        """
        Update the read status of a notification.
        
        Args:
            notification_id: ID of the notification to update
            is_read: New read status for the notification
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PATCH',
            f"/notifications/{notification_id}/status",
            json={'isRead': is_read}
        )
        return True
        
    def get_unread_count(self) -> int:
        """
        Get the count of unread notifications.
        
        Returns:
            int: Number of unread notifications
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request(
            'GET',
            '/notifications/unread-count'
        )
        return response['unreadCount']
        
    def mark_all_as_read(self) -> bool:
        """
        Mark all notifications as read.
        
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PATCH',
            '/notifications/read-all'
        )
        return True
