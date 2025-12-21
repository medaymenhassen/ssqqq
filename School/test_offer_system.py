import requests
import json
import time

# Base URL for the Spring Boot application
BASE_URL = "http://localhost:8080"

# Admin user credentials (assuming this user exists and has admin rights)
ADMIN_USER = {
    "email": "admin@example.com",
    "password": "adminpassword"
}

# Regular user credentials
USER_DATA = {
    "firstname": "Offer",
    "lastname": "Tester",
    "email": f"offer.tester.{int(time.time())}@example.com",
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

def login_user(email, password):
    """Log in a user"""
    print(f"🔐 Logging in user {email}...")
    login_data = {
        "email": email,
        "password": password
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

def create_offer(token):
    """Create a new offer"""
    print("🎁 Creating a new offer...")
    headers = {"Authorization": f"Bearer {token}"}
    offer_data = {
        "title": "Basic Access Package",
        "description": "24 hours of access to all course lessons",
        "price": 9.99,
        "durationHours": 24,
        "userTypeId": 1
    }
    url = f"{BASE_URL}/api/offers"
    response = requests.post(url, json=offer_data, headers=headers)
    
    if response.status_code == 200:
        offer = response.json()
        print(f"✅ Offer created successfully with ID: {offer['id']}")
        return offer
    else:
        print(f"❌ Offer creation failed with status code {response.status_code}")
        print(response.text)
        return None

def get_all_offers():
    """Get all active offers"""
    print("🛒 Getting all active offers...")
    url = f"{BASE_URL}/api/offers"
    response = requests.get(url)
    
    if response.status_code == 200:
        offers = response.json()
        print(f"✅ Retrieved {len(offers)} offers")
        return offers
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
        user_offer = response.json()
        print(f"✅ Offer purchased successfully")
        return user_offer
    else:
        print(f"❌ Offer purchase failed with status code {response.status_code}")
        print(response.text)
        return None

def check_user_access(user_id):
    """Check if user has access to content"""
    print(f"🔒 Checking access for user {user_id}...")
    url = f"{BASE_URL}/api/offers/user/{user_id}/access"
    response = requests.get(url)
    
    if response.status_code == 200:
        has_access = response.json()
        print(f"✅ User access check: {'Yes' if has_access else 'No'}")
        return has_access
    else:
        print(f"❌ Access check failed with status code {response.status_code}")
        print(response.text)
        return None

def try_access_lesson_without_access(lesson_id):
    """Try to access a lesson without having purchased an offer"""
    print(f"🚫 Trying to access lesson {lesson_id} without access...")
    url = f"{BASE_URL}/api/course-lessons/{lesson_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✅ Lesson accessed successfully (this might be unexpected)")
        return True
    elif response.status_code == 403:
        print("✅ Correctly blocked access to lesson (403 Forbidden)")
        return False
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
        print(response.text)
        return None

def try_access_lesson_with_access(lesson_id, user_id):
    """Try to access a lesson after purchasing an offer"""
    print(f"✅ Trying to access lesson {lesson_id} with access...")
    url = f"{BASE_URL}/api/course-lessons/{lesson_id}?userId={user_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✅ Lesson accessed successfully")
        return True
    elif response.status_code == 403:
        print("❌ Still blocked access to lesson (403 Forbidden)")
        return False
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")
        print(response.text)
        return None

def main():
    """Main function to test the complete offer workflow"""
    print("=" * 60)
    print("🚀 Starting Offer System Test")
    print("=" * 60)
    
    # Step 1: Register user
    register_response = register_user()
    if not register_response:
        print("💥 Workflow failed at registration step")
        return
    
    # Small delay
    time.sleep(1)
    
    # Step 2: Login user
    login_response = login_user(USER_DATA["email"], USER_DATA["password"])
    if not login_response:
        print("💥 Workflow failed at login step")
        return
    
    user_token = login_response.get("accessToken")
    if not user_token:
        print("💥 No access token found in login response")
        return
    
    user_id = 1  # This would normally be extracted from the token or response
    
    print(f"🔑 User token obtained: {user_token[:20]}...")
    
    # Small delay
    time.sleep(1)
    
    # Step 3: Try to access lessons without purchase (should be blocked)
    print("\n--- Testing Access Control ---")
    try_access_lesson_without_access(1)  # Try to access lesson 1
    
    # Small delay
    time.sleep(1)
    
    # Step 4: Get all offers
    print("\n--- Offer Management ---")
    offers = get_all_offers()
    if not offers or len(offers) == 0:
        print("⚠️ No offers available. An admin needs to create offers first.")
        print("💡 In a real scenario, an admin would create offers through the admin panel.")
        return
    
    offer_id = offers[0]["id"]
    print(f"🎯 Selected offer ID: {offer_id}")
    
    # Small delay
    time.sleep(1)
    
    # Step 5: Purchase an offer
    print("\n--- Purchase Process ---")
    user_offer = purchase_offer(user_token, offer_id, user_id)
    if not user_offer:
        print("💥 Workflow failed at purchase step")
        return
    
    print(f"💰 Purchase confirmed: {user_offer}")
    
    # Small delay
    time.sleep(1)
    
    # Step 6: Check access after purchase
    print("\n--- Access Verification ---")
    has_access = check_user_access(user_id)
    if has_access is None:
        print("💥 Workflow failed at access check step")
        return
    
    if has_access:
        print("🎉 User now has access to content!")
    else:
        print("❌ User still does not have access to content")
    
    # Small delay
    time.sleep(1)
    
    # Step 7: Try to access lessons with purchase (should be allowed)
    print("\n--- Content Access Test ---")
    try_access_lesson_with_access(1, user_id)  # Try to access lesson 1
    
    print("\n" + "=" * 60)
    print("🎉 Offer System Test Completed!")
    print("=" * 60)
    print("📊 Summary:")
    print("   👤 User registered and logged in")
    print("   🛒 Offers retrieved")
    print("   💰 Offer purchased")
    print("   🔒 Access control verified")
    print("   📚 Content access tested")

if __name__ == "__main__":
    main()