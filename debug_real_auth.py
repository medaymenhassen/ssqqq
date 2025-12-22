

import requests
import json
import time
import random
import string
import base64

# Configuration
BASE_URL = "http://localhost:8080/api"
RANDOM_STRING = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
EMAIL = f"realtest_{RANDOM_STRING}@example.com"
PASSWORD = "realtest123"

# Track the flow
flow_log = []

def log_step(status, message, details=None):
    """Log each step for debugging"""
    entry = {
        "status": status,
        "message": message,
        "details": details,
        "timestamp": time.time()
    }
    flow_log.append(entry)
    
    icon = "✅" if status == "success" else "❌" if status == "error" else "ℹ️"
    print(f"{icon} {message}")
    if details:
        if isinstance(details, dict):
            for key, value in details.items():
                print(f"   → {key}: {value}")
        else:
            print(f"   → {details}")

def test_registration():
    """Test registration flow"""
    print("\n" + "="*60)
    print("STEP 1: REGISTRATION")
    print("="*60)
    
    register_data = {
        "firstname": "Real",
        "lastname": "Tester",
        "email": EMAIL,
        "password": PASSWORD,
        "rgpdAccepted": True,
        "ccpaAccepted": True,  # ← Make sure this is included
        "commercialUseConsent": True
    }

    log_step("info", f"Attempting to register user: {EMAIL}")
    log_step("info", "Request data:", {
        "endpoint": f"{BASE_URL}/auth/register",
        "method": "POST",
        "body_keys": list(register_data.keys())
    })

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        log_step("info", f"Response received", {
            "status_code": response.status_code,
            "content_type": response.headers.get('Content-Type', 'unknown')
        })

        if response.status_code == 200:
            result = response.json()
            log_step("success", "Registration successful")
            
            access_token = result.get('accessToken')
            refresh_token = result.get('refreshToken')
            
            log_step("info", "Token check", {
                "access_token_present": bool(access_token),
                "refresh_token_present": bool(refresh_token),
                "access_token_length": len(access_token) if access_token else 0
            })

            if access_token:
                try:
                    parts = access_token.split('.')
                    if len(parts) == 3:
                        payload = parts[1]
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = base64.b64decode(payload)
                        payload_json = json.loads(decoded)
                        log_step("info", "Token payload decoded", payload_json)
                    else:
                        log_step("error", f"Invalid token format - {len(parts)} parts instead of 3")
                except Exception as e:
                    log_step("error", f"Failed to decode token: {e}")

            return result
        else:
            log_step("error", f"Registration failed with status {response.status_code}")
            log_step("error", "Response body", response.text)
            return None

    except Exception as e:
        log_step("error", f"Registration request failed: {e}")
        return None

def test_login():
    """Test login flow"""
    print("\n" + "="*60)
    print("STEP 2: LOGIN")
    print("="*60)
    
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }

    log_step("info", f"Attempting to login as: {EMAIL}")
    log_step("info", "Request data:", {
        "endpoint": f"{BASE_URL}/auth/login",
        "method": "POST"
    })

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        log_step("info", "Response received", {
            "status_code": response.status_code,
            "content_type": response.headers.get('Content-Type', 'unknown')
        })

        if response.status_code == 200:
            result = response.json()
            log_step("success", "Login successful")
            
            access_token = result.get('accessToken')
            log_step("info", "Token received", {
                "token_length": len(access_token) if access_token else 0,
                "token_type": result.get('tokenType')
            })

            if access_token:
                try:
                    parts = access_token.split('.')
                    if len(parts) == 3:
                        payload = parts[1]
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = base64.b64decode(payload)
                        payload_json = json.loads(decoded)
                        log_step("info", "Token payload", payload_json)
                    else:
                        log_step("error", f"Invalid token format - {len(parts)} parts")
                except Exception as e:
                    log_step("error", f"Failed to decode token: {e}")

            return result
        else:
            log_step("error", f"Login failed with status {response.status_code}")
            log_step("error", "Response body", response.text)
            return None

    except Exception as e:
        log_step("error", f"Login request failed: {e}")
        return None

def test_database_check(access_token):
    """Test direct user lookup - simulates what the backend does"""
    print("\n" + "="*60)
    print("STEP 2.5: DATABASE CHECK (What Backend Does)")
    print("="*60)
    
    log_step("info", "Simulating backend's findByEmail() lookup")
    log_step("info", f"Checking if user '{EMAIL}' exists in database")
    
    # This doesn't actually test the database, but shows what should happen
    log_step("info", "Expected flow:", {
        "1_user_registered": "User created during registration",
        "2_user_authenticated": "User password validated during login",
        "3_user_should_exist": "User MUST exist in database for profile access"
    })

def test_profile_access(access_token):
    """Test accessing user profile with token"""
    print("\n" + "="*60)
    print("STEP 3: PROFILE ACCESS")
    print("="*60)

    log_step("info", "Attempting to access profile endpoint")
    log_step("info", "Request details:", {
        "endpoint": f"{BASE_URL}/user/profile",
        "method": "GET",
        "token_length": len(access_token) if access_token else 0,
        "token_preview": f"{access_token[:20]}..." if access_token else "None"
    })

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        
        log_step("info", "Response received", {
            "status_code": response.status_code,
            "content_type": response.headers.get('Content-Type', 'unknown'),
            "content_length": len(response.text)
        })

        if response.status_code == 200:
            result = response.json()
            log_step("success", "Profile access successful")
            log_step("info", "User profile", {
                "id": result.get('id'),
                "email": result.get('email'),
                "name": f"{result.get('firstname')} {result.get('lastname')}",
                "role": result.get('role')
            })
            return result
        
        elif response.status_code == 404:
            log_step("error", "❌ 404 NOT FOUND - User profile endpoint returned 404")
            log_step("error", "POSSIBLE CAUSES:", {
                "1": "User NOT found in database (findByEmail returned empty)",
                "2": "User created during registration but not persisted to DB",
                "3": "Database connection issue during registration",
                "4": "User created but with different email than used for login",
                "5": "Registration succeeded but user wasn't actually saved"
            })
            log_step("error", "Response body", response.text)
            
        elif response.status_code == 401:
            log_step("error", "❌ 401 UNAUTHORIZED - Token validation failed")
            log_step("error", "Possible causes:", {
                "1": "Token signature invalid",
                "2": "Token expired",
                "3": "JWT validation failed"
            })
            log_step("error", "Response body", response.text)
            
        elif response.status_code == 403:
            log_step("error", "❌ 403 FORBIDDEN - Access denied")
            log_step("error", "Possible causes:", {
                "1": "User authenticated but lacks required role",
                "2": "Method-level security annotation blocking access",
                "3": "CustomAccessDeniedHandler triggered"
            })
            log_step("error", "Response body", response.text)
        
        else:
            log_step("error", f"Unexpected status code: {response.status_code}")
            log_step("error", "Response body", response.text)
            
        return None

    except Exception as e:
        log_step("error", f"Profile access request failed: {e}")
        return None

def test_token_refresh(refresh_token):
    """Test token refresh"""
    print("\n" + "="*60)
    print("STEP 4: TOKEN REFRESH")
    print("="*60)

    log_step("info", "Attempting to refresh token")

    refresh_data = {
        "refreshToken": refresh_token
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/refresh-token", json=refresh_data)
        
        log_step("info", f"Response received", {
            "status_code": response.status_code
        })

        if response.status_code == 200:
            result = response.json()
            log_step("success", "Token refresh successful")
            return result
        else:
            log_step("error", f"Token refresh failed with status {response.status_code}")
            log_step("error", "Response body", response.text)
            return None

    except Exception as e:
        log_step("error", f"Token refresh failed: {e}")
        return None

def print_summary():
    """Print execution summary"""
    print("\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)
    
    successes = sum(1 for log in flow_log if log["status"] == "success")
    errors = sum(1 for log in flow_log if log["status"] == "error")
    infos = sum(1 for log in flow_log if log["status"] == "info")
    
    print(f"\n📊 Results: {successes} success, {errors} errors, {infos} info messages")
    
    if errors > 0:
        print(f"\n🔍 Found {errors} error(s). Review above for details.\n")
        print("ROOT CAUSE ANALYSIS:")
        print("-" * 60)
        
        # Analyze the error pattern
        profile_error = next((log for log in flow_log if "404" in str(log.get("message", ""))), None)
        
        if profile_error and "404" in str(profile_error):
            print("\n⚠️  404 NOT FOUND on /api/user/profile")
            print("\nThis means:")
            print("  1. The endpoint EXISTS (not routing issue)")
            print("  2. But UserController.getCurrentUserProfile() returned 404")
            print("  3. Which means userService.findByEmail() returned empty")
            print("\nMOST LIKELY CAUSE:")
            print("  → User was NOT successfully saved to database during registration")
            print("\nTO INVESTIGATE:")
            print("  1. Check your database (MySQL/PostgreSQL) directly")
            print("     SELECT * FROM users WHERE email = '" + EMAIL + "';")
            print("  2. Check backend logs for registration save errors")
            print("  3. Verify UserRepository.save() is called and succeeds")
            print("  4. Check for transaction rollback issues")

def main():
    print("\n" + "🚀 STARTING ENHANCED AUTHENTICATION DEBUG" + "\n")
    print(f"Base URL: {BASE_URL}")
    print(f"Test email: {EMAIL}")
    print(f"Test password: {PASSWORD}")

    # Test 1: Registration
    reg_result = test_registration()
    if not reg_result:
        log_step("error", "Stopping - Registration failed")
        print_summary()
        return
    
    time.sleep(2)

    # Test 2: Login
    login_result = test_login()
    if not login_result:
        log_step("error", "Stopping - Login failed")
        print_summary()
        return
    
    time.sleep(2)

    # Test 2.5: Database check simulation
    access_token = login_result.get('accessToken')
    if access_token:
        test_database_check(access_token)
    
    time.sleep(1)

    # Test 3: Profile access
    if access_token:
        profile_result = test_profile_access(access_token)
        if not profile_result:
            log_step("error", "⚠️  Profile access failed - see analysis below")
    else:
        log_step("error", "No access token for profile test")
    
    time.sleep(2)

    # Test 4: Token refresh
    refresh_token = login_result.get('refreshToken')
    if refresh_token:
        refresh_result = test_token_refresh(refresh_token)
    else:
        log_step("error", "No refresh token for refresh test")

    # Print summary
    print_summary()
    print("\n" + "="*60)
    print("✅ ENHANCED AUTH DEBUG COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()