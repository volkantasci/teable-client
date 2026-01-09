
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("TEABLE_API_URL")
API_KEY = os.getenv("TEABLE_API_KEY")
TEABLE_TEST_SPACE_ID = os.getenv("TEABLE_TEST_SPACE_ID")

print(f"URL: {API_URL}")
print(f"KEY: {API_KEY}")

def test_endpoint(endpoint):
    url = f"{API_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    print(f"\nTesting {url}...")
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    # Test User Info
    test_endpoint("/auth/user/me")
    
    # Test User Info (Alternative)
    test_endpoint("/auth/user")

    # Test Spaces List
    test_endpoint("/space")

    # Test Create Space
    url = f"{API_URL}/space"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    print(f"\nTesting POST {url}...")
    response = requests.post(url, headers=headers, json={"name": "Test Space Manual"})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

    # Test Create Base in a Space
    if TEABLE_TEST_SPACE_ID:
        base_url = f"{API_URL}/base"
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }
        print(f"\nTesting POST {base_url}...")
        response = requests.post(base_url, headers=headers, json={"spaceId": TEABLE_TEST_SPACE_ID, "name": "Test Base"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    else:
        print("\nSkipping Test Create Base: TEABLE_TEST_SPACE_ID not set.")


