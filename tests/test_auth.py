"""Test suite for Authentication operations."""
import os
import pytest
from teable.models.user import User
from teable.exceptions import ValidationError

def test_signin_flow(client):
    """Test signing in with email/password."""
    # Get credentials from environment
    email = os.getenv('TEABLE_EMAIL')
    password = os.getenv('TEABLE_PASSWORD')
    
    if not email or not password:
        pytest.skip("TEABLE_EMAIL and TEABLE_PASSWORD environment variables are required")
    
    # Sign in
    user = client.auth.signin(email=email, password=password)
    assert isinstance(user, User)
    assert user.email == email
    
    # Get current user info
    current_user = client.auth.get_user()
    assert isinstance(current_user, User)
    assert current_user.email == email
    
    # Sign out
    assert client.auth.signout() is True

def test_signin_validation(client):
    """Test sign in validation."""
    # Test invalid email format
    with pytest.raises(ValidationError):
        client.auth.signin(email="invalid-email", password="ValidPass1")
    
    # Test invalid password (too short)
    with pytest.raises(ValidationError):
        client.auth.signin(email="test@example.com", password="short")
    
    # Test invalid password (no uppercase)
    with pytest.raises(ValidationError):
        client.auth.signin(email="test@example.com", password="password123")
    
    # Test invalid password (no number)
    with pytest.raises(ValidationError):
        client.auth.signin(email="test@example.com", password="Password")
