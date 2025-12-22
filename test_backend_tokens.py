#!/usr/bin/env python3
"""
Simple test to verify backend token generation
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
EMAIL = f"backendtest_{RANDOM_STRING}@example.com"
PASSWORD = "backendtest123"

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
        "firstname": "Backend",
        "lastname": "Tester",
        "email": EMAIL,
        "password": PASSWORD,
        "rgpdAccepted": True,
        "commercialUseConsent": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Register response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Registration successful")
            print(f"Access token length: {len(result.get('accessToken', ''))}")
            print(f"Refresh token length: {len(result.get('refreshToken', ''))}")
            
            # Decode tokens
            access_payload = decode_jwt_payload(result.get('accessToken', ''))
            refresh_payload = decode_jwt_payload(result.get('refreshToken', ''))
            
            if access_payload:
                print("Access token payload:")
                print(json.dumps(access_payload, indent=2))
            
            if refresh_payload:
                print("Refresh token payload:")
                print(json.dumps(refresh_payload, indent=2))
            
            return result
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
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful")
            print(f"Access token length: {len(result.get('accessToken', ''))}")
            print(f"Refresh token length: {len(result.get('refreshToken', ''))}")
            
            # Decode tokens
            access_payload = decode_jwt_payload(result.get('accessToken', ''))
            refresh_payload = decode_jwt_payload(result.get('refreshToken', ''))
            
            if access_payload:
                print("Access token payload:")
                print(json.dumps(access_payload, indent=2))
            
            if refresh_payload:
                print("Refresh token payload:")
                print(json.dumps(refresh_payload, indent=2))
            
            return result
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_refresh_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Test the refresh token endpoint"""
    print("\n🔄 Testing refresh token...")
    
    refresh_data = {
        "refreshToken": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
        print(f"Refresh token response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Token refresh successful")
            print(f"New access token length: {len(result.get('accessToken', ''))}")
            print(f"New refresh token length: {len(result.get('refreshToken', ''))}")
            
            # Decode new tokens
            access_payload = decode_jwt_payload(result.get('accessToken', ''))
            refresh_payload = decode_jwt_payload(result.get('refreshToken', ''))
            
            if access_payload:
                print("New access token payload:")
                print(json.dumps(access_payload, indent=2))
            
            if refresh_payload:
                print("New refresh token payload:")
                print(json.dumps(refresh_payload, indent=2))
            
            return result
        else:
            print(f"❌ Token refresh failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during token refresh: {e}")
        return None

def main():
    print("🚀 Starting Backend Token Test")
    print(f"Using email: {EMAIL}")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Test 1: Register user
        print("\n" + "="*50)
        print("TEST 1: User Registration")
        print("="*50)
        register_result = register_user()
        if not register_result:
            print("❌ Registration test failed")
            return
        
        time.sleep(2)
        
        # Test 2: Login user
        print("\n" + "="*50)
        print("TEST 2: User Login")
        print("="*50)
        login_result = login_user()
        if not login_result:
            print("❌ Login test failed")
            return
        
        time.sleep(2)
        
        # Test 3: Refresh token
        print("\n" + "="*50)
        print("TEST 3: Token Refresh")
        print("="*50)
        refresh_token_str = login_result.get('refreshToken')
        if refresh_token_str:
            refresh_result = test_refresh_token(refresh_token_str)
            if not refresh_result:
                print("❌ Refresh token test failed")
                return
        else:
            print("❌ No refresh token found in login response")
            return
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED!")
        print("Backend token generation is working correctly!")
        print("="*50)
        
    except Exception as e:
        print(f"💥 Unexpected error during testing: {e}")

if __name__ == "__main__":
    main()