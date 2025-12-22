#!/usr/bin/env python3
"""
Debug script to reproduce and fix the refresh token error:
"auth.service.ts:176 ❌ Could not refresh token"
"""

import requests
import json
import time
import random
import string
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8080/api"
# Generate a random email to avoid conflicts
RANDOM_STRING = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
EMAIL = f"debug_{RANDOM_STRING}@example.com"
PASSWORD = "debugpassword123"

def register_user():
    """Register a new user"""
    print("📝 Registering user...")
    register_data = {
        "firstname": "Debug",
        "lastname": "User",
        "email": EMAIL,
        "password": PASSWORD,
        "rgpdAccepted": True,
        "commercialUseConsent": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
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
        if response.status_code == 200:
            print("✅ Login successful")
            return response.json()
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_refresh_token_valid(refresh_token):
    """Test refresh token with valid token"""
    print("\n🔄 Testing refresh token with VALID token...")
    refresh_data = {
        "refreshToken": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
        print(f"Refresh token response status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Refresh token successful")
            return response.json()
        else:
            print(f"❌ Refresh token failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during refresh token: {e}")
        return None

def test_refresh_token_invalid():
    """Test refresh token with invalid token"""
    print("\n🔄 Testing refresh token with INVALID token...")
    refresh_data = {
        "refreshToken": "invalid.token.string"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
        print(f"Refresh token response status: {response.status_code}")
        if response.status_code == 200:
            print("❌ Invalid token should have failed but didn't")
            return response.json()
        else:
            print("✅ Invalid token correctly rejected")
            print(f"Error response: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during refresh token: {e}")
        return None

def test_refresh_token_missing():
    """Test refresh token with missing token"""
    print("\n🔄 Testing refresh token with MISSING token...")
    refresh_data = {
        # No refreshToken field
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
        print(f"Refresh token response status: {response.status_code}")
        if response.status_code == 200:
            print("❌ Missing token should have failed but didn't")
            return response.json()
        else:
            print("✅ Missing token correctly rejected")
            print(f"Error response: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during refresh token: {e}")
        return None

def test_refresh_token_empty():
    """Test refresh token with empty token"""
    print("\n🔄 Testing refresh token with EMPTY token...")
    refresh_data = {
        "refreshToken": ""
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
        print(f"Refresh token response status: {response.status_code}")
        if response.status_code == 200:
            print("❌ Empty token should have failed but didn't")
            return response.json()
        else:
            print("✅ Empty token correctly rejected")
            print(f"Error response: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during refresh token: {e}")
        return None

def simulate_expired_token_scenario():
    """Simulate a scenario where token might be expired"""
    print("\n⏰ Simulating expired token scenario...")
    
    # First, login to get a fresh token
    login_response = login_user()
    if not login_response:
        return False
    
    refresh_token = login_response.get("refreshToken")
    if not refresh_token:
        print("❌ No refresh token in login response")
        return False
    
    # Wait a moment
    time.sleep(1)
    
    # Try to refresh the token
    refresh_response = test_refresh_token_valid(refresh_token)
    if refresh_response:
        print("✅ Token refresh worked even after small delay")
        return True
    else:
        print("❌ Token refresh failed after small delay")
        return False

def main():
    print(f"🚀 Starting refresh token debug test at {datetime.now()}")
    print(f"Using email: {EMAIL}")
    
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
    
    # Step 3: Extract tokens
    refresh_token = login_response.get("refreshToken")
    if not refresh_token:
        print("❌ No refresh token found in login response")
        return
    
    print(f"\n🔑 Got refresh token (first 50 chars): {refresh_token[:50]}...")
    
    # Step 4: Test various refresh token scenarios
    print("\n" + "="*50)
    print("TESTING REFRESH TOKEN SCENARIOS")
    print("="*50)
    
    # Test 1: Valid refresh token
    refresh_response = test_refresh_token_valid(refresh_token)
    
    # Test 2: Invalid refresh token
    test_refresh_token_invalid()
    
    # Test 3: Missing refresh token
    test_refresh_token_missing()
    
    # Test 4: Empty refresh token
    test_refresh_token_empty()
    
    # Test 5: Expired token simulation
    simulate_expired_token_scenario()
    
    print("\n" + "="*50)
    print("DEBUG TEST COMPLETE")
    print("="*50)
    
    if refresh_response:
        print("✅ All critical tests passed!")
    else:
        print("❌ Some tests failed!")

if __name__ == "__main__":
    main()