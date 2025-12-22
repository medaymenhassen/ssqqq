#!/usr/bin/env python3
"""
Debug script to test refresh token functionality and identify the "Could not refresh token" error
"""

import requests
import json
import time
import random
import string
import base64
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "http://localhost:8080/api"
# Generate a random email to avoid conflicts
RANDOM_STRING = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
EMAIL = f"refreshtest_{RANDOM_STRING}@example.com"
PASSWORD = "refreshtest123"

# Global session for persistent cookies/headers
session = requests.Session()

def decode_jwt_payload(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT payload to inspect its contents"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decode the payload (second part)
        payload = parts[1]
        # Add padding if necessary
        payload += '=' * (4 - len(payload) % 4)
        decoded_payload = base64.b64decode(payload)
        payload_json = json.loads(decoded_payload)
        return payload_json
    except Exception as e:
        print(f"❌ Error decoding JWT payload: {e}")
        return None

def register_user() -> Optional[Dict[str, Any]]:
    """Register a new user for testing"""
    print("\n📝 Registering user...")
    register_data = {
        "firstname": "Refresh",
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
            return response.json()
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_refresh_token_endpoint(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Test the refresh token endpoint specifically"""
    print("\n🔄 Testing refresh token endpoint...")
    print(f"Refresh token length: {len(refresh_token)}")
    
    # Decode refresh token payload to inspect
    payload = decode_jwt_payload(refresh_token)
    if payload:
        print("🔓 Refresh token payload:")
        print(json.dumps(payload, indent=2))
        print(f"⏱️ Token expires: {time.ctime(payload.get('exp', 0))}")
        print(f"👤 Token subject: {payload.get('sub', 'Unknown')}")
        print(f"🎭 Token role: {payload.get('role', 'Unknown')}")
    
    refresh_data = {
        "refreshToken": refresh_token
    }
    
    try:
        # Test with JSON content type
        headers = {"Content-Type": "application/json"}
        response = session.post(
            f"{BASE_URL}/auth/refresh-token", 
            json=refresh_data,
            headers=headers
        )
        print(f"Refresh token response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Token refresh successful")
            result = response.json()
            print(f"Result keys: {list(result.keys())}")
            return result
        else:
            print(f"❌ Token refresh failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error details: {error_detail}")
            except:
                print(f"Response text: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during token refresh: {e}")
        return None

def test_refresh_token_with_form_data(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Test the refresh token endpoint with form data"""
    print("\n🔄 Testing refresh token endpoint with form data...")
    
    try:
        # Test with form data
        refresh_data = {
            "refreshToken": refresh_token
        }
        response = session.post(
            f"{BASE_URL}/auth/refresh-token", 
            data=refresh_data
        )
        print(f"Form data refresh response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Form data token refresh successful")
            return response.json()
        else:
            print(f"❌ Form data token refresh failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error during form data token refresh: {e}")
        return None

def test_refresh_token_directly(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Test refresh token by making a direct request to a protected endpoint"""
    print("\n🧪 Testing refresh token with protected endpoint...")
    
    try:
        # First, try accessing a protected endpoint with an expired/expiring token
        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = session.get(f"{BASE_URL}/user/profile", headers=headers)
        print(f"Protected endpoint response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Protected endpoint accessible with current token")
            return response.json()
        elif response.status_code == 401:
            print("⚠️ Protected endpoint returned 401 - token may be expired")
            # Try to refresh and then access again
            refresh_result = test_refresh_token_endpoint(refresh_token)
            if refresh_result:
                new_token = refresh_result.get('accessToken')
                if new_token:
                    headers = {"Authorization": f"Bearer {new_token}"}
                    response2 = session.get(f"{BASE_URL}/user/profile", headers=headers)
                    print(f"Retry response status: {response2.status_code}")
                    if response2.status_code == 200:
                        print("✅ Successfully accessed protected endpoint with refreshed token")
                        return response2.json()
                    else:
                        print(f"❌ Still failed after refresh: {response2.text}")
            return None
        else:
            print(f"❌ Unexpected response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing protected endpoint: {e}")
        return None

def debug_refresh_token_issues() -> bool:
    """Debug refresh token issues comprehensively"""
    print("="*60)
    print("DEBUGGING REFRESH TOKEN ISSUES")
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
    
    # Decode tokens
    print("\n🔓 Decoding registration tokens...")
    access_payload = decode_jwt_payload(access_token)
    refresh_payload = decode_jwt_payload(refresh_token_str)
    
    if access_payload:
        print("Access token payload:")
        print(json.dumps(access_payload, indent=2))
    
    if refresh_payload:
        print("Refresh token payload:")
        print(json.dumps(refresh_payload, indent=2))
    
    # Wait a moment
    time.sleep(2)
    
    # Step 2: Login user
    print("\nStep 2: User Login")
    login_response = login_user()
    if not login_response:
        print("❌ Login failed")
        return False
    
    # Extract login tokens
    login_access_token = login_response.get('accessToken')
    login_refresh_token = login_response.get('refreshToken')
    
    print(f"✅ Login access token length: {len(login_access_token)}")
    print(f"✅ Login refresh token length: {len(login_refresh_token)}")
    
    # Step 3: Test refresh token endpoint with login refresh token
    print("\nStep 3: Testing Refresh Token Endpoint")
    refresh_result = test_refresh_token_endpoint(login_refresh_token)
    if not refresh_result:
        print("❌ Refresh token endpoint test failed")
        # Try alternative approaches
        print("\nTrying alternative approaches...")
        test_refresh_token_with_form_data(login_refresh_token)
        return False
    
    # Extract refreshed tokens
    refreshed_access_token = refresh_result.get('accessToken')
    refreshed_refresh_token = refresh_result.get('refreshToken')
    
    print(f"✅ Refreshed access token length: {len(refreshed_access_token)}")
    print(f"✅ Refreshed refresh token length: {len(refreshed_refresh_token)}")
    
    # Step 4: Test using refreshed token to access protected endpoint
    print("\nStep 4: Testing Protected Endpoint Access")
    protected_result = test_refresh_token_directly(refreshed_access_token)
    if not protected_result:
        print("❌ Protected endpoint access failed")
        return False
    
    print("✅ Protected endpoint access successful")
    
    # Step 5: Test multiple refresh cycles
    print("\nStep 5: Testing Multiple Refresh Cycles")
    current_refresh_token = refreshed_refresh_token
    for i in range(3):
        print(f"\nCycle {i+1}:")
        cycle_result = test_refresh_token_endpoint(current_refresh_token)
        if not cycle_result:
            print(f"❌ Refresh cycle {i+1} failed")
            return False
        
        current_refresh_token = cycle_result.get('refreshToken', current_refresh_token)
        print(f"✅ Cycle {i+1} successful")
    
    print("✅ All refresh token tests completed successfully!")
    return True

def main():
    print("🚀 Starting Refresh Token Debug Test")
    print(f"Using email: {EMAIL}")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Run the refresh token debug test
        success = debug_refresh_token_issues()
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        
        if success:
            print("✅ All refresh token debug tests passed!")
            print("✅ Refresh token functionality is working correctly!")
        else:
            print("❌ Some refresh token debug tests failed!")
            print("❌ There may be issues with the refresh token implementation")
            
    except Exception as e:
        print(f"💥 Unexpected error during testing: {e}")

if __name__ == "__main__":
    main()