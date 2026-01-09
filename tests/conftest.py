
import os
import pytest
from dotenv import load_dotenv
from teable import TeableClient, TeableConfig

# Load environment variables from .env file
load_dotenv()

@pytest.fixture(scope="session")
def api_url():
    url = os.getenv("TEABLE_API_URL")
    if not url:
        pytest.skip("TEABLE_API_URL not set in .env")
    return url

@pytest.fixture(scope="session")
def api_key():
    key = os.getenv("TEABLE_API_KEY")
    if not key:
        pytest.skip("TEABLE_API_KEY not set in .env")
    return key

@pytest.fixture(scope="session")
def client(api_url, api_key):
    config = TeableConfig(api_url=api_url, api_key=api_key)
    return TeableClient(config)
