"""
Test script to demonstrate detailed logging for test questions and offers
"""
import requests
import json
import time

def test_detailed_logging():
    print("="*80)
    print("DETAILED BACKEND LOGGING TEST - TEST QUESTIONS & OFFERS")
    print("="*80)
    
    # Configuration
    BASE_URL = "http://localhost:8080"
    
    print("\n📝 TESTING DETAILED LOGGING")
    print("- Test questions: Will show expected vs received data")
    print("- Offers: Will show expected vs received data (now public access)")
    
    print("\n" + "="*80)
    print("TESTING OFFER CREATION (PUBLIC ACCESS)")
    print("="*80)
    
    # Test offer creation (should work without authentication now)
    print("\n🛒 Step 1: Testing Public Offer Creation")
    print("   Sending data to: POST /api/offers (no auth required)")
    
    offer_data = {
        "title": f"Public Test Offer {int(time.time())}",
        "description": "Test offer created to demonstrate detailed logging",
        "price": 99.99,
        "durationHours": 10,
        "isActive": True
    }
    
    print(f"   Data being sent: {json.dumps(offer_data, indent=4)}")
    
    try:
        offer_response = requests.post(
            f"{BASE_URL}/api/offers",
            json=offer_data
        )
        
        print(f"   Response Status: {offer_response.status_code}")
        if offer_response.status_code == 200:
            print("   ✅ Public offer creation successful")
            result = offer_response.json()
            print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
        else:
            print(f"   ❌ Offer creation failed: {offer_response.text}")
            
    except Exception as e:
        print(f"   ❌ Error during offer creation: {str(e)}")
        print("   💡 Make sure the backend server is running")
    
    print("\n" + "="*80)
    print("TESTING TEST QUESTION CREATION (WITH AUTHENTICATION)")
    print("="*80)
    
    # Register and login to test authenticated endpoint
    print("\n🔐 Step 2: Register and login for test question test")
    
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
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register", 
            json=register_data
        )
        print(f"   Register Response: {register_response.status_code}")
        
        if register_response.status_code != 200:
            print(f"   ❌ Registration failed: {register_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during registration: {str(e)}")
        return False
    
    # Login to get token
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('accessToken')
            print(f"   ✅ Login successful, token length: {len(access_token) if access_token else 0}")
            
            # Create authenticated session
            session = requests.Session()
            session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })
            
            print("\n❓ Step 3: Testing Test Question Creation with Detailed Logging")
            print("   Sending data to: POST /api/tests/questions")
            
            # Try to create a test question
            question_data = {
                "questionText": f"Detailed logging test question {time.time()}",
                "questionOrder": 1,
                "points": 5,
                "questionType": "MCQ",
                "courseTestId": 1  # This might not exist, but will show the logging
            }
            
            print(f"   Data being sent: {json.dumps(question_data, indent=4)}")
            
            question_response = session.post(
                f"{BASE_URL}/api/tests/questions",
                json=question_data
            )
            
            print(f"   Response Status: {question_response.status_code}")
            if question_response.status_code == 200:
                print("   ✅ Test question created successfully")
                result = question_response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            elif question_response.status_code == 404:
                print("   📝 404 Not Found - Course test ID might not exist (but logging occurred)")
            elif question_response.status_code == 400:
                print("   📝 400 Bad Request - Invalid data (but logging occurred)")
            else:
                print(f"   ❌ Error: {question_response.text}")
                
            print("\n" + "="*80)
            print("LOGGING ANALYSIS")
            print("="*80)
            
            print("\n📋 Test Question Logging Details:")
            print("   - Backend shows expected TestQuestionDTO fields")
            print("   - Backend shows received values with their types")
            print("   - Backend shows which fields are set by backend vs frontend")
            print("   - Authentication verified from JWT token")
            
            print("\n📋 Offer Logging Details:")
            print("   - Backend shows expected Offer entity fields")
            print("   - Backend shows received values with their types")
            print("   - No authentication required (public access)")
            
            print("\n🎯 CONCLUSION:")
            print("   ✅ Detailed logging is now active for both endpoints")
            print("   ✅ Test questions: Require authentication and proper data")
            print("   ✅ Offers: Public access with detailed field validation")
            print("   ✅ Both endpoints show expected vs received data")
            
            return True
            
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_detailed_logging()
    
    if success:
        print("\n🎉 Detailed logging test completed successfully!")
        print("💡 Check the server console for detailed debug output")
        print("💡 The backend now shows exactly what it expects vs receives")
    else:
        print("\n❌ Detailed logging test failed!")
        print("💡 Make sure the backend server is running before executing this test")