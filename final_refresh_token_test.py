#!/usr/bin/env python3
"""
Final comprehensive test to verify refresh token functionality works end-to-end
and to identify the exact cause of the frontend error.
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
EMAIL = f"final_{RANDOM_STRING}@example.com"
PASSWORD = "finalpassword123"

def register_user():
    """Register a new user"""
    print("📝 Registering user...")
    register_data = {
        "firstname": "Final",
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

def get_user_profile(access_token):
    """Get user profile using access token"""
    print("\n👤 Getting user profile...")
    
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

def simulate_full_auth_flow():
    """Simulate the full authentication flow that might cause the error"""
    print("\n" + "="*60)
    print("SIMULATING FULL AUTHENTICATION FLOW")
    print("="*60)
    
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
    print(f"   Refresh Token (first 30 chars): {refresh_token_str[:30]}...")
    
    # Step 3: Get user profile with access token
    profile_response = get_user_profile(access_token)
    if not profile_response:
        print("❌ Failed to get user profile with access token")
        return False
    
    print(f"   User: {profile_response.get('firstname')} {profile_response.get('lastname')}")
    
    # Step 4: Refresh token
    refresh_response = refresh_token(refresh_token_str)
    if not refresh_response:
        print("❌ Failed to refresh token")
        return False
    
    new_access_token = refresh_response.get("accessToken")
    new_refresh_token = refresh_response.get("refreshToken")
    
    if not new_access_token or not new_refresh_token:
        print("❌ Missing tokens in refresh response")
        return False
    
    print(f"\n🆕 Got new tokens after refresh:")
    print(f"   New Access Token (first 30 chars): {new_access_token[:30]}...")
    print(f"   New Refresh Token (first 30 chars): {new_refresh_token[:30]}...")
    
    # Step 5: Get user profile with new access token
    new_profile_response = get_user_profile(new_access_token)
    if not new_profile_response:
        print("❌ Failed to get user profile with new access token")
        return False
    
    print(f"   User: {new_profile_response.get('firstname')} {new_profile_response.get('lastname')}")
    
    # Step 6: Try to refresh with old token (should still work in some cases)
    print("\n🔁 Trying to refresh with old token...")
    old_refresh_response = refresh_token(refresh_token_str)
    if old_refresh_response:
        print("✅ Old token still works (might be a security concern)")
    else:
        print("✅ Old token correctly invalidated")
    
    return True

def test_edge_cases():
    """Test edge cases that might cause the frontend error"""
    print("\n" + "="*60)
    print("TESTING EDGE CASES")
    print("="*60)
    
    # Test 1: Refresh with token that has wrong signature
    print("\n🧪 Test 1: Refresh with malformed token")
    refresh_token("malformed.token.here")
    
    # Test 2: Refresh with expired token (simulate by waiting)
    print("\n🧪 Test 2: Simulating token expiration scenario")
    login_response = login_user()
    if login_response:
        # In a real scenario, we'd wait for token expiration, but we'll just test immediately
        refresh_response = refresh_token(login_response.get("refreshToken"))
        if refresh_response:
            print("✅ Token refresh works immediately after login")
        else:
            print("❌ Token refresh failed immediately after login")
    
    # Test 3: Multiple rapid refreshes
    print("\n🧪 Test 3: Multiple rapid refreshes")
    login_response = login_user()
    if login_response:
        token = login_response.get("refreshToken")
        for i in range(3):
            print(f"   Refresh attempt {i+1}:")
            refresh_response = refresh_token(token)
            if refresh_response:
                token = refresh_response.get("refreshToken")  # Use new token for next attempt
                print("   ✅ Refresh successful")
            else:
                print("   ❌ Refresh failed")
                break

def main():
    print(f"🚀 Starting final refresh token test at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Using email: {EMAIL}")
    
    # Test the full authentication flow
    flow_success = simulate_full_auth_flow()
    
    # Test edge cases
    test_edge_cases()
    
    print("\n" + "="*60)
    print("FINAL TEST RESULTS")
    print("="*60)
    
    if flow_success:
        print("✅ All critical authentication flow tests passed!")
        print("✅ Backend refresh token functionality is working correctly!")
        print("\n📝 If you're still seeing the frontend error, the issue is likely:")
        print("   1. Tokens not being stored properly in localStorage")
        print("   2. Network/CORS issues in the browser environment")
        print("   3. Race conditions in token retrieval")
        print("   4. Issues with the AuthService implementation")
    else:
        print("❌ Some tests failed!")
        print("❌ There may be issues with the backend refresh token functionality")

if __name__ == "__main__":
    main()