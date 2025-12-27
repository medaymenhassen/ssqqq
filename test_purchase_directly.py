import requests
import json

BASE_URL = "http://localhost:8080"

# Create a regular user to test the purchase
regular_user = {
    "firstname": "Test",
    "lastname": "User",
    "email": "testpurchase@example.com",
    "password": "password123",
    "rgpdAccepted": True,
    "ccpaAccepted": True,
    "commercialUseConsent": True
}

print("🔍 Testing purchase functionality as regular user...")

# Register the regular user
print("1. Registering regular user...")
register_response = requests.post(f"{BASE_URL}/api/auth/register", json=regular_user)

if register_response.status_code in [200, 201]:
    print("✅ User registered successfully")
elif "Email already registered" in register_response.text:
    print("⚠️ User already exists")
else:
    print(f"❌ Registration failed: {register_response.status_code}")
    print(f"Response: {register_response.text}")

# Login the regular user
print("\n2. Logging in user...")
login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": regular_user["email"],
    "password": regular_user["password"]
})

if login_response.status_code == 200:
    user_data = login_response.json()
    user_token = user_data.get("accessToken", user_data.get("token", ""))
    print("✅ User logged in successfully")
    print(f"Token: {user_token[:30]}...")  # Show partial token for verification
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    exit(1)

# Get available offers
print("\n3. Fetching available offers...")
headers = {
    "Authorization": f"Bearer {user_token}",
    "Content-Type": "application/json"
}

offers_response = requests.get(f"{BASE_URL}/api/offers", headers=headers)

if offers_response.status_code == 200:
    offers = offers_response.json()
    print(f"✅ Found {len(offers)} offers")
    for i, offer in enumerate(offers):
        print(f"   {i+1}. Offer ID: {offer['id']}, Title: '{offer['title']}', Price: €{offer['price']}")
    
    if offers:
        # Try to purchase the first offer
        selected_offer_id = offers[0]['id']
        print(f"\n4. Attempting to purchase offer ID: {selected_offer_id}")
        
        purchase_response = requests.post(f"{BASE_URL}/api/offers/{selected_offer_id}/purchase", headers=headers)
        
        if purchase_response.status_code == 200:
            purchase_result = purchase_response.json()
            print("✅ Purchase successful!")
            print(f"   - Purchase ID: {purchase_result.get('id')}")
            print(f"   - Approval Status: {purchase_result.get('approvalStatus', 'N/A')}")
            print(f"   - Is Active: {purchase_result.get('isActive', 'N/A')}")
            print(f"   - Purchase Date: {purchase_result.get('purchaseDate', 'N/A')}")
            
            # Check if it's in PENDING status as expected
            if purchase_result.get('approvalStatus') == 'PENDING':
                print("✅ Purchase correctly set to PENDING status for admin approval")
            else:
                print(f"⚠️ Expected PENDING status, but got: {purchase_result.get('approvalStatus')}")
                
        else:
            print(f"❌ Purchase failed with status: {purchase_response.status_code}")
            print(f"Response: {purchase_response.text}")
            
            # Check if it's an authentication issue
            if purchase_response.status_code == 401 or purchase_response.status_code == 403:
                print("⚠️ This might be an authentication/authorization issue")
                
                # Test with admin token to see if the endpoint works
                print("\n   Testing with admin account...")
                admin_login = requests.post(f"{BASE_URL}/api/auth/login", json={
                    "email": "mohamed@admin.com",
                    "password": "mohamed0192837465MED"
                })
                
                if admin_login.status_code == 200:
                    admin_token = admin_login.json().get("accessToken", admin_login.json().get("token", ""))
                    admin_headers = {
                        "Authorization": f"Bearer {admin_token}",
                        "Content-Type": "application/json"
                    }
                    
                    admin_purchase_response = requests.post(f"{BASE_URL}/api/offers/{selected_offer_id}/purchase", headers=admin_headers)
                    print(f"   Admin purchase status: {admin_purchase_response.status_code}")
                    if admin_purchase_response.status_code != 200:
                        print(f"   Admin purchase response: {admin_purchase_response.text}")
    else:
        print("❌ No offers available to purchase")
else:
    print(f"❌ Failed to fetch offers: {offers_response.status_code}")
    print(f"Response: {offers_response.text}")

# Test the purchase endpoint without authentication to confirm the message
print("\n5. Testing purchase without authentication (should fail)...")
no_auth_response = requests.post(f"{BASE_URL}/api/offers/{selected_offer_id if 'selected_offer_id' in locals() else 1}/purchase")
print(f"Response without auth: {no_auth_response.status_code}")
if no_auth_response.status_code == 401:
    print("✅ Unauthenticated requests correctly return 401 Unauthorized")
else:
    print(f"⚠️ Unexpected response for unauthenticated request: {no_auth_response.status_code}")