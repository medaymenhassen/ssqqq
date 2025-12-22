#!/usr/bin/env python3
"""
Step-by-step authentication debugging
"""

import requests
import json
import time
import random
import string
import base64

# Configuration
BASE_URL = "http://localhost:8080/api"
RANDOM_STRING = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
EMAIL = f"debugtest_{RANDOM_STRING}@example.com"
PASSWORD = "debugtest123"

def step1_test_backend_registration():
    """Step 1: Test backend registration and token generation"""
    print("=== STEP 1: Testing Backend Registration ===")
    
    register_data = {
        "firstname": "Debug",
        "lastname": "Tester",
        "email": EMAIL,
        "password": PASSWORD,
        "rgpdAccepted": True,
        "commercialUseConsent": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Registration status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Registration successful")
            print(f"Access token present: {'accessToken' in result}")
            print(f"Refresh token present: {'refreshToken' in result}")
            print(f"Access token length: {len(result.get('accessToken', ''))}")
            print(f"Refresh token length: {len(result.get('refreshToken', ''))}")
            
            # Try to decode token
            try:
                token = result['accessToken']
                payload = token.split('.')[1]
                # Add padding
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.b64decode(payload)
                payload_json = json.loads(decoded)
                print("Token payload:", json.dumps(payload_json, indent=2))
            except Exception as e:
                print(f"Error decoding token: {e}")
            
            return result
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def step2_test_backend_login():
    """Step 2: Test backend login"""
    print("\n=== STEP 2: Testing Backend Login ===")
    
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful")
            print(f"Access token present: {'accessToken' in result}")
            print(f"Refresh token present: {'refreshToken' in result}")
            print(f"Access token length: {len(result.get('accessToken', ''))}")
            print(f"Refresh token length: {len(result.get('refreshToken', ''))}")
            return result
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def step3_test_user_profile(access_token):
    """Step 3: Test accessing user profile with token"""
    print("\n=== STEP 3: Testing User Profile Access ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        print(f"Profile access status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Profile access successful")
            print(f"User ID: {result.get('id')}")
            print(f"User email: {result.get('email')}")
            print(f"User name: {result.get('firstname')} {result.get('lastname')}")
            return result
        else:
            print(f"❌ Profile access failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Profile access error: {e}")
        return None

def step4_test_token_refresh(refresh_token):
    """Step 4: Test token refresh"""
    print("\n=== STEP 4: Testing Token Refresh ===")
    
    refresh_data = {
        "refreshToken": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
        print(f"Token refresh status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Token refresh successful")
            print(f"New access token present: {'accessToken' in result}")
            print(f"New refresh token present: {'refreshToken' in result}")
            print(f"New access token length: {len(result.get('accessToken', ''))}")
            print(f"New refresh token length: {len(result.get('refreshToken', ''))}")
            return result
        else:
            print(f"❌ Token refresh failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        return None

def main():
    print("🚀 Starting Step-by-Step Authentication Debug")
    print(f"Email: {EMAIL}")
    
    # Step 1: Test registration
    reg_result = step1_test_backend_registration()
    if not reg_result:
        print("❌ Stopping debug - Registration failed")
        return
    
    time.sleep(2)
    
    # Step 2: Test login
    login_result = step2_test_backend_login()
    if not login_result:
        print("❌ Stopping debug - Login failed")
        return
    
    time.sleep(2)
    
    # Step 3: Test profile access
    access_token = login_result['accessToken']
    profile_result = step3_test_user_profile(access_token)
    if not profile_result:
        print("❌ Profile access failed")
    
    time.sleep(2)
    
    # Step 4: Test token refresh
    refresh_token = login_result['refreshToken']
    refresh_result = step4_test_token_refresh(refresh_token)
    if not refresh_result:
        print("❌ Token refresh failed")
    
    print("\n" + "="*50)
    print("DEBUG COMPLETE")
    print("="*50)

if __name__ == "__main__":
    main()