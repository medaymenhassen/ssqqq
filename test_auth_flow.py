#!/usr/bin/env python3
"""
Test script to verify the authentication flow and identify issues with logout visibility
"""

import requests
import json
import time
import random
import string
import os
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "http://localhost:8080/api"
# Generate a random email to avoid conflicts
RANDOM_STRING = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
EMAIL = f"authtest_{RANDOM_STRING}@example.com"
PASSWORD = "authtest123"

# Global session for persistent cookies/headers
session = requests.Session()

def register_user() -> Optional[Dict[str, Any]]:
    """Register a new user for testing"""
    print("\n📝 Registering user...")
    register_data = {
        "firstname": "Auth",
        "lastname": "Tester",
        "email": EMAIL,
        "password": PASSWORD,
        "rgpdAccepted": True,
        "commercialUseConsent": True
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Register response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Registration successful")
            return response.json()
        else:
            print(f"❌ Registration failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def login_user() -> Optional[Dict[str, Any]]:
    """Login user to get authentication tokens"""
    print("\n🔐 Logging in...")
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful")
            tokens = response.json()
            # Set authorization header for future requests
            session.headers.update({
                "Authorization": f"Bearer {tokens['accessToken']}"
            })
            return tokens
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def get_user_profile(tokens: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get user profile using the access token"""
    print("\n👤 Getting user profile...")
    
    try:
        # Set authorization header
        session.headers.update({
            "Authorization": f"Bearer {tokens['accessToken']}"
        })
        
        response = session.get(f"{BASE_URL}/user/profile")
        print(f"Profile response status: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ User profile retrieved - ID: {profile.get('id')}, Email: {profile.get('email')}")
            return profile
        else:
            print(f"❌ Failed to get user profile: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        return None

def refresh_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Test token refresh functionality"""
    print("\n🔄 Testing token refresh...")
    
    refresh_data = {
        "refreshToken": refresh_token
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
        print(f"Refresh token response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token refresh successful")
            return response.json()
        else:
            print(f"❌ Token refresh failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during token refresh: {e}")
        return None

def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token to inspect its contents"""
    print("\n🔓 Decoding JWT token...")
    
    try:
        import base64
        # Split the token into parts
        parts = token.split('.')
        if len(parts) != 3:
            print("❌ Invalid JWT token format")
            return None
        
        # Decode the payload (second part)
        payload = parts[1]
        # Add padding if necessary
        payload += '=' * (4 - len(payload) % 4)
        decoded_payload = base64.b64decode(payload)
        payload_json = json.loads(decoded_payload)
        
        print("✅ JWT token decoded successfully")
        print(f"Payload: {json.dumps(payload_json, indent=2)}")
        return payload_json
    except Exception as e:
        print(f"❌ Error decoding JWT token: {e}")
        return None

def test_authentication_flow() -> bool:
    """Test the complete authentication flow"""
    print("="*60)
    print("TESTING AUTHENTICATION FLOW")
    print("="*60)
    
    # Step 1: Register user
    print("\nStep 1: User Registration")
    register_response = register_user()
    if not register_response:
        print("❌ Registration failed")
        return False
    
    # Extract tokens
    access_token = register_response.get('accessToken')
    refresh_token_str = register_response.get('refreshToken')
    
    if not access_token or not refresh_token_str:
        print("❌ Tokens not found in registration response")
        return False
    
    print(f"✅ Access token length: {len(access_token)}")
    print(f"✅ Refresh token length: {len(refresh_token_str)}")
    
    # Decode tokens to inspect contents
    decode_jwt_token(access_token)
    decode_jwt_token(refresh_token_str)
    
    # Wait a moment
    time.sleep(2)
    
    # Step 2: Get user profile with registration tokens
    print("\nStep 2: Get User Profile (using registration tokens)")
    profile = get_user_profile(register_response)
    if not profile:
        print("❌ Failed to get user profile with registration tokens")
        return False
    
    # Step 3: Login user
    print("\nStep 3: User Login")
    login_response = login_user()
    if not login_response:
        print("❌ Login failed")
        return False
    
    # Extract login tokens
    login_access_token = login_response.get('accessToken')
    login_refresh_token = login_response.get('refreshToken')
    
    if not login_access_token or not login_refresh_token:
        print("❌ Tokens not found in login response")
        return False
    
    print(f"✅ Login access token length: {len(login_access_token)}")
    print(f"✅ Login refresh token length: {len(login_refresh_token)}")
    
    # Decode login tokens
    decode_jwt_token(login_access_token)
    decode_jwt_token(login_refresh_token)
    
    # Step 4: Get user profile with login tokens
    print("\nStep 4: Get User Profile (using login tokens)")
    profile = get_user_profile(login_response)
    if not profile:
        print("❌ Failed to get user profile with login tokens")
        return False
    
    # Step 5: Test token refresh
    print("\nStep 5: Token Refresh")
    refresh_response = refresh_token(login_refresh_token)
    if not refresh_response:
        print("❌ Token refresh failed")
        return False
    
    # Extract refreshed tokens
    refreshed_access_token = refresh_response.get('accessToken')
    refreshed_refresh_token = refresh_response.get('refreshToken')
    
    if not refreshed_access_token or not refreshed_refresh_token:
        print("❌ Refreshed tokens not found in refresh response")
        return False
    
    print(f"✅ Refreshed access token length: {len(refreshed_access_token)}")
    print(f"✅ Refreshed refresh token length: {len(refreshed_refresh_token)}")
    
    # Decode refreshed tokens
    decode_jwt_token(refreshed_access_token)
    decode_jwt_token(refreshed_refresh_token)
    
    # Step 6: Get user profile with refreshed tokens
    print("\nStep 6: Get User Profile (using refreshed tokens)")
    refresh_response_copy = {
        'accessToken': refreshed_access_token,
        'refreshToken': refreshed_refresh_token
    }
    profile = get_user_profile(refresh_response_copy)
    if not profile:
        print("❌ Failed to get user profile with refreshed tokens")
        return False
    
    print("✅ Complete authentication flow test completed successfully!")
    return True

def main():
    print("🚀 Starting Authentication Flow Test")
    print(f"Using email: {EMAIL}")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Run the authentication flow test
        success = test_authentication_flow()
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        
        if success:
            print("✅ All authentication flow tests passed!")
            print("✅ Authentication system is working correctly!")
        else:
            print("❌ Some authentication flow tests failed!")
            print("❌ There may be issues with the authentication system")
            
    except Exception as e:
        print(f"💥 Unexpected error during testing: {e}")

if __name__ == "__main__":
    main()