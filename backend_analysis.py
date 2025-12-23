"""
Backend Analysis Script for Offers and Test Questions
This script tests the complete workflow: register -> login -> create test
and compares what the frontend sends vs. what the backend expects.
"""
import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

class BackendAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.created_test_id = None
        self.created_offer_id = None
        
    def register_user(self, email: str, password: str, firstname: str, lastname: str):
        """Register a new user"""
        print("🔐 Registering user...")
        register_data = {
            "email": email,
            "password": password,
            "confirmPassword": password,
            "firstname": firstname,
            "lastname": lastname,
            "rgpdAccepted": True,
            "ccpaAccepted": True,
            "commercialUseConsent": True
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/auth/register",
            json=register_data,
            headers=HEADERS
        )
        
        print(f"Registration response: {response.status_code}")
        if response.status_code == 200:
            print("✅ User registered successfully")
            return response.json()
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
    
    def login_user(self, email: str, password: str):
        """Login user and store tokens"""
        print("🔐 Logging in user...")
        login_data = {
            "email": email,
            "password": password
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            headers=HEADERS
        )
        
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get('accessToken')
            self.refresh_token = result.get('refreshToken')
            print("✅ User logged in successfully")
            print(f"   Access token length: {len(self.access_token) if self.access_token else 0}")
            print(f"   Refresh token length: {len(self.refresh_token) if self.refresh_token else 0}")
            
            # Set auth headers for future requests
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
            
            return result
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    
    def create_test(self, title: str, description: str, passing_score: int = 50):
        """Create a course test"""
        print("📝 Creating course test...")
        test_data = {
            "title": title,
            "description": description,
            "passingScore": passing_score,
            "timeLimitMinutes": 60
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/tests/course-tests",
            json=test_data,
            headers=HEADERS
        )
        
        print(f"Create test response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            self.created_test_id = result.get('id')
            print(f"✅ Test created successfully with ID: {self.created_test_id}")
            return result
        else:
            print(f"❌ Test creation failed: {response.text}")
            return None
    
    def create_offer(self, title: str, description: str, price: float):
        """Create an offer"""
        print("🏷️ Creating offer...")
        offer_data = {
            "title": title,
            "description": description,
            "price": price,
            "durationHours": 10,
            "userTypeId": 1,  # Assuming user type ID 1 exists
            "isActive": True
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/offers",
            json=offer_data,
            headers=HEADERS
        )
        
        print(f"Create offer response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            self.created_offer_id = result.get('id')
            print(f"✅ Offer created successfully with ID: {self.created_offer_id}")
            return result
        else:
            print(f"❌ Offer creation failed: {response.text}")
            return None
    
    def create_test_question(self, test_id: int, question_text: str):
        """Create a test question"""
        print("❓ Creating test question...")
        question_data = {
            "questionText": question_text,
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
        
        print(f"Create question response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Question created successfully with ID: {result.get('id')}")
            return result
        else:
            print(f"❌ Question creation failed: {response.text}")
            return None
    
    def get_offers(self):
        """Get all offers"""
        print("📋 Getting all offers...")
        response = self.session.get(
            f"{BASE_URL}/api/offers",
            headers=HEADERS
        )
        
        print(f"Get offers response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {len(result)} offers")
            return result
        else:
            print(f"❌ Get offers failed: {response.text}")
            return None
    
    def get_test_questions(self):
        """Get all test questions"""
        print("📋 Getting all test questions...")
        response = self.session.get(
            f"{BASE_URL}/api/tests/questions",
            headers=HEADERS
        )
        
        print(f"Get questions response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved {len(result)} questions")
            return result
        else:
            print(f"❌ Get questions failed: {response.text}")
            return None
    
    def analyze_token_structure(self):
        """Analyze JWT token structure"""
        if not self.access_token:
            print("❌ No access token available for analysis")
            return
        
        print("\n🔍 JWT Token Analysis:")
        print(f"Token length: {len(self.access_token)}")
        
        # Split token into parts
        parts = self.access_token.split('.')
        if len(parts) == 3:
            header, payload, signature = parts
            print(f"Header part length: {len(header)}")
            print(f"Payload part length: {len(payload)}")
            print(f"Signature part length: {len(signature)}")
            
            # Decode payload (with proper padding)
            import base64
            try:
                # Add padding if needed
                payload_padded = payload + '=' * (4 - len(payload) % 4)
                decoded_payload = base64.b64decode(payload_padded)
                payload_json = json.loads(decoded_payload)
                print(f"Decoded payload: {json.dumps(payload_json, indent=2)}")
            except Exception as e:
                print(f"Error decoding payload: {e}")
        else:
            print("❌ Invalid JWT token format")
    
    def run_complete_analysis(self):
        """Run the complete analysis workflow"""
        print("=" * 60)
        print("🚀 Backend Analysis for Offers and Test Questions")
        print("=" * 60)
        
        # Step 1: Register user
        user_data = {
            "email": f"testuser_{int(time.time())}@example.com",
            "password": "testpassword123",
            "firstname": "Test",
            "lastname": "User"
        }
        
        register_result = self.register_user(**user_data)
        if not register_result:
            print("❌ Failed to register user, stopping analysis")
            return
        
        # Step 2: Login user
        login_result = self.login_user(user_data["email"], user_data["password"])
        if not login_result:
            print("❌ Failed to login user, stopping analysis")
            return
        
        # Step 3: Analyze token structure
        self.analyze_token_structure()
        
        # Step 4: Create an offer
        offer_result = self.create_offer(
            title="Test Offer",
            description="Test offer for analysis",
            price=99.99
        )
        
        # Step 5: Get all offers to verify creation
        offers = self.get_offers()
        
        # Step 6: Create a course test
        test_result = self.create_test(
            title="Test Analysis",
            description="Test for backend analysis"
        )
        
        if test_result:
            # Step 7: Create a test question for the test
            question_result = self.create_test_question(
                test_id=test_result["id"],
                question_text="What is the analysis question?"
            )
        
        # Step 8: Get all test questions to verify creation
        questions = self.get_test_questions()
        
        print("\n" + "=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"✅ User registered: {register_result is not None}")
        print(f"✅ User logged in: {login_result is not None}")
        print(f"✅ Token analysis: {self.access_token is not None}")
        print(f"✅ Offer created: {offer_result is not None}")
        print(f"✅ Offers retrieved: {offers is not None}")
        print(f"✅ Test created: {test_result is not None}")
        print(f"✅ Question created: {question_result is not None}")
        print(f"✅ Questions retrieved: {questions is not None}")
        
        if offers:
            print(f"   Total offers: {len(offers)}")
        if questions:
            print(f"   Total questions: {len(questions)}")
        
        print("\n✅ Backend analysis completed!")
        print("=" * 60)

def main():
    analyzer = BackendAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()