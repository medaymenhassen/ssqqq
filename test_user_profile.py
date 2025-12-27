import requests
import json

def test_user_profile_access():
    """Test accessing user profile with the test user's token"""
    
    print("🔍 Testing user profile access...")
    
    # Login with the test user
    user_email = "udevetyffi-0610@yopmail.com"
    user_password = "udevetyffi-0610@yopmail.com"
    
    # Login first
    login_data = {
        "email": user_email,
        "password": user_password
    }
    
    login_response = requests.post("http://localhost:8080/api/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        access_token = login_result.get('accessToken', login_result.get('token', ''))
        
        if access_token:
            print("✅ Login successful, testing profile access...")
            
            # Test accessing user profile
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            profile_response = requests.get("http://localhost:8080/api/user/profile", headers=headers)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("✅ Profile access successful")
                print(f"User: {profile_data.get('firstname')} {profile_data.get('lastname')}")
                print(f"Email: {profile_data.get('email')}")
                print(f"Role: {profile_data.get('role')}")
                print(f"ID: {profile_data.get('id')}")
                
                # Test accessing user profile by ID as well
                user_id = profile_data.get('id')
                if user_id:
                    user_profile_response = requests.get(f"http://localhost:8080/api/user/profile/{user_id}", headers=headers)
                    print(f"Profile by ID access: {user_profile_response.status_code}")
                    
            elif profile_response.status_code == 401:
                print("❌ Profile access failed - 401 Unauthorized")
                print("This could be the issue causing the redirect to login")
                print(f"Response: {profile_response.text}")
            else:
                print(f"❌ Profile access failed - Status: {profile_response.status_code}")
                print(f"Response: {profile_response.text}")
        else:
            print("❌ No access token received")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")

def test_admin_profile_access():
    """Test accessing user profile with admin token for comparison"""
    
    print("\n🔍 Testing admin profile access...")
    
    # Login with admin
    admin_login_data = {
        "email": "mohamed@admin.com",
        "password": "mohamed0192837465MED"
    }
    
    login_response = requests.post("http://localhost:8080/api/auth/login", json=admin_login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        access_token = login_result.get('accessToken', login_result.get('token', ''))
        
        if access_token:
            print("✅ Admin login successful, testing profile access...")
            
            # Test accessing admin profile
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            profile_response = requests.get("http://localhost:8080/api/user/profile", headers=headers)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("✅ Admin profile access successful")
                print(f"User: {profile_data.get('firstname')} {profile_data.get('lastname')}")
                print(f"Email: {profile_data.get('email')}")
                print(f"Role: {profile_data.get('role')}")
            else:
                print(f"❌ Admin profile access failed - Status: {profile_response.status_code}")
                print(f"Response: {profile_response.text}")
        else:
            print("❌ No admin access token received")
    else:
        print(f"❌ Admin login failed: {login_response.status_code}")

def test_offers_access():
    """Test if user can access offers after login"""
    
    print("\n🔍 Testing offers access after user login...")
    
    # Login with the test user
    user_email = "udevetyffi-0610@yopmail.com"
    user_password = "udevetyffi-0610@yopmail.com"
    
    # Login first
    login_data = {
        "email": user_email,
        "password": user_password
    }
    
    login_response = requests.post("http://localhost:8080/api/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        access_token = login_result.get('accessToken', login_result.get('token', ''))
        
        if access_token:
            print("✅ User login successful, testing offers access...")
            
            # Test accessing offers (should be public)
            offers_response = requests.get("http://localhost:8080/api/offers")
            print(f"Public offers access: {offers_response.status_code}")
            
            # Test accessing offers with auth header (should work the same for public endpoint)
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            auth_offers_response = requests.get("http://localhost:8080/api/offers", headers=headers)
            print(f"Auth offers access: {auth_offers_response.status_code}")
            
            # Test purchasing an offer
            if auth_offers_response.status_code == 200:
                offers = auth_offers_response.json()
                if offers:
                    first_offer_id = offers[0]['id']
                    print(f"Testing purchase for offer ID: {first_offer_id}")
                    
                    purchase_response = requests.post(f"http://localhost:8080/api/offers/{first_offer_id}/purchase", headers=headers)
                    print(f"Purchase response: {purchase_response.status_code}")
                    
                    if purchase_response.status_code == 200:
                        print("✅ Purchase successful - user is properly authenticated")
                    else:
                        print(f"❌ Purchase failed - {purchase_response.text}")
                else:
                    print("❌ No offers available to test")
        else:
            print("❌ No access token received")
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    print("Testing user profile and authentication endpoints...")
    print("="*60)
    
    test_user_profile_access()
    test_admin_profile_access()
    test_offers_access()
    
    print("\n" + "="*60)
    print("Testing completed.")
    print("\nIf user profile access fails, that's likely the cause of the")
    print("redirect issue - the Angular app can't verify the user is logged in.")