"""
Script de débogage pour analyser les différences entre ce qui est envoyé et ce que le backend attend
Spécifiquement pour identifier les causes potentielles d'erreurs 403 Forbidden
"""
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080"
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "password123"

class Debug403Analyzer:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def register_and_login(self):
        """Register and login to get a valid token"""
        print("="*70)
        print("REGISTRATION & LOGIN FOR TESTING")
        print("="*70)
        
        # Register
        register_data = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "password123",
            "confirmPassword": "password123",
            "firstname": "Test",
            "lastname": "User",
            "rgpdAccepted": True,
            "ccpaAccepted": False,
            "commercialUseConsent": True
        }
        
        try:
            register_response = self.session.post(
                f"{BASE_URL}/api/auth/register", 
                json=register_data
            )
            print(f"Registration: {register_response.status_code}")
            
            if register_response.status_code != 200:
                print(f"Registration failed: {register_response.text}")
                return False
                
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return False
        
        # Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        try:
            login_response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data
            )
            print(f"Login: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                self.access_token = login_result.get('accessToken')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                print("✅ Successfully obtained access token")
                return True
            else:
                print(f"Login failed: {login_response.text}")
                return False
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False

    def test_endpoint_access(self, endpoint, method="GET", data=None, expected_role="USER"):
        """Test access to a specific endpoint"""
        print(f"\n🔍 TESTING: {method} {endpoint}")
        print(f"Expected role: {expected_role}")
        
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        if data:
            headers["Content-Type"] = "application/json"
        
        try:
            if method.upper() == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method.upper() == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(f"{BASE_URL}{endpoint}", json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                print(f"Unsupported method: {method}")
                return None
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 403:
                print("❌ 403 Forbidden - Access denied")
                print(f"Response: {response.text}")
                
                # Analyze potential causes
                self.analyze_403_causes(endpoint, method, data, expected_role)
                
            elif response.status_code == 200:
                print("✅ 200 OK - Access granted")
                print(f"Response preview: {str(response.text)[:200]}...")
            elif response.status_code == 401:
                print("❌ 401 Unauthorized - Invalid or expired token")
            else:
                print(f"Other status: {response.status_code}")
                print(f"Response: {response.text}")
                
            return response
            
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None

    def analyze_403_causes(self, endpoint, method, data, expected_role):
        """Analyze potential causes for 403 Forbidden errors"""
        print("\n🔍 ANALYZING 403 CAUSES:")
        
        # Check 1: Token validity
        print("1. Token validity check...")
        if not self.access_token:
            print("   ❌ No access token available")
        else:
            print("   ✅ Access token is present")
        
        # Check 2: User role requirements
        print(f"2. Role requirement check...")
        print(f"   Endpoint requires: {expected_role}")
        print(f"   Your token likely has: USER role (not ADMIN)")
        
        # Check 3: Specific endpoint analysis
        if "offers" in endpoint and method == "POST":
            print("3. Offer creation check...")
            print("   ❌ Offer creation typically requires ADMIN role")
            print("   ❌ Regular users cannot create offers")
        
        elif "course-lessons" in endpoint and "/user/" in endpoint:
            print("4. Lesson access check...")
            print("   ❌ May require active offer purchase")
            print("   ❌ Check if user has purchased access to content")
        
        elif "tests" in endpoint and method == "POST":
            print("5. Test/Question creation check...")
            print("   ✅ Should work with USER role")
            print("   ❌ Check if required fields are properly set")
        
        # Check 4: Data validation
        if data:
            print("6. Data validation check...")
            print(f"   Data sent: {json.dumps(data, indent=2)}")
            
            # Check for required fields based on endpoint
            if "offers" in endpoint:
                required_fields = ["title", "price", "durationHours"]
                missing = [field for field in required_fields if field not in data or data[field] is None]
                if missing:
                    print(f"   ❌ Missing required fields: {missing}")
                else:
                    print(f"   ✅ Required fields present: {required_fields}")
            
            elif "tests" in endpoint and "questions" in endpoint:
                required_fields = ["questionText", "questionOrder", "points", "questionType"]
                missing = [field for field in required_fields if field not in data or data[field] is None]
                if missing:
                    print(f"   ❌ Missing required fields: {missing}")
                else:
                    print(f"   ✅ Required fields present: {required_fields}")

    def comprehensive_test(self):
        """Run comprehensive tests to identify 403 issues"""
        print("="*70)
        print("COMPREHENSIVE 403 DEBUGGING ANALYSIS")
        print("="*70)
        
        # Step 1: Register and login
        if not self.register_and_login():
            print("❌ Failed to register and login. Cannot proceed with tests.")
            return
        
        print(f"\nUser token: {self.access_token[:20]}..." if self.access_token else "No token")
        
        # Test different endpoints that might return 403
        test_cases = [
            {
                "endpoint": "/api/offers",
                "method": "POST",
                "data": {
                    "title": "Test Offer",
                    "description": "Test description",
                    "price": 9.99,
                    "durationHours": 24,
                    "isActive": True
                },
                "expected_role": "ADMIN",
                "description": "Creating an offer (should fail for non-admin)"
            },
            {
                "endpoint": "/api/offers",
                "method": "GET",
                "data": None,
                "expected_role": "PUBLIC",
                "description": "Getting all offers (should work for anyone)"
            },
            {
                "endpoint": "/api/course-lessons",
                "method": "GET",
                "data": None,
                "expected_role": "USER",
                "description": "Getting all course lessons (might require offer purchase)"
            },
            {
                "endpoint": "/api/tests/questions",
                "method": "POST",
                "data": {
                    "questionText": "Test question?",
                    "questionOrder": 1,
                    "points": 5,
                    "questionType": "MCQ"
                },
                "expected_role": "USER",
                "description": "Creating a test question (should work for user)"
            },
            {
                "endpoint": "/api/tests/questions",
                "method": "GET",
                "data": None,
                "expected_role": "USER",
                "description": "Getting all test questions (might require offer)"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*20} TEST {i} {'='*20}")
            print(f"Description: {test_case['description']}")
            response = self.test_endpoint_access(
                test_case["endpoint"],
                test_case["method"],
                test_case["data"],
                test_case["expected_role"]
            )
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70)
        print("\nKey Points for 403 Troubleshooting:")
        print("1. ADMIN endpoints require ADMIN role - regular users get 403")
        print("2. Content access (lessons, questions) may require purchased offer")
        print("3. Check if your user has the required role for the endpoint")
        print("4. Verify that all required fields are properly set in the request")
        print("5. Some endpoints check for user access to content before allowing operations")

def main():
    analyzer = Debug403Analyzer()
    analyzer.comprehensive_test()

if __name__ == "__main__":
    main()