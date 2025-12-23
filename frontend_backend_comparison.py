"""
Frontend-Backend Comparison Script
This script compares what the frontend sends vs. what the backend expects
for offers and test questions functionality.
"""
import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

class FrontendBackendComparison:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_data = None
        self.test_data = None
        self.question_data = None
        
    def register_and_login_user(self):
        """Register and login a user for testing"""
        print("🔐 Registering and logging in user...")
        
        # Register user
        register_data = {
            "email": f"testuser_{int(time.time())}@example.com",
            "password": "testpassword123",
            "confirmPassword": "testpassword123",
            "firstname": "Test",
            "lastname": "User",
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
        self.session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })
        
        print("✅ User registered and logged in successfully")
        return True
    
    def analyze_frontend_offer_structure(self):
        """Analyze what frontend expects for offers (based on Angular code)"""
        print("\n🔍 ANALYZING FRONTEND OFFER STRUCTURE")
        print("=" * 50)
        
        # Based on Angular Offer interface
        frontend_offer_structure = {
            "id": "number (optional for creation)",
            "title": "string",
            "description": "string", 
            "price": "number",
            "durationHours": "number",
            "userTypeId": "number (nullable)",
            "isActive": "boolean",
            "createdAt": "string (timestamp)",
            "updatedAt": "string (timestamp)"
        }
        
        print("Frontend Offer Interface (from Angular):")
        for field, type_hint in frontend_offer_structure.items():
            print(f"  {field}: {type_hint}")
        
        return frontend_offer_structure
    
    def analyze_backend_offer_structure(self):
        """Analyze what backend expects for offers"""
        print("\n🔍 ANALYZING BACKEND OFFER STRUCTURE")
        print("=" * 50)
        
        # Try to get existing offers to see structure
        response = self.session.get(f"{BASE_URL}/api/offers")
        backend_structure = None
        
        if response.status_code == 200:
            offers = response.json()
            if offers:
                backend_structure = offers[0]  # Use first offer as example
                print("Backend Offer Structure (from API response):")
                for field, value in backend_structure.items():
                    print(f"  {field}: {type(value).__name__} = {value}")
            else:
                print("No existing offers found, showing expected structure:")
                # Based on the Offer entity from the backend
                backend_structure = {
                    "id": 0,
                    "title": "string",
                    "description": "string",
                    "price": 0.0,
                    "durationHours": 0,
                    "userTypeId": 0,  # This might be null
                    "isActive": True,
                    "createdAt": "2025-12-23T10:30:00.000+00:00",
                    "updatedAt": "2025-12-23T10:30:00.000+00:00"
                }
                for field, value in backend_structure.items():
                    print(f"  {field}: {type(value).__name__}")
        else:
            print(f"❌ Could not fetch offers: {response.status_code}")
        
        return backend_structure
    
    def analyze_frontend_test_question_structure(self):
        """Analyze what frontend expects for test questions"""
        print("\n🔍 ANALYZING FRONTEND TEST QUESTION STRUCTURE")
        print("=" * 50)
        
        # Based on Angular TestQuestion interface
        frontend_question_structure = {
            "id": "number (optional for creation)",
            "questionText": "string",
            "questionOrder": "number",
            "points": "number", 
            "questionType": "string (MCQ or OPEN_ENDED)",
            "createdAt": "string (timestamp)",
            "updatedAt": "string (timestamp)",
            "courseTestId": "number",
            "userId": "number (optional)",
            "answers": "TestAnswer[] (optional)"
        }
        
        print("Frontend Test Question Interface (from Angular):")
        for field, type_hint in frontend_question_structure.items():
            print(f"  {field}: {type_hint}")
        
        return frontend_question_structure
    
    def analyze_backend_test_question_structure(self):
        """Analyze what backend expects for test questions"""
        print("\n🔍 ANALYZING BACKEND TEST QUESTION STRUCTURE")
        print("=" * 50)
        
        # Create a test to use for questions
        test_data = {
            "title": "Analysis Test",
            "description": "Test for structure analysis",
            "passingScore": 50,
            "timeLimitMinutes": 60
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/tests/course-tests",
            json=test_data,
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"❌ Could not create test: {response.text}")
            return None
        
        created_test = response.json()
        test_id = created_test.get('id')
        
        # Create a test question
        question_data = {
            "questionText": "Analysis question?",
            "questionOrder": 1,
            "points": 10,
            "questionType": "MCQ",
            "courseTestId": test_id
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/tests/questions",
            json=question_data,
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"❌ Could not create question: {response.text}")
            return None
        
        created_question = response.json()
        
        print("Backend Test Question Structure (from API response):")
        for field, value in created_question.items():
            print(f"  {field}: {type(value).__name__} = {value}")
        
        return created_question
    
    def compare_structures(self, frontend_structure, backend_structure, entity_type):
        """Compare frontend and backend structures"""
        print(f"\n📋 COMPARING {entity_type.upper()} STRUCTURES")
        print("=" * 50)
        
        if not backend_structure:
            print("❌ Cannot compare - no backend structure available")
            return
        
        frontend_fields = set(frontend_structure.keys()) if isinstance(frontend_structure, dict) else set()
        backend_fields = set(backend_structure.keys()) if isinstance(backend_structure, dict) else set()
        
        print(f"Frontend fields: {len(frontend_fields)}")
        for field in sorted(frontend_fields):
            print(f"  ✅ {field}")
        
        print(f"\nBackend fields: {len(backend_fields)}")
        for field in sorted(backend_fields):
            print(f"  ✅ {field}")
        
        # Find differences
        only_in_frontend = frontend_fields - backend_fields
        only_in_backend = backend_fields - frontend_fields
        
        print(f"\n⚠️  Differences:")
        if only_in_frontend:
            print(f"  Only in frontend: {list(only_in_frontend)}")
        if only_in_backend:
            print(f"  Only in backend: {list(only_in_backend)}")
        
        if not only_in_frontend and not only_in_backend:
            print("  ✅ Structures match perfectly!")
        
        return {
            'frontend_fields': frontend_fields,
            'backend_fields': backend_fields,
            'only_in_frontend': only_in_frontend,
            'only_in_backend': only_in_backend
        }
    
    def test_token_consistency(self):
        """Test token consistency between requests"""
        print("\n🔐 TESTING TOKEN CONSISTENCY")
        print("=" * 50)
        
        # Make several requests with the same token
        endpoints = [
            f"{BASE_URL}/api/user/profile",
            f"{BASE_URL}/api/tests/course-tests",
            f"{BASE_URL}/api/tests/questions"
        ]
        
        results = []
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint)
                status = response.status_code
                results.append((endpoint, status))
                print(f"  {endpoint}: {status}")
            except Exception as e:
                print(f"  {endpoint}: ERROR - {e}")
                results.append((endpoint, "ERROR"))
        
        # Check if all requests succeeded
        successful_requests = [r for r in results if r[1] == 200]
        print(f"\n✅ Successful requests: {len(successful_requests)}/{len(endpoints)}")
        
        return len(successful_requests) == len(endpoints)
    
    def run_full_comparison(self):
        """Run the full comparison analysis"""
        print("=" * 60)
        print("🚀 FRONTEND-BACKEND COMPARISON ANALYSIS")
        print("=" * 60)
        
        # Step 1: Register and login user
        if not self.register_and_login_user():
            print("❌ Failed to register/login user")
            return
        
        # Step 2: Analyze offer structures
        frontend_offer = self.analyze_frontend_offer_structure()
        backend_offer = self.analyze_backend_offer_structure()
        
        # Step 3: Compare offer structures
        offer_comparison = self.compare_structures(
            frontend_offer, backend_offer, "offers"
        )
        
        # Step 4: Analyze test question structures
        frontend_question = self.analyze_frontend_test_question_structure()
        backend_question = self.analyze_backend_test_question_structure()
        
        # Step 5: Compare test question structures
        question_comparison = self.compare_structures(
            frontend_question, backend_question, "test questions"
        )
        
        # Step 6: Test token consistency
        token_consistency = self.test_token_consistency()
        
        print("\n" + "=" * 60)
        print("📊 FINAL COMPARISON REPORT")
        print("=" * 60)
        
        print(f"✅ User authentication: Working")
        print(f"✅ Offer structure comparison: {'Completed' if offer_comparison else 'Failed'}")
        print(f"✅ Test question structure comparison: {'Completed' if question_comparison else 'Failed'}")
        print(f"✅ Token consistency: {'✅ Working' if token_consistency else '❌ Issues'}")
        
        if offer_comparison:
            print(f"   - Offer fields match: {len(offer_comparison['only_in_frontend']) == 0 and len(offer_comparison['only_in_backend']) == 0}")
        
        if question_comparison:
            print(f"   - Question fields match: {len(question_comparison['only_in_frontend']) == 0 and len(question_comparison['only_in_backend']) == 0}")
        
        print("\n✅ Frontend-Backend comparison completed!")
        print("=" * 60)

def main():
    analyzer = FrontendBackendComparison()
    analyzer.run_full_comparison()

if __name__ == "__main__":
    main()