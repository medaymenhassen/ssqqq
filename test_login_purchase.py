import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:4200"
API_BASE_URL = "http://localhost:8080"  # Backend API

def login_user_and_test_purchase():
    """Test the login process and purchase functionality"""
    
    print("🔍 Testing login and purchase functionality...")
    
    # User credentials
    user_email = "udevetyffi-0610@yopmail.com"
    user_password = "udevetyffi-0610@yopmail.com"
    
    # First, try to login via the API
    print(f"1. Logging in user: {user_email}")
    
    login_data = {
        "email": user_email,
        "password": user_password
    }
    
    try:
        login_response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            access_token = login_result.get('accessToken', login_result.get('token', ''))
            
            if access_token:
                print("✅ Login successful!")
                print(f"Token received: {access_token[:30]}...")
                
                # Create authenticated session
                session = requests.Session()
                session.headers.update({
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                })
                
                # Get available offers
                print("\n2. Fetching available offers...")
                offers_response = session.get(f"{API_BASE_URL}/api/offers")
                
                if offers_response.status_code == 200:
                    offers = offers_response.json()
                    print(f"✅ Found {len(offers)} offers")
                    
                    if offers:
                        # Try to purchase the first available offer
                        offer_to_purchase = offers[0]
                        print(f"Purchasing offer: {offer_to_purchase['title']} (ID: {offer_to_purchase['id']})")
                        
                        purchase_response = session.post(f"{API_BASE_URL}/api/offers/{offer_to_purchase['id']}/purchase")
                        
                        if purchase_response.status_code == 200:
                            purchase_result = purchase_response.json()
                            print("✅ Purchase successful!")
                            print(f"Purchase ID: {purchase_result.get('id')}")
                            print(f"Approval Status: {purchase_result.get('approvalStatus', 'N/A')}")
                            print(f"Is Active: {purchase_result.get('isActive', 'N/A')}")
                            
                            # Check if the purchase is pending as expected
                            if purchase_result.get('approvalStatus') == 'PENDING':
                                print("✅ Purchase correctly set to PENDING status")
                            else:
                                print(f"⚠️ Expected PENDING status, got: {purchase_result.get('approvalStatus')}")
                        else:
                            print(f"❌ Purchase failed: {purchase_response.status_code}")
                            print(f"Response: {purchase_response.text}")
                    else:
                        print("❌ No offers available to purchase")
                else:
                    print(f"❌ Failed to fetch offers: {offers_response.status_code}")
                    print(f"Response: {offers_response.text}")
            else:
                print("❌ No access token received from login")
                print(f"Response: {login_result}")
        else:
            print(f"❌ Login failed with status: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
            # Check if user exists by trying to register (will show if email already exists)
            register_check = {
                "email": user_email,
                "firstname": "Test",
                "lastname": "User",
                "password": user_password,
                "rgpdAccepted": True,
                "ccpaAccepted": True,
                "commercialUseConsent": True
            }
            
            register_response = requests.post(f"{API_BASE_URL}/api/auth/register", json=register_check)
            if register_response.status_code == 400 and "Email already registered" in register_response.text:
                print("ℹ️ User exists but login failed - likely incorrect password")
            else:
                print("ℹ️ User may not exist in the system")
    
    except Exception as e:
        print(f"❌ Error during login and purchase test: {e}")

def test_frontend_access():
    """Test accessing frontend and checking authentication state"""
    
    print("\n🔍 Testing frontend access and authentication...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Access the frontend
        frontend_response = session.get(BASE_URL)
        
        if frontend_response.status_code == 200:
            print("✅ Successfully accessed frontend")
            
            # Try to get offers through frontend (this might redirect if not authenticated properly)
            # Since Angular serves at 4200 but API is at 8080, we need to access API directly
            # but the issue might be with frontend state management
            print("ℹ️ Frontend is accessible, authentication issue might be client-side")
        else:
            print(f"❌ Failed to access frontend: {frontend_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error accessing frontend: {e}")

def debug_purchase_with_auth_token():
    """Debug purchase using the admin token to see if it's an API issue"""
    
    print("\n🔍 Debugging with known working admin credentials...")
    
    # Login as admin first to make sure API is working
    admin_login_data = {
        "email": "mohamed@admin.com",
        "password": "mohamed0192837465MED"
    }
    
    try:
        admin_login_response = requests.post(f"{API_BASE_URL}/api/auth/login", json=admin_login_data)
        
        if admin_login_response.status_code == 200:
            admin_result = admin_login_response.json()
            admin_token = admin_result.get('accessToken', admin_result.get('token', ''))
            
            if admin_token:
                print("✅ Admin login successful - API is working")
                
                # Create admin session
                admin_session = requests.Session()
                admin_session.headers.update({
                    'Authorization': f'Bearer {admin_token}',
                    'Content-Type': 'application/json'
                })
                
                # Get offers with admin
                offers_response = admin_session.get(f"{API_BASE_URL}/api/offers")
                if offers_response.status_code == 200:
                    offers = offers_response.json()
                    print(f"✅ Admin can access {len(offers)} offers")
                    
                    if offers:
                        # Test purchase with admin token as well
                        first_offer = offers[0]
                        print(f"Testing purchase with admin on offer: {first_offer['title']}")
                        
                        purchase_response = admin_session.post(f"{API_BASE_URL}/api/offers/{first_offer['id']}/purchase")
                        print(f"Admin purchase result: {purchase_response.status_code}")
                        
                        if purchase_response.status_code == 200:
                            result = purchase_response.json()
                            print(f"✅ Admin purchase successful - status: {result.get('approvalStatus')}")
                        else:
                            print(f"❌ Admin purchase failed: {purchase_response.text}")
                else:
                    print("❌ Admin cannot access offers")
            else:
                print("❌ No admin token received")
        else:
            print(f"❌ Admin login failed: {admin_login_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error with admin debug: {e}")

def check_user_exists():
    """Check if the specific user exists in the system"""
    
    print("\n🔍 Checking if user exists in the system...")
    
    # Try to register with the same email to see if it exists
    test_register_data = {
        "email": "udevetyffi-0610@yopmail.com",
        "firstname": "Test",
        "lastname": "User",
        "password": "udevetyffi-0610@yopmail.com",
        "rgpdAccepted": True,
        "ccpaAccepted": True,
        "commercialUseConsent": True
    }
    
    try:
        register_response = requests.post(f"{API_BASE_URL}/api/auth/register", json=test_register_data)
        
        if register_response.status_code == 400 and "Email already registered" in register_response.text:
            print("✅ User exists in the system")
        elif register_response.status_code == 200 or register_response.status_code == 201:
            print("✅ User was created successfully")
        else:
            print(f"❌ Registration check failed: {register_response.status_code}")
            print(f"Response: {register_response.text}")
    
    except Exception as e:
        print(f"❌ Error checking user existence: {e}")

if __name__ == "__main__":
    print("Testing login and purchase functionality for udevetyffi-0610@yopmail.com")
    print("="*70)
    
    # Check if user exists first
    check_user_exists()
    
    # Test the login and purchase
    login_user_and_test_purchase()
    
    # Test admin access to ensure API is working
    debug_purchase_with_auth_token()
    
    # Test frontend access
    test_frontend_access()
    
    print("\n" + "="*70)
    print("Test completed. Check results above for potential issues.")
    print("\nCommon causes of redirect to login:")
    print("1. Invalid or expired JWT token")
    print("2. Token not properly stored in localStorage")
    print("3. Token format issues")
    print("4. Authentication state not properly maintained in Angular")
    print("5. CORS issues between frontend and backend")