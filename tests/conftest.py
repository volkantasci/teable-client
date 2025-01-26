"""Pytest configuration file for Teable client tests."""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from teable import TeableClient, TeableConfig

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

@pytest.fixture(scope='session')
def api_key():
    """Get API key from environment variables."""
    api_key = os.getenv('TEABLE_API_KEY')
    if not api_key:
        raise ValueError('TEABLE_API_KEY environment variable is not set')
    return api_key

@pytest.fixture(scope='session')
def api_url():
    """Get API URL from environment variables."""
    api_url = os.getenv('TEABLE_API_URL', 'https://api.teable.io')
    return api_url

@pytest.fixture(scope='session')
def email():
    """Get email from environment variables."""
    email = os.getenv('TEABLE_EMAIL')
    if not email:
        raise ValueError('TEABLE_EMAIL environment variable is not set')
    return email

@pytest.fixture(scope='session')
def password():
    """Get password from environment variables."""
    password = os.getenv('TEABLE_PASSWORD')
    if not password:
        raise ValueError('TEABLE_PASSWORD environment variable is not set')
    return password

@pytest.fixture(scope='session')
def client(api_key, api_url):
    """Create a TeableClient instance."""
    config = TeableConfig(
        api_key=api_key,
        api_url=api_url
    )
    return TeableClient(config)

@pytest.fixture(scope='function')
def authenticated_client(client, email, password):
    """Create an authenticated TeableClient instance.
    
    This fixture:
    1. Takes the base client
    2. Signs in with email/password
    3. Yields the authenticated client
    4. Signs out after the test completes
    """
    # Sign in
    client.auth.signin(email=email, password=password)
    
    yield client
    
    # Sign out after test completes
    client.auth.signout()
