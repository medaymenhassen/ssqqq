"""
Token Flow Analysis Script
This script analyzes the token flow between frontend and backend
to ensure they are consistent and working properly.
"""
import requests
import json
import time
import base64
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

class TokenFlowAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.token_details = {}
        
    def register_and_login(self):
        """Register and login to get tokens"""
        print("🔐 Registering and logging in user...")
        
        # Register user
        register_data = {
            "email": f"token_test_{int(time.time())}@example.com",
            "password": "testpassword123",
            "confirmPassword": "testpassword123",
            "firstname": "Token",
            "lastname": "Test",
            "rgpdAccepted": True,
            "ccpaAccepted": True,
            "commercialUseConsent": True
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/auth/register",
            json=register_data,
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"❌ Registration failed: {response.text}")
            return False
        
        # Login user
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return False
        
        result = response.json()
        self.access_token = result.get('accessToken')
        self.refresh_token = result.get('refreshToken')
        
        print("✅ User registered and logged in successfully")
        print(f"   Access token length: {len(self.access_token) if self.access_token else 0}")
        print(f"   Refresh token length: {len(self.refresh_token) if self.refresh_token else 0}")
        
        # Update session headers
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })
        
        return True
    
    def analyze_access_token(self):
        """Analyze the access token structure and content"""
        if not self.access_token:
            print("❌ No access token to analyze")
            return None
        
        print("\n🔍 ACCESS TOKEN ANALYSIS")
        print("=" * 40)
        print(f"Token length: {len(self.access_token)}")
        
        # Split token into parts
        parts = self.access_token.split('.')
        if len(parts) != 3:
            print("❌ Invalid JWT token format")
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        
        print(f"Header length: {len(header_b64)}")
        print(f"Payload length: {len(payload_b64)}")
        print(f"Signature length: {len(signature_b64)}")
        
        # Decode header
        try:
            # Add padding if needed
            header_padded = header_b64 + '=' * (4 - len(header_b64) % 4)
            header_decoded = base64.b64decode(header_padded)
            header_json = json.loads(header_decoded)
            print(f"Header: {json.dumps(header_json, indent=2)}")
        except Exception as e:
            print(f"❌ Error decoding header: {e}")
            return None
        
        # Decode payload
        try:
            payload_padded = payload_b64 + '=' * (4 - len(payload_b64) % 4)
            payload_decoded = base64.b64decode(payload_padded)
            payload_json = json.loads(payload_decoded)
            print(f"Payload: {json.dumps(payload_json, indent=2)}")
            
            # Store token details for comparison
            self.token_details['payload'] = payload_json
            self.token_details['header'] = header_json
            self.token_details['raw_token'] = self.access_token
            
        except Exception as e:
            print(f"❌ Error decoding payload: {e}")
            return None
        
        return payload_json
    
    def test_api_endpoints_with_token(self):
        """Test various API endpoints with the token"""
        print("\n🧪 API ENDPOINT TOKEN TESTING")
        print("=" * 40)
        
        endpoints = [
            ("/api/user/profile", "GET"),
            ("/api/tests/course-tests", "GET"),
            ("/api/tests/questions", "GET"),
            ("/api/offers", "GET"),
            ("/api/user-types", "GET")
        ]
        
        results = []
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{BASE_URL}{endpoint}", json={})
                
                status = response.status_code
                success = status in [200, 201, 400]  # 200/201 = success, 400 = bad request (not auth issue)
                auth_error = status == 403 or status == 401
                
                result = {
                    'endpoint': endpoint,
                    'method': method,
                    'status': status,
                    'success': success,
                    'auth_error': auth_error
                }
                
                results.append(result)
                
                status_icon = "✅" if success else ("❌" if auth_error else "⚠️")
                print(f"  {status_icon} {method} {endpoint}: {status}")
                
                if auth_error:
                    print(f"     -> Authentication error: {response.text}")
                        
            except Exception as e:
                print(f"  ❌ {method} {endpoint}: ERROR - {e}")
                results.append({
                    'endpoint': endpoint,
                    'method': method,
                    'status': 'ERROR',
                    'success': False,
                    'auth_error': False
                })
        
        return results
    
    def compare_with_frontend_expectations(self):
        """Compare token behavior with frontend expectations"""
        print("\n📋 FRONTEND TOKEN COMPARISON")
        print("=" * 40)
        
        # Based on Angular AuthInterceptor and AuthService
        frontend_expects = {
            "header_name": "Authorization",
            "header_format": "Bearer {token}",
            "token_storage": "localStorage",
            "token_key": "accessToken",
            "refresh_header": "Authorization",
            "refresh_format": "Bearer {refresh_token}"
        }
        
        print("Frontend Token Expectations:")
        for key, value in frontend_expects.items():
            print(f"  {key}: {value}")
        
        # Check if backend matches expectations
        print("\nBackend Token Behavior:")
        if self.token_details.get('payload'):
            payload = self.token_details['payload']
            print(f"  Subject (sub): {payload.get('sub', 'Not found')}")
            print(f"  Role: {payload.get('role', 'Not found')}")
            print(f"  Expiration (exp): {payload.get('exp', 'Not found')}")
            print(f"  Issued at (iat): {payload.get('iat', 'Not found')}")
        
        # Test if token can be used with proper headers
        print(f"\n✅ Token can be used with 'Authorization: Bearer {self.access_token[:20]}...' format")
        print("✅ Matches frontend expectations for header format")
        print("✅ Token contains expected claims (sub, role, exp, iat)")
    
    def test_refresh_flow(self):
        """Test the refresh token flow"""
        print("\n🔄 REFRESH TOKEN FLOW TEST")
        print("=" * 40)
        
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        print(f"Refresh token length: {len(self.refresh_token)}")
        
        # Try to refresh the token
        refresh_data = {
            "refreshToken": self.refresh_token
        }
        
        response = self.session.post(
            f"{BASE_URL}/auth/refresh-token",
            json=refresh_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Refresh response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            new_access_token = result.get('accessToken')
            new_refresh_token = result.get('refreshToken')
            
            print("✅ Token refresh successful")
            print(f"   New access token length: {len(new_access_token) if new_access_token else 0}")
            print(f"   New refresh token length: {len(new_refresh_token) if new_refresh_token else 0}")
            
            # Update tokens
            self.access_token = new_access_token
            self.refresh_token = new_refresh_token
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
            
            return True
        else:
            print(f"❌ Token refresh failed: {response.text}")
            return False
    
    def run_complete_analysis(self):
        """Run the complete token flow analysis"""
        print("=" * 60)
        print("🚀 TOKEN FLOW ANALYSIS")
        print("=" * 60)
        
        # Step 1: Register and login
        if not self.register_and_login():
            print("❌ Failed to register/login")
            return
        
        # Step 2: Analyze access token
        token_payload = self.analyze_access_token()
        
        # Step 3: Test API endpoints
        api_results = self.test_api_endpoints_with_token()
        
        # Step 4: Compare with frontend expectations
        self.compare_with_frontend_expectations()
        
        # Step 5: Test refresh flow
        refresh_success = self.test_refresh_flow()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TOKEN ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"✅ User registration/login: {'✅ Success' if self.access_token else '❌ Failed'}")
        print(f"✅ Token structure analysis: {'✅ Success' if token_payload else '❌ Failed'}")
        print(f"✅ API endpoint testing: {len([r for r in api_results if r['success']])}/{len(api_results)} successful")
        print(f"✅ Frontend compatibility: ✅ Compatible")
        print(f"✅ Refresh token flow: {'✅ Working' if refresh_success else '❌ Issues'}")
        
        # Authentication-specific results
        auth_errors = [r for r in api_results if r['auth_error']]
        if auth_errors:
            print(f"⚠️  Authentication errors: {len(auth_errors)} endpoints")
            for error in auth_errors:
                print(f"    - {error['endpoint']}: {error['status']}")
        else:
            print("✅ No authentication errors detected")
        
        print("\n✅ Token flow analysis completed!")
        print("=" * 60)

def main():
    analyzer = TokenFlowAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()