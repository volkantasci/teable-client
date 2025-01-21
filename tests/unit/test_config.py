"""
Unit tests for the TeableConfig class.
"""

import pytest

from teable import TeableConfig
from teable.exceptions import ConfigurationError


def test_config_initialization():
    """Test basic configuration initialization."""
    config = TeableConfig(
        api_url="https://api.example.com",
        api_key="test-key"
    )
    assert config.api_url == "https://api.example.com"
    assert config.api_key == "test-key"
    assert config.timeout == 30.0  # default value
    assert config.max_retries == 3  # default value
    assert config.retry_delay == 1.0  # default value


def test_config_validation():
    """Test configuration validation."""
    # Test missing API URL
    with pytest.raises(ConfigurationError, match="API URL is required"):
        TeableConfig(api_url="", api_key="test-key")

    # Test missing API key
    with pytest.raises(ConfigurationError, match="API key is required"):
        TeableConfig(api_url="https://api.example.com", api_key="")

    # Test invalid URL format
    with pytest.raises(ConfigurationError, match="Invalid API URL"):
        TeableConfig(api_url="not-a-url", api_key="test-key")

    # Test invalid timeout
    with pytest.raises(ConfigurationError, match="Timeout must be positive"):
        TeableConfig(
            api_url="https://api.example.com",
            api_key="test-key",
            timeout=-1
        )

    # Test invalid retry settings
    with pytest.raises(ConfigurationError, match="Max retries cannot be negative"):
        TeableConfig(
            api_url="https://api.example.com",
            api_key="test-key",
            max_retries=-1
        )


def test_config_from_dict():
    """Test configuration creation from dictionary."""
    config_dict = {
        "api_url": "https://api.example.com",
        "api_key": "test-key",
        "timeout": 60.0,
        "max_retries": 5,
        "retry_delay": 2.0
    }
    
    config = TeableConfig.from_dict(config_dict)
    assert config.api_url == config_dict["api_url"]
    assert config.api_key == config_dict["api_key"]
    assert config.timeout == config_dict["timeout"]
    assert config.max_retries == config_dict["max_retries"]
    assert config.retry_delay == config_dict["retry_delay"]


def test_config_to_dict():
    """Test configuration conversion to dictionary."""
    config = TeableConfig(
        api_url="https://api.example.com",
        api_key="test-key",
        timeout=60.0,
        max_retries=5,
        retry_delay=2.0
    )
    
    config_dict = config.to_dict()
    assert config_dict["api_url"] == config.api_url
    assert config_dict["api_key"] == config.api_key
    assert config_dict["timeout"] == config.timeout
    assert config_dict["max_retries"] == config.max_retries
    assert config_dict["retry_delay"] == config.retry_delay


def test_base_url_property():
    """Test base_url property normalization."""
    config = TeableConfig(
        api_url="https://api.example.com/",  # with trailing slash
        api_key="test-key"
    )
    assert config.base_url == "https://api.example.com"  # without trailing slash

    config = TeableConfig(
        api_url="https://api.example.com",  # without trailing slash
        api_key="test-key"
    )
    assert config.base_url == "https://api.example.com"  # still without trailing slash
