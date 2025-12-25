#!/usr/bin/env python3
"""
Script to test the complete offer approval workflow
This demonstrates the flow: purchase offer -> pending status -> admin approval -> access granted
"""

import requests
import json
import time

def register_and_get_token():
    """Register a new user and get JWT token"""
    base_url = "http://localhost:8080"
    
    timestamp = str(int(time.time()))
    email = f"testuser_{timestamp}@example.com"
    
    user_data = {
        "email": email,
        "firstname": "Test",
        "lastname": "User",
        "password": "password123",
        "rgpdAccepted": True,
        "ccpaAccepted": True,
        "commercialUseConsent": True
    }
    
    print(f"1. Registering user: {email}...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            token = result.get('accessToken') or result.get('token')
            if token:
                print("✅ User registered successfully!")
                return token, email
            else:
                print("❌ Token not found in registration response")
                return None, None
        else:
            print(f"❌ Registration failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return None, None

def create_offer_for_purchase():
    """Create an offer that can be purchased"""
    base_url = "http://localhost:8080"
    
    # First, login as admin to create an offer
    admin_login_data = {
        "email": "admin@example.com",
        "password": "password123"
    }
    
    print("\n2. Logging in as admin to create an offer...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=admin_login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            admin_token = result.get('accessToken') or result.get('token')
            if admin_token:
                print("✅ Admin login successful!")
                
                # Create an offer
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
                
                offer_data = {
                    "title": f"Test Offer for Approval - {int(time.time())}",
                    "description": "Test offer that requires admin approval",
                    "price": 99.99,
                    "durationHours": 10,
                    "userTypeId": 1,
                    "isActive": True
                }
                
                print("3. Creating offer for purchase...")
                response = requests.post(
                    f"{base_url}/api/offers",
                    json=offer_data,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    offer_result = response.json()
                    print(f"✅ Offer created successfully! ID: {offer_result.get('id')}")
                    return offer_result.get('id'), admin_token
                else:
                    print(f"❌ Failed to create offer. Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None, admin_token
            else:
                print("❌ Admin token not found")
                return None, None
        else:
            print(f"❌ Admin login failed. Status: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        return None, None

def purchase_offer(user_token, offer_id):
    """Purchase an offer (should create with PENDING status)"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {user_token}'
    }
    
    print(f"\n4. Purchasing offer {offer_id} as user...")
    try:
        # First, get the user ID from their profile
        profile_response = requests.get(
            f"{base_url}/api/user/profile",
            headers=headers
        )
        
        if profile_response.status_code == 200:
            user_data = profile_response.json()
            user_id = user_data.get('id')
            
            if user_id:
                print(f"✅ Got user ID: {user_id}")
                
                # Now purchase the offer
                response = requests.post(
                    f"{base_url}/api/offers/{offer_id}/purchase",
                    params={'userId': user_id},
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    purchase_result = response.json()
                    print("✅ Offer purchased successfully!")
                    print(f"   Purchase ID: {purchase_result.get('id')}")
                    print(f"   Approval Status: {purchase_result.get('approvalStatus', 'N/A')}")
                    print(f"   Active: {purchase_result.get('isActive', 'N/A')}")
                    return purchase_result.get('id'), user_id
                else:
                    print(f"❌ Failed to purchase offer. Status: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None, user_id
            else:
                print("❌ Could not get user ID")
                return None, None
        else:
            print(f"❌ Failed to get user profile. Status: {profile_response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Purchase error: {str(e)}")
        return None, None

def check_user_pending_offers(user_token, user_id):
    """Check user's pending offers"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {user_token}'
    }
    
    print(f"\n5. Checking user's pending offers...")
    try:
        response = requests.get(
            f"{base_url}/api/offers/user/{user_id}/pending",
            headers=headers
        )
        
        if response.status_code == 200:
            pending_offers = response.json()
            print(f"✅ Found {len(pending_offers)} pending offers")
            for offer in pending_offers:
                print(f"   - Offer ID: {offer.get('id')}, Status: {offer.get('approvalStatus')}")
            return pending_offers
        else:
            print(f"❌ Failed to get pending offers. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Pending offers check error: {str(e)}")
        return []

def admin_approve_offer(admin_token, user_offer_id):
    """Admin approves the user's offer"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }
    
    print(f"\n6. Admin approving offer {user_offer_id}...")
    try:
        response = requests.put(
            f"{base_url}/api/offers/{user_offer_id}/approve",
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            approval_result = response.json()
            print("✅ Offer approved successfully!")
            print(f"   Approval Status: {approval_result.get('approvalStatus')}")
            print(f"   Active: {approval_result.get('isActive')}")
            return True
        else:
            print(f"❌ Failed to approve offer. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Approval error: {str(e)}")
        return False

def check_access_after_approval(user_token, user_id):
    """Check if user has access after approval"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {user_token}'
    }
    
    print(f"\n7. Checking user access after approval...")
    try:
        response = requests.get(
            f"{base_url}/api/offers/user/{user_id}/access",
            headers=headers
        )
        
        if response.status_code == 200:
            has_access = response.json()
            print(f"✅ User access status: {has_access}")
            return has_access
        else:
            print(f"❌ Failed to check access. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Access check error: {str(e)}")
        return False

def main():
    """Main execution flow for testing the approval workflow"""
    print("Testing Complete Offer Approval Workflow")
    print("="*50)
    
    # Step 1: Register user and get token
    user_token, user_email = register_and_get_token()
    if not user_token:
        print("❌ Cannot proceed without user token")
        return
    
    print(f"✅ Using user token for: {user_email}")
    
    # Step 2: Create an offer (as admin)
    offer_id, admin_token = create_offer_for_purchase()
    if not offer_id or not admin_token:
        print("❌ Cannot proceed without an offer to purchase")
        return
    
    # Step 3: Purchase the offer
    user_offer_id, user_id = purchase_offer(user_token, offer_id)
    if not user_offer_id:
        print("❌ Cannot proceed without a purchased offer")
        return
    
    # Step 4: Check pending offers
    pending_offers = check_user_pending_offers(user_token, user_id)
    
    # Step 5: Admin approves the offer
    approval_success = admin_approve_offer(admin_token, user_offer_id)
    if not approval_success:
        print("❌ Approval failed, cannot test access")
        return
    
    # Step 6: Check access after approval
    has_access = check_access_after_approval(user_token, user_id)
    
    print("\n" + "="*50)
    print("Approval workflow test completed!")
    print(f"✅ User can access content after approval: {has_access}")

if __name__ == "__main__":
    main()