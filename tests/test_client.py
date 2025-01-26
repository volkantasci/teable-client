"""Test suite for TeableClient initialization and configuration."""
import os
import pytest
from teable import TeableClient
from teable.exceptions import ConfigurationError
from teable.models.config import TeableConfig
from teable.models.user import User

def test_client_init_with_dict(api_key, api_url, client):
    """Test client initialization with dictionary configuration."""
    # Sign in with original client
    email = os.getenv('TEABLE_EMAIL')
    password = os.getenv('TEABLE_PASSWORD')
    user = client.auth.signin(email=email, password=password)
    assert isinstance(user, User)
    
    # Test new client initialization
    config = {
        'api_key': api_key,
        'api_url': api_url,
        'timeout': 60.0,
        'max_retries': 5
    }
    new_client = TeableClient(config)
    assert isinstance(new_client.config, TeableConfig)
    assert new_client.config.api_key == api_key
    assert new_client.config.api_url.endswith('/api')
    assert new_client.config.timeout == 60.0
    assert new_client.config.max_retries == 5
    
    # Sign out with original client
    assert client.auth.signout() is True

def test_client_init_with_config_object(api_key, api_url, client):
    """Test client initialization with TeableConfig object."""
    # Sign in with original client
    email = os.getenv('TEABLE_EMAIL')
    password = os.getenv('TEABLE_PASSWORD')
    user = client.auth.signin(email=email, password=password)
    assert isinstance(user, User)
    
    # Test new client initialization
    config = TeableConfig(
        api_key=api_key,
        api_url=api_url,
        timeout=45.0
    )
    new_client = TeableClient(config)
    assert new_client.config is config
    assert new_client.config.timeout == 45.0
    
    # Sign out with original client
    assert client.auth.signout() is True

def test_invalid_api_key():
    """Test client initialization with invalid API key."""
    with pytest.raises(ConfigurationError, match="API key must start with 'teable_'"):
        TeableClient({
            'api_key': 'invalid_key',
            'api_url': 'https://api.teable.io'
        })

def test_invalid_api_url():
    """Test client initialization with invalid API URL."""
    with pytest.raises(ConfigurationError, match="Invalid API URL"):
        TeableClient({
            'api_key': 'teable_test_key',
            'api_url': 'not_a_url'
        })

def test_missing_required_config():
    """Test client initialization with missing required configuration."""
    with pytest.raises(ConfigurationError):
        TeableClient({
            'api_url': 'https://api.teable.io'
        })

def test_invalid_timeout():
    """Test client initialization with invalid timeout."""
    with pytest.raises(ConfigurationError, match="Timeout must be positive"):
        TeableClient({
            'api_key': 'teable_test_key',
            'api_url': 'https://api.teable.io',
            'timeout': -1
        })

def test_client_managers_initialization(client):
    # Sign in
    email = os.getenv('TEABLE_EMAIL')
    password = os.getenv('TEABLE_PASSWORD')
    user = client.auth.signin(email=email, password=password)
    assert isinstance(user, User)
    
    """Test that all managers are properly initialized."""
    assert client.spaces is not None
    assert client.tables is not None
    assert client.records is not None
    assert client.fields is not None
    assert client.views is not None
    assert client.attachments is not None
    assert client.selection is not None
    assert client.notifications is not None
    assert client.access_tokens is not None
    assert client.imports is not None
    assert client.exports is not None
    assert client.pins is not None
    assert client.billing is not None
    assert client.admin is not None
    assert client.usage is not None
    assert client.oauth is not None
    assert client.undo_redo is not None
    assert client.plugins is not None
    assert client.comments is not None
    assert client.organizations is not None
    assert client.ai is not None
    assert client.integrity is not None
    assert client.aggregation is not None
    
    # Sign out
    assert client.auth.signout() is True

def test_clear_cache(client):
    # Sign in
    email = os.getenv('TEABLE_EMAIL')
    password = os.getenv('TEABLE_PASSWORD')
    user = client.auth.signin(email=email, password=password)
    assert isinstance(user, User)
    
    """Test cache clearing functionality."""
    # First ensure we can clear cache without errors
    client.clear_cache()
    # This is a basic test since we can't easily verify cache state
    # More detailed cache testing would be done in integration tests
    
    # Sign out
    assert client.auth.signout() is True
