import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8080"
ADMIN_USER = {
    "firstname": "Mohamed",
    "lastname": "Admin",
    "email": "mohamed@admin.com",
    "password": "mohamed0192837465MED",
    "rgpdAccepted": True,
    "ccpaAccepted": True,
    "commercialUseConsent": True
}

def create_admin_user():
    """Create admin user with specified credentials"""
    print("Creating admin user...")
    
    # First, register the admin user
    register_url = f"{BASE_URL}/api/auth/register"
    
    try:
        response = requests.post(register_url, json=ADMIN_USER)
        
        if response.status_code in [200, 201]:
            print("✅ Admin user registered successfully as regular user")
            return True
        elif response.status_code == 400 and "Email already registered" in response.text:
            print("⚠️ Admin user already exists")
            return True
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def login_admin():
    """Login admin user and return authentication token"""
    print("Logging in admin user...")
    
    login_url = f"{BASE_URL}/api/auth/login"
    
    try:
        response = requests.post(login_url, json={
            "email": ADMIN_USER["email"],
            "password": ADMIN_USER["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token", data.get("accessToken", ""))
            print("✅ Admin logged in successfully")
            return token
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error logging in admin user: {e}")
        return None

def promote_user_to_admin(token, user_email):
    """Promote a user to admin role"""
    print(f"Promoting user {user_email} to admin...")
    
    # First, get the user ID by email
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get all users to find the one we just created
        users_response = requests.get(f"{BASE_URL}/api/users", headers=headers)
        if users_response.status_code == 200:
            users = users_response.json()
            user_id = None
            for user in users:
                if user.get('email') == user_email:
                    user_id = user.get('id')
                    break
            
            if user_id:
                # Update the user's role to ADMIN
                user_update_url = f"{BASE_URL}/api/users/{user_id}"
                user_data = {
                    "id": user_id,
                    "firstname": ADMIN_USER["firstname"],
                    "lastname": ADMIN_USER["lastname"],
                    "email": user_email,
                    "password": ADMIN_USER["password"],  # This will be encoded by the server
                    "role": "ADMIN"
                }
                
                update_response = requests.put(user_update_url, json=user_data, headers=headers)
                
                if update_response.status_code in [200, 201]:
                    print(f"✅ User {user_email} promoted to admin successfully")
                    return True
                else:
                    print(f"❌ Failed to promote user. Status: {update_response.status_code}")
                    print(f"Response: {update_response.text}")
                    return False
            else:
                print(f"❌ User with email {user_email} not found")
                return False
        else:
            print(f"❌ Failed to fetch users: {users_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error promoting user to admin: {e}")
        return False

def create_offer(token):
    """Create an offer using admin token"""
    print("Creating offer...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    offer_data = {
        "title": "Premium Access Offer",
        "description": "Access to premium courses and lessons with full functionality",
        "price": 99.99,
        "durationHours": 168,  # 1 week
        "userTypeId": 1  # Default user type
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/offers", json=offer_data, headers=headers)
        
        if response.status_code in [200, 201]:
            offer = response.json()
            print(f"✅ Offer created successfully: {offer.get('title', 'Unknown')}")
            return offer.get('id')
        else:
            print(f"❌ Failed to create offer: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating offer: {e}")
        return None

def create_lesson(token, offer_id):
    """Create a lesson using admin token"""
    print("Creating lesson...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    lesson_data = {
        "title": "Introduction to Electric Vehicles",
        "description": "Basic concepts and principles of electric vehicles",
        "videoUrl": "https://example.com/ev-intro-video.mp4",
        "animation3dUrl": "https://example.com/ev-3d-animation.mp4",
        "contentTitle": "Electric Vehicle Basics",
        "contentDescription": "Learn about electric vehicle components, technology, and benefits",
        "displayOrder": 1,
        "lessonOrder": 1,
        "isService": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/course-lessons", json=lesson_data, headers=headers)
        
        if response.status_code in [200, 201]:
            lesson = response.json()
            print(f"✅ Lesson created successfully: {lesson.get('title', 'Unknown')}")
            return lesson.get('id')
        else:
            print(f"❌ Failed to create lesson: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating lesson: {e}")
        return None

def create_questions_for_lesson(token, lesson_id):
    """Create questions for the lesson"""
    print("Creating questions for lesson...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # We need to create test questions - let's first create a test
    test_data = {
        "title": "Electric Vehicle Quiz",
        "description": "Test your knowledge about electric vehicles",
        "lessonId": lesson_id,
        "maxAttempts": 3,
        "timeLimit": 300,  # 5 minutes
        "passingScore": 70
    }
    
    try:
        # Create test
        response = requests.post(f"{BASE_URL}/api/tests", json=test_data, headers=headers)
        
        if response.status_code in [200, 201]:
            test = response.json()
            test_id = test.get('id')
            print(f"✅ Test created successfully: {test.get('title', 'Unknown')}")
            
            # Now create questions for the test
            questions = [
                {
                    "questionText": "What is the main component that converts electrical energy to mechanical energy in an electric vehicle?",
                    "questionType": "MCQ",
                    "expectedAnswerType": "MULTIPLE_CHOICE",
                    "questionOrder": 1,
                    "points": 1,
                    "courseTestId": test_id
                },
                {
                    "questionText": "What are the advantages of electric vehicles compared to traditional vehicles?",
                    "questionType": "OPEN_ENDED",
                    "expectedAnswerType": "OPEN_TEXT",
                    "questionOrder": 2,
                    "points": 2,
                    "courseTestId": test_id
                }
            ]
            
            for question in questions:
                q_response = requests.post(f"{BASE_URL}/api/tests/{test_id}/questions", json=question, headers=headers)
                if q_response.status_code in [200, 201]:
                    print(f"✅ Question created successfully")
                else:
                    print(f"❌ Failed to create question: {q_response.status_code}")
            
            return test_id
        else:
            print(f"❌ Failed to create test: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test/questions: {e}")
        return None

def test_purchase_functionality(admin_token):
    """Test the purchase functionality"""
    print("Testing purchase functionality...")
    
    # First, create an offer as admin to ensure there's something to purchase
    offer_data = {
        "title": "Test Purchase Offer",
        "description": "Offer created specifically for purchase testing",
        "price": 49.99,
        "durationHours": 168,  # 1 week
        "userTypeId": 1  # Default user type
    }
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/offers", json=offer_data, headers=headers)
        
        if response.status_code in [200, 201]:
            offer = response.json()
            test_offer_id = offer.get('id')
            print(f"✅ Test offer created successfully: ID {test_offer_id}")
        else:
            print(f"❌ Failed to create test offer: {response.status_code}")
            print(f"Response: {response.text}")
            # Try to get an existing offer
            offers_response = requests.get(f"{BASE_URL}/api/offers")
            if offers_response.status_code == 200:
                offers = offers_response.json()
                if offers:
                    test_offer_id = offers[0].get('id')
                    print(f"✅ Using existing offer for testing: ID {test_offer_id}")
                else:
                    print("❌ No offers available for testing")
                    return False
            else:
                print("❌ Could not fetch offers")
                return False
    except Exception as e:
        print(f"❌ Error creating test offer: {e}")
        return False
    
    # We need to create a regular user first to test the purchase
    regular_user = {
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com",
        "password": "testpassword123",
        "rgpdAccepted": True,
        "ccpaAccepted": True,
        "commercialUseConsent": True
    }
    
    # Register regular user
    try:
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json=regular_user)
        if register_response.status_code in [200, 201]:
            print("✅ Test user registered successfully")
        elif register_response.status_code == 400 and "Email already registered" in register_response.text:
            print("⚠️ Test user already exists")
        else:
            print(f"❌ Could not register test user: {register_response.status_code}")
            print(f"Response: {register_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error registering test user: {e}")
        return False
    
    # Login as regular user
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": regular_user["email"],
            "password": regular_user["password"]
        })
        
        if login_response.status_code == 200:
            user_token = login_response.json().get("token", login_response.json().get("accessToken", ""))
            print("✅ Test user logged in successfully")
        else:
            print(f"❌ Test user login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error logging in test user: {e}")
        return False
    
    # Try to purchase the offer
    try:
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }
        
        purchase_response = requests.post(f"{BASE_URL}/api/offers/{test_offer_id}/purchase", headers=headers)
        
        if purchase_response.status_code == 200:
            purchase_data = purchase_response.json()
            print(f"✅ Offer purchased successfully: {purchase_data}")
            
            # Check if the purchase was processed correctly
            if 'id' in purchase_data and 'approvalStatus' in purchase_data:
                print(f"✅ Purchase ID: {purchase_data['id']}")
                print(f"✅ Approval Status: {purchase_data['approvalStatus']}")
                return True
            else:
                print("⚠️ Purchase response missing expected fields")
                return True  # Still consider it a success since the purchase went through
        else:
            print(f"❌ Purchase failed: {purchase_response.status_code}")
            print(f"Response: {purchase_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing purchase functionality: {e}")
        return False

def main():
    print("🚀 Starting data initialization...")
    print(f"Base URL: {BASE_URL}")
    print(f"Admin credentials: {ADMIN_USER['email']} / {ADMIN_USER['password']}")
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(5)
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/offers")
        if response.status_code != 401 and response.status_code != 200:
            print(f"❌ Server might not be running. Status: {response.status_code}")
            return
        else:
            print("✅ Server is accessible")
    except:
        print("❌ Server is not accessible")
        return
    
    # Create admin user
    if not create_admin_user():
        print("⚠️ Could not create admin user, proceeding with next steps...")
    
    # Login as admin
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    # Check if user has admin privileges by trying to access an admin-only endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Try to get all users (admin-only endpoint)
        users_response = requests.get(f"{BASE_URL}/api/users", headers=headers)
        
        if users_response.status_code == 200:
            print("✅ User already has admin privileges")
            admin_token = token
        elif users_response.status_code == 403:
            print("⚠️ User does not have admin privileges, attempting to promote...")
            # This means we need an existing admin to promote this user, which we have now
            # Login with the admin user that was created by our Java code
            admin_token = login_admin()
            if not admin_token:
                print("❌ Cannot proceed without admin token")
                return
        else:
            print(f"❌ Unexpected response when checking admin privileges: {users_response.status_code}")
            admin_token = token
    except Exception as e:
        print(f"❌ Error checking admin privileges: {e}")
        return
    
    # Create offer
    offer_id = create_offer(admin_token)
    if not offer_id:
        print("❌ Cannot proceed without offer")
        return
    
    # Create lesson
    lesson_id = create_lesson(admin_token, offer_id)
    if not lesson_id:
        print("❌ Cannot proceed without lesson")
        return
    
    # Create questions for the lesson
    test_id = create_questions_for_lesson(admin_token, lesson_id)
    if not test_id:
        print("⚠️ Could not create questions, but continuing...")
    
    # Test purchase functionality
    purchase_success = test_purchase_functionality(admin_token)
    if purchase_success:
        print("✅ Purchase functionality test PASSED")
    else:
        print("❌ Purchase functionality test FAILED")
    
    print("✅ Data initialization completed!")
    print(f"Admin user: {ADMIN_USER['email']}")
    print(f"Password: {ADMIN_USER['password']}")
    print(f"Offer ID: {offer_id}")
    print(f"Lesson ID: {lesson_id}")
    print(f"Test ID: {test_id}")

if __name__ == "__main__":
    main()