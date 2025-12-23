"""
Form Data Verification Script
This script tests that HTML forms are properly sending data to the backend
for offers and test questions functionality.
"""
import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

class FormDataValidator:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_data = {}
        
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
        
        try:
            register_response = self.session.post(
                f"{BASE_URL}/api/auth/register", 
                json=register_data
            )
            print(f"✅ Registration: {register_response.status_code}")
            
            # Login user
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            
            login_response = self.session.post(
                f"{BASE_URL}/api/auth/login", 
                json=login_data
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.access_token = login_data.get('accessToken')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                print(f"✅ Login successful, token received")
                print(f"   Token length: {len(self.access_token) if self.access_token else 0}")
                return True
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error during registration/login: {str(e)}")
            return False

    def test_offer_creation(self):
        """Test that offer form data is properly sent to backend"""
        print("\n🛒 Testing Offer Creation...")
        
        # Test data for offer creation
        offer_data = {
            "title": f"Test Offer {int(time.time())}",
            "description": "This is a test offer created for validation",
            "price": 99.99,
            "durationHours": 10,
            "userTypeId": None,
            "isActive": True,
            "createdAt": "2025-12-23T11:00:00",
            "updatedAt": "2025-12-23T11:00:00"
        }
        
        try:
            # Attempt to create offer (this should fail with 403 for non-admin)
            response = self.session.post(
                f"{BASE_URL}/api/offers",
                json=offer_data
            )
            
            print(f"   Offer creation response: {response.status_code}")
            if response.status_code == 403:
                print("   ✅ Expected 403 error (only admin can create offers)")
            elif response.status_code == 200:
                print("   ✅ Offer created successfully")
                return True
            else:
                print(f"   ❌ Unexpected response: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error creating offer: {str(e)}")
        
        return False

    def test_test_question_creation(self):
        """Test that test question form data is properly sent to backend"""
        print("\n❓ Testing Test Question Creation...")
        
        # First, create a course test to associate with the question
        course_test_data = {
            "title": f"Test Course {int(time.time())}",
            "description": "Test course for validation",
            "passingScore": 70,
            "timeLimitMinutes": 60,
            "courseId": 1
        }
        
        try:
            # Create a course test
            test_response = self.session.post(
                f"{BASE_URL}/api/tests/course-tests",
                json=course_test_data
            )
            
            if test_response.status_code in [200, 201]:
                test_data = test_response.json()
                course_test_id = test_data['id']
                print(f"   ✅ Course test created with ID: {course_test_id}")
            else:
                print(f"   ❌ Failed to create course test: {test_response.status_code}")
                # Use an existing test if available
                tests_response = self.session.get(f"{BASE_URL}/api/tests/course-tests")
                if tests_response.status_code == 200:
                    tests_data = tests_response.json()
                    if tests_data:
                        course_test_id = tests_data[0]['id']
                        print(f"   📝 Using existing course test ID: {course_test_id}")
                    else:
                        print("   ❌ No course tests available")
                        return False
                else:
                    return False
            
            # Now create a test question
            question_data = {
                "questionText": f"Test question created at {time.time()}",
                "questionOrder": 1,
                "points": 5,
                "questionType": "MCQ",
                "courseTestId": course_test_id
            }
            
            question_response = self.session.post(
                f"{BASE_URL}/api/tests/questions",
                json=question_data
            )
            
            print(f"   Test question creation response: {question_response.status_code}")
            if question_response.status_code in [200, 201]:
                print("   ✅ Test question created successfully")
                question_data_resp = question_response.json()
                print(f"   Question ID: {question_data_resp.get('id', 'N/A')}")
                return True
            else:
                print(f"   ❌ Failed to create test question: {question_response.status_code}")
                print(f"   Response: {question_response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating test question: {str(e)}")
            return False

    def test_video_generation(self):
        """Test that video generation form data is properly sent to backend"""
        print("\n🎥 Testing Video Generation...")
        
        # Sample CSV content for video generation
        csv_content = """Timestamp,Pose Confidence,Head X,Head Y,Head Z,Head Confidence
1634567890,0.95,0.1,0.2,0.3,0.95
1634567891,0.92,0.15,0.25,0.35,0.92
1634567892,0.90,0.2,0.3,0.4,0.90"""
        
        # Create a CSV file
        import io
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        # Create form data for video generation
        files = {
            'file': ('test_data.csv', csv_file, 'text/csv')
        }
        
        data = {
            'userId': '1',  # Using default user ID
            'videoName': f'test-video-{int(time.time())}.mp4'
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/springboot/csv/create-video",
                files=files,
                data=data
            )
            
            print(f"   Video generation response: {response.status_code}")
            if response.status_code in [200, 201]:
                print("   ✅ Video generation request successful")
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                return True
            else:
                print(f"   ❌ Video generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error in video generation: {str(e)}")
            return False

    def run_complete_validation(self):
        """Run complete form data validation"""
        print("=" * 60)
        print("FORM DATA VALIDATION - OFFERS & TEST QUESTIONS")
        print("=" * 60)
        
        print("\n📋 STEP 1: User Registration & Authentication")
        auth_success = self.register_and_login_user()
        
        if not auth_success:
            print("❌ Authentication failed, cannot proceed with tests")
            return False
        
        print("\n📋 STEP 2: Offer Form Data Validation")
        offer_success = self.test_offer_creation()
        
        print("\n📋 STEP 3: Test Question Form Data Validation")
        question_success = self.test_test_question_creation()
        
        print("\n📋 STEP 4: Video Generation Form Data Validation")
        video_success = self.test_video_generation()
        
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS:")
        print(f"  ✅ Offer Creation: {'PASS' if offer_success else 'FAIL'}")
        print(f"  ✅ Test Question Creation: {'PASS' if question_success else 'FAIL'}")
        print(f"  ✅ Video Generation: {'PASS' if video_success else 'FAIL'}")
        
        overall_success = offer_success and question_success and video_success
        print(f"\n  🎯 OVERALL: {'PASS' if overall_success else 'FAIL'}")
        print("=" * 60)
        
        return overall_success

if __name__ == "__main__":
    validator = FormDataValidator()
    success = validator.run_complete_validation()
    
    if success:
        print("\n🎉 All form data validations passed!")
    else:
        print("\n⚠️  Some validations failed. Check the backend configuration.")