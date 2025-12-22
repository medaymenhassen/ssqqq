import requests
import json
import time

# Base URL for the Spring Boot application
BASE_URL = "http://localhost:8080"

# Test user credentials
USER_DATA = {
    "firstname": "Test",
    "lastname": "User",
    "email": "test.user@example.com",
    "password": "password123",
    "rgpdAccepted": True,
    "ccpaAccepted": False
}

def register_user():
    """Register a new user"""
    print("📝 Registering user...")
    url = f"{BASE_URL}/api/auth/register"
    response = requests.post(url, json=USER_DATA)
    
    if response.status_code == 200:
        print("✅ User registered successfully")
        return response.json()
    else:
        print(f"❌ Registration failed with status code {response.status_code}")
        print(response.text)
        return None

def login_user():
    """Log in the user"""
    print("🔐 Logging in user...")
    login_data = {
        "email": USER_DATA["email"],
        "password": USER_DATA["password"]
    }
    url = f"{BASE_URL}/api/auth/login"
    response = requests.post(url, json=login_data)
    
    if response.status_code == 200:
        print("✅ User logged in successfully")
        return response.json()
    else:
        print(f"❌ Login failed with status code {response.status_code}")
        print(response.text)
        return None

def get_all_offers(token):
    """Get all active offers"""
    print("🛒 Getting all active offers...")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/offers"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Offers retrieved successfully")
        return response.json()
    else:
        print(f"❌ Failed to get offers with status code {response.status_code}")
        print(response.text)
        return None

def purchase_offer(token, offer_id, user_id):
    """Purchase an offer"""
    print(f"💳 Purchasing offer {offer_id} for user {user_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/offers/{offer_id}/purchase?userId={user_id}"
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Offer purchased successfully")
        return response.json()
    else:
        print(f"❌ Failed to purchase offer with status code {response.status_code}")
        print(response.text)
        return None

def check_user_access(token, user_id):
    """Check if user has access to content"""
    print(f"🔒 Checking access for user {user_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/offers/user/{user_id}/access"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Access check completed")
        return response.json()
    else:
        print(f"❌ Failed to check access with status code {response.status_code}")
        print(response.text)
        return None

def get_course_lessons(token, user_id=None):
    """Get course lessons with optional user access check"""
    print("📚 Getting course lessons...")
    headers = {"Authorization": f"Bearer {token}"}
    if user_id:
        url = f"{BASE_URL}/api/course-lessons?userId={user_id}"
    else:
        url = f"{BASE_URL}/api/course-lessons"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Course lessons retrieved successfully")
        return response.json()
    elif response.status_code == 403:
        print("❌ Access denied - user needs to purchase an offer")
        return None
    else:
        print(f"❌ Failed to get course lessons with status code {response.status_code}")
        print(response.text)
        return None

def get_test_questions(token):
    """Get test questions"""
    print("❓ Getting test questions...")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/tests/questions"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("✅ Test questions retrieved successfully")
        return response.json()
    elif response.status_code == 403:
        print("❌ Access denied - user needs to purchase an offer")
        return None
    else:
        print(f"❌ Failed to get test questions with status code {response.status_code}")
        print(response.text)
        return None

def create_sample_offer(token):
    """Create a sample offer for testing"""
    print("🎁 Creating sample offer...")
    headers = {"Authorization": f"Bearer {token}"}
    offer_data = {
        "title": "Basic Access Pass",
        "description": "Get access to all course content for 1 hour",
        "price": 9.99,
        "durationHours": 1,
        "isActive": True
    }
    url = f"{BASE_URL}/api/offers"
    response = requests.post(url, json=offer_data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Sample offer created successfully")
        return response.json()
    else:
        print(f"❌ Failed to create sample offer with status code {response.status_code}")
        print(response.text)
        return None

def main():
    """Main function to test API access"""
    print("=" * 60)
    print("🚀 Starting API Access Test")
    print("=" * 60)
    
    # Step 1: Register user
    register_response = register_user()
    if not register_response:
        print("💥 Workflow failed at registration step")
        return
    
    # Small delay
    time.sleep(1)
    
    # Step 2: Login user
    login_response = login_user()
    if not login_response:
        print("💥 Workflow failed at login step")
        return
    
    token = login_response.get("accessToken")
    if not token:
        print("💥 No access token found in login response")
        return
    
    print(f"🔑 Access token obtained: {token[:20]}...")
    
    # Small delay
    time.sleep(1)
    
    # Step 3: Try to access course lessons without purchase (should fail with 403)
    print("\n--- Testing access WITHOUT purchase ---")
    lessons = get_course_lessons(token)
    if lessons is None:
        print("🔒 Expected: Access denied without purchase")
    else:
        print("🔓 Unexpected: Access granted without purchase")
    
    # Small delay
    time.sleep(1)
    
    # Step 4: Try to access test questions without purchase (should fail with 403)
    print("\n--- Testing access to test questions WITHOUT purchase ---")
    questions = get_test_questions(token)
    if questions is None:
        print("🔒 Expected: Access denied without purchase")
    else:
        print("🔓 Unexpected: Access granted without purchase")
    
    # Small delay
    time.sleep(1)
    
    # Step 5: Get all offers
    offers = get_all_offers(token)
    offer_id = None
    if offers and len(offers) > 0:
        offer_id = offers[0]["id"]
        print(f"🛍️ Found offer ID: {offer_id}")
    else:
        # Create a sample offer if none exist
        offer_response = create_sample_offer(token)
        if offer_response:
            offer_id = offer_response["id"]
            print(f"🛍️ Created offer ID: {offer_id}")
        else:
            print("💥 Could not create or find an offer")
            return
    
    # Small delay
    time.sleep(1)
    
    # Step 6: Purchase the offer
    user_id = 1  # Assuming user ID 1 for test user
    purchase_response = purchase_offer(token, offer_id, user_id)
    if not purchase_response:
        print("💥 Workflow failed at purchase step")
        return
    
    print("💰 Offer purchased successfully!")
    
    # Small delay
    time.sleep(1)
    
    # Step 7: Check user access
    access_check = check_user_access(token, user_id)
    if access_check and access_check.get("hasAccess"):
        print("✅ User now has access to content")
    else:
        print("❌ User still does not have access")
    
    # Small delay
    time.sleep(1)
    
    # Step 8: Try to access course lessons with purchase (should succeed)
    print("\n--- Testing access WITH purchase ---")
    lessons = get_course_lessons(token, user_id)
    if lessons is not None:
        print("🔓 Success: Access granted with purchase")
        print(f"   Found {len(lessons)} course lessons")
    else:
        print("🔒 Failed: Still no access with purchase")
    
    # Small delay
    time.sleep(1)
    
    # Step 9: Try to access test questions with purchase (should succeed)
    print("\n--- Testing access to test questions WITH purchase ---")
    questions = get_test_questions(token)
    if questions is not None:
        print("🔓 Success: Access granted with purchase")
        print(f"   Found {len(questions)} test questions")
    else:
        print("🔒 Failed: Still no access with purchase")
    
    print("=" * 60)
    print("🎉 API Access Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()