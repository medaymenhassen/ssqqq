#!/usr/bin/env python3
"""
Manual test script to verify the profile endpoint is working correctly
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8080/api"
EMAIL = "test@example.com"
PASSWORD = "password123"

def register_user():
    """Register a test user"""
    register_data = {
        "firstname": "Test",
        "lastname": "User",
        "email": EMAIL,
        "password": PASSWORD,
        "rgpdAccepted": True,
        "ccpaAccepted": False,
        "commercialUseConsent": True
    }
    
    print("Registering user...")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Register response status: {response.status_code}")
    print(f"Register response: {response.text}")
    
    if response.status_code == 200:
        return response.json()
    return None

def login_user():
    """Login the test user"""
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    print("\nLogging in user...")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.text}")
    
    if response.status_code == 200:
        return response.json()
    return None

def get_profile(token):
    """Get user profile"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("\nGetting user profile...")
    response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
    print(f"Profile response status: {response.status_code}")
    print(f"Profile response headers: {dict(response.headers)}")
    print(f"Profile response: {response.text}")
    
    return response

def main():
    print("Testing profile endpoint...")
    
    # Register user
    register_response = register_user()
    if not register_response:
        print("Failed to register user")
        return
    
    # Login user
    login_response = login_user()
    if not login_response:
        print("Failed to login user")
        return
    
    # Get access token
    access_token = login_response.get("accessToken")
    if not access_token:
        print("No access token in login response")
        return
    
    print(f"\nAccess token: {access_token[:50]}...")
    
    # Get profile
    profile_response = get_profile(access_token)
    
    if profile_response.status_code == 200:
        print("\n✅ Profile endpoint is working correctly!")
        print(f"User profile: {profile_response.json()}")
    else:
        print(f"\n❌ Profile endpoint failed with status {profile_response.status_code}")
        print("Headers sent:")
        print(f"  Authorization: Bearer {access_token[:20]}...")

if __name__ == "__main__":
    main()