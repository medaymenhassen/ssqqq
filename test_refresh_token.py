#!/usr/bin/env python3
"""
Script to test the refresh token functionality and reproduce the error:
"auth.service.ts:176 ❌ Could not refresh token"
"""

import requests
import json
import time
import random
import string

# Configuration
BASE_URL = "http://localhost:8080/api"
# Generate a random email to avoid conflicts
RANDOM_STRING = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
EMAIL = f"test_{RANDOM_STRING}@example.com"
PASSWORD = "testpassword123"

def register_user():
    """Register a new user"""
    print("📝 Registering user...")
    register_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": EMAIL,
        "password": PASSWORD,
        "rgpdAccepted": True,
        "commercialUseConsent": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Register response status: {response.status_code}")
        print(f"Register response: {response.json()}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def login_user():
    """Login user to get tokens"""
    print("\n🔐 Logging in...")
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        print(f"Login response: {response.json()}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_refresh_token(refresh_token):
    """Test refresh token functionality"""
    print("\n🔄 Testing refresh token...")
    refresh_data = {
        "refreshToken": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
        print(f"Refresh token response status: {response.status_code}")
        print(f"Refresh token response: {response.json()}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ Error during refresh token: {e}")
        return None

def main():
    print(f"🚀 Starting refresh token test with email: {EMAIL}")
    
    # Step 1: Register user
    register_response = register_user()
    if not register_response:
        print("❌ Registration failed, exiting...")
        return
    
    # Small delay to ensure user is properly created
    time.sleep(1)
    
    # Step 2: Login to get tokens
    login_response = login_user()
    if not login_response:
        print("❌ Login failed, exiting...")
        return
    
    # Step 3: Test refresh token
    refresh_token = login_response.get("refreshToken")
    if not refresh_token:
        print("❌ No refresh token found in login response")
        return
    
    refresh_response = test_refresh_token(refresh_token)
    if not refresh_response:
        print("❌ Refresh token test failed")
        return
    
    print("✅ All tests passed!")
    
    # Step 4: Test with invalid refresh token to reproduce the error
    print("\n🧪 Testing with invalid refresh token...")
    invalid_refresh_response = test_refresh_token("invalid.token.here")
    if not invalid_refresh_response:
        print("✅ Invalid token test behaved as expected (returned error)")
    else:
        print("❌ Invalid token test should have failed")

if __name__ == "__main__":
    main()