"""
Authentication and user management module.

This module handles user authentication, registration, and profile management.
"""

from typing import Any, Dict, Optional

from ..models.user import User
from .http import TeableHttpClient

class AuthManager:
    """
    Handles authentication and user management operations.
    
    This class manages:
    - User authentication
    - User registration
    - Profile management
    - Password operations
    """
    
    def __init__(self, http_client: TeableHttpClient):
        """
        Initialize the auth manager.
        
        Args:
            http_client: HTTP client for API communication
        """
        self._http = http_client
        
    def get_user(self) -> User:
        """
        Get current user information.
        
        Returns:
            User: Current user information
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', "auth/user")
        return User.from_api_response(response)
        
    def get_user_info(self) -> User:
        """
        Get detailed user information.
        
        Returns:
            User: Detailed user information
            
        Raises:
            APIError: If the request fails
        """
        response = self._http.request('GET', "auth/user/me")
        return User.from_api_response(response)
        
    def signin(self, email: str, password: str) -> User:
        """
        Sign in with email and password.
        
        Args:
            email: User email
            password: User password (minimum 8 chars)
            
        Returns:
            User: User information
            
        Raises:
            APIError: If the sign in fails
            ValueError: If password is less than 8 characters
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        response = self._http.request(
            'POST',
            "auth/signin",
            json={
                'email': email,
                'password': password
            }
        )
        return User.from_api_response(response)
        
    def signout(self) -> bool:
        """
        Sign out the current user.
        
        Returns:
            bool: True if sign out successful
            
        Raises:
            APIError: If the sign out fails
        """
        self._http.request('POST', "auth/signout")
        return True
        
    def signup(
        self,
        email: str,
        password: str,
        default_space_name: Optional[str] = None,
        ref_meta: Optional[Dict[str, Any]] = None,
        verification: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Sign up a new user.
        
        Args:
            email: User email
            password: User password (minimum 8 chars, must contain uppercase and number)
            default_space_name: Optional name for default space
            ref_meta: Optional reference metadata with query and referer
            verification: Optional verification with code and token
            
        Returns:
            User: User information
            
        Raises:
            APIError: If the sign up fails
            ValueError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        if not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one uppercase letter and one number")
            
        data: Dict[str, Any] = {
            'email': email,
            'password': password
        }
        
        if default_space_name:
            data['defaultSpaceName'] = default_space_name
        if ref_meta:
            data['refMeta'] = ref_meta
        if verification:
            data['verification'] = verification
            
        response = self._http.request(
            'POST',
            "auth/signup",
            json=data
        )
        return User.from_api_response(response)
        
    def update_user_name(self, name: str) -> bool:
        """
        Update user name.
        
        Args:
            name: New name for the user
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PATCH',
            "user/name",
            json={'name': name}
        )
        return True
        
    def update_user_avatar(self, avatar_data: bytes) -> bool:
        """
        Update user avatar.
        
        Args:
            avatar_data: Binary image data for avatar
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PATCH',
            "user/avatar",
            files={'file': ('avatar', avatar_data, 'image/*')}
        )
        return True
        
    def update_user_notify_meta(self, email: bool) -> bool:
        """
        Update user notification settings.
        
        Args:
            email: Whether to enable email notifications
            
        Returns:
            bool: True if update successful
            
        Raises:
            APIError: If the update fails
        """
        self._http.request(
            'PATCH',
            "user/notify-meta",
            json={'email': email}
        )
        return True
        
    def send_change_email_code(self, email: str, password: str) -> Dict[str, str]:
        """
        Send email change verification code.
        
        Args:
            email: New email address
            password: Current password
            
        Returns:
            Dict[str, str]: Response containing verification token
            
        Raises:
            APIError: If sending code fails
        """
        return self._http.request(
            'POST',
            "auth/send-change-email-code",
            json={
                'email': email,
                'password': password
            }
        )
        
    def change_email(self, email: str, token: str, code: str) -> bool:
        """
        Change email address.
        
        Args:
            email: New email address
            token: Verification token
            code: Verification code
            
        Returns:
            bool: True if email change successful
            
        Raises:
            APIError: If the email change fails
        """
        self._http.request(
            'PATCH',
            "auth/change-email",
            json={
                'email': email,
                'token': token,
                'code': code
            }
        )
        return True
        
    def send_signup_verification_code(self, email: str) -> Dict[str, str]:
        """
        Send signup verification code.
        
        Args:
            email: User email
            
        Returns:
            Dict[str, str]: Response containing verification token and expiry
            
        Raises:
            APIError: If sending code fails
        """
        return self._http.request(
            'POST',
            "auth/send-signup-verification-code",
            json={'email': email}
        )
        
    def add_password(self, password: str) -> bool:
        """
        Add password for user.
        
        Args:
            password: Password to add (minimum 8 chars, must contain uppercase and number)
            
        Returns:
            bool: True if password added successfully
            
        Raises:
            APIError: If adding password fails
            ValueError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        if not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one uppercase letter and one number")
            
        self._http.request(
            'POST',
            "auth/add-password",
            json={'password': password}
        )
        return True
        
    def reset_password(self, password: str, code: str) -> bool:
        """
        Reset user password.
        
        Args:
            password: New password (minimum 8 chars, must contain uppercase and number)
            code: Reset code from email
            
        Returns:
            bool: True if password reset successful
            
        Raises:
            APIError: If the password reset fails
            ValueError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        if not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one uppercase letter and one number")
            
        self._http.request(
            'POST',
            "auth/reset-password",
            json={
                'password': password,
                'code': code
            }
        )
        return True
        
    def send_reset_password_email(self, email: str) -> bool:
        """
        Send reset password email.
        
        Args:
            email: User email
            
        Returns:
            bool: True if email sent successfully
            
        Raises:
            APIError: If sending email fails
        """
        self._http.request(
            'POST',
            "auth/send-reset-password-email",
            json={'email': email}
        )
        return True
        
    def change_password(self, password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            password: Current password
            new_password: New password (minimum 8 chars, must contain uppercase and number)
            
        Returns:
            bool: True if password change successful
            
        Raises:
            APIError: If the password change fails
            ValueError: If new password doesn't meet requirements
        """
        if len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters")
            
        if not any(c.isupper() for c in new_password) or not any(c.isdigit() for c in new_password):
            raise ValueError("New password must contain at least one uppercase letter and one number")
            
        self._http.request(
            'PATCH',
            "auth/change-password",
            json={
                'password': password,
                'newPassword': new_password
            }
        )
        return True
