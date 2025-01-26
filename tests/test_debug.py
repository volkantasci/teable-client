import os
import pytest
from datetime import datetime

def write_debug(msg):
    with open('debug.log', 'a') as f:
        f.write(f"{datetime.now()}: {msg}\n")

def test_debug():
    write_debug("Starting test")
    try:
        from teable import TeableClient, TeableConfig
        write_debug("Imported teable")
        
        # Load env vars
        api_key = os.getenv('TEABLE_API_KEY')
        api_url = os.getenv('TEABLE_API_URL')
        email = os.getenv('TEABLE_EMAIL')
        password = os.getenv('TEABLE_PASSWORD')
        
        write_debug(f"Env vars: url={api_url}, email={email}, password={password}")
        
        # Create client
        config = TeableConfig(api_key=api_key, api_url=api_url)
        client = TeableClient(config)
        write_debug("Created client")
        
        # Create signin data
        signin_data = {
            'email': email,
            'password': password
        }
        write_debug(f"Signin data: {signin_data}")
        
        # Try to sign in
        user = client.auth.signin(**signin_data)
        write_debug(f"Signed in as {user.email}")
        
        # Sign out
        client.auth.signout()
        write_debug("Signed out")
        
    except Exception as e:
        write_debug(f"Error: {str(e)}")
        raise
