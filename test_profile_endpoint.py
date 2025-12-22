#!/usr/bin/env python3
"""
Test script to specifically test the profile endpoint
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
EMAIL = f"profiletest_{RANDOM_STRING}@example.com"
PASSWORD = "profiletest123"

# Global session for persistent cookies/headers
session = requests.Session()

def register_user() -> Optional[Dict[str, Any]]:
    """Register a new user for testing"""
    print(f"\n📝 Registering user: {EMAIL}")
    register_data = {
        "firstname": "Profile",
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
            print(f"❌ Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def get_user_profile(access_token: str) -> Optional[Dict[str, Any]]:
    """Get user profile using the access token"""
    print("\n👤 Getting user profile...")
    
    try:
        # Set authorization header
        session.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        
        print(f"Using Authorization header: Bearer {access_token[:20]}...")
        
        response = session.get(f"{BASE_URL}/user/profile")
        print(f"Profile response status: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ User profile retrieved - ID: {profile.get('id')}, Email: {profile.get('email')}")
            return profile
        else:
            print(f"❌ Failed to get user profile. Response: {response.text}")
            print(f"Response headers: {dict(response.headers)}")
            return None
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        return None

def main():
    print("🚀 Starting Profile Endpoint Test")
    print(f"Using email: {EMAIL}")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Register user
        register_response = register_user()
        if not register_response:
            print("❌ Registration failed")
            return
        
        # Extract access token
        access_token = register_response.get('accessToken')
        if not access_token:
            print("❌ Access token not found in registration response")
            return
        
        print(f"✅ Access token length: {len(access_token)}")
        
        # Wait a moment for the user to be fully persisted
        time.sleep(2)
        
        # Get user profile
        profile = get_user_profile(access_token)
        if not profile:
            print("❌ Failed to get user profile")
            return
            
        print("✅ Profile endpoint test completed successfully!")
        
    except Exception as e:
        print(f"💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()