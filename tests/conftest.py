
import os
import pytest
from dotenv import load_dotenv
from teable import TeableClient, TeableConfig

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

@pytest.fixture(scope="session")
def authenticated_client(api_url, api_key):
    email = os.getenv("TEABLE_AUTH_EMAIL")
    password = os.getenv("TEABLE_AUTH_PASSWORD")
    if not email or not password:
        pytest.skip("TEABLE_AUTH_EMAIL and TEABLE_AUTH_PASSWORD not set in .env")
    config = TeableConfig(api_url=api_url, api_key=api_key)
    client = TeableClient(config)
    client.auth.signin(email=email, password=password)
    return client
