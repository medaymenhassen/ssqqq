#!/usr/bin/env python3
"""
Test to verify authenticated access to user profile endpoint
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
EMAIL = f"auth_{RANDOM_STRING}@example.com"
PASSWORD = "authpassword123"

def register_user():
    """Register a new user"""
    print("📝 Registering user...")
    register_data = {
        "firstname": "Auth",
        "lastname": "Test",
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

def get_user_profile(access_token):
    """Get user profile using access token"""
    print("\n👤 Getting user profile with authentication...")
    
    try:
        response = requests.get(f"{BASE_URL}/user/profile", 
                              headers={"Authorization": f"Bearer {access_token}"})
        print(f"Profile response status: {response.status_code}")
        if response.status_code == 200:
            print("✅ User profile retrieved successfully")
            return response.json()
        else:
            print(f"❌ Failed to get user profile: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        return None

def refresh_token(refresh_token):
    """Refresh token using the refresh endpoint"""
    print("\n🔄 Refreshing token...")
    refresh_data = {
        "refreshToken": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
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

def test_authenticated_access():
    """Test authenticated access to profile endpoint"""
    print("🚀 Testing authenticated access to profile endpoint...")
    
    # Step 1: Register
    register_response = register_user()
    if not register_response:
        return False
    
    time.sleep(2)  # Wait for user creation
    
    # Step 2: Login
    login_response = login_user()
    if not login_response:
        return False
    
    access_token = login_response.get("accessToken")
    refresh_token_str = login_response.get("refreshToken")
    
    if not access_token or not refresh_token_str:
        print("❌ Missing tokens in login response")
        return False
    
    print(f"\n🔑 Got tokens:")
    print(f"   Access Token (first 30 chars): {access_token[:30]}...")
    
    # Step 3: Get user profile with authentication
    profile_response = get_user_profile(access_token)
    if profile_response:
        print(f"   User: {profile_response.get('firstname')} {profile_response.get('lastname')}")
        print(f"   Email: {profile_response.get('email')}")
        print(f"   Role: {profile_response.get('role')}")
        return True
    else:
        print("❌ Failed to get user profile with authentication")
        return False

def test_refresh_then_profile():
    """Test refresh token then access profile with new token"""
    print("\n" + "="*50)
    print("TESTING REFRESH THEN PROFILE ACCESS")
    print("="*50)
    
    # Login
    login_response = login_user()
    if not login_response:
        return False
    
    access_token = login_response.get("accessToken")
    refresh_token_str = login_response.get("refreshToken")
    
    # Refresh token
    refresh_response = refresh_token(refresh_token_str)
    if not refresh_response:
        return False
    
    new_access_token = refresh_response.get("accessToken")
    print(f"\n🆕 Got new access token: {new_access_token[:30]}...")
    
    # Access profile with new token
    profile_response = get_user_profile(new_access_token)
    if profile_response:
        print(f"   User: {profile_response.get('firstname')} {profile_response.get('lastname')}")
        print("✅ Successfully accessed profile with refreshed token")
        return True
    else:
        print("❌ Failed to access profile with refreshed token")
        return False

def main():
    print(f"🚀 Starting authenticated profile access test...")
    print(f"Using email: {EMAIL}")
    
    # Test authenticated access
    auth_success = test_authenticated_access()
    
    # Test refresh then profile access
    refresh_success = test_refresh_then_profile()
    
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    
    if auth_success and refresh_success:
        print("✅ All authenticated access tests passed!")
        print("✅ Backend security and authentication are working correctly!")
    else:
        print("❌ Some authenticated access tests failed!")
        if not auth_success:
            print("   - Direct profile access failed")
        if not refresh_success:
            print("   - Refresh then profile access failed")

if __name__ == "__main__":
    main()