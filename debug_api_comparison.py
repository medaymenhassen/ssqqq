#!/usr/bin/env python3
"""
Debug API Comparison Script
This script compares what the frontend sends and what the backend expects
to help identify API communication issues.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional


class APIComparator:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        # You may need to set authentication headers here
        self.session.headers.update({
            'Content-Type': 'application/json',
            # Add authorization header if needed
            # 'Authorization': 'Bearer YOUR_TOKEN_HERE'
        })
        
    def login_admin(self, email: str, password: str) -> Optional[str]:
        """
        Login with admin credentials to get access token
        """
        print(f"Attempting to login with admin credentials...")
        print(f"Email: {email}")
        
        login_url = f"{self.base_url}/api/auth/login"
        
        try:
            response = self.session.post(login_url, json={
                'email': email,
                'password': password
            })
            
            print(f"Login Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    access_token = response_data.get('accessToken')
                    if access_token:
                        print("✓ Login successful! Token received.")
                        # Update session headers with the token
                        self.session.headers.update({
                            'Authorization': f'Bearer {access_token}'
                        })
                        return access_token
                    else:
                        print("⚠ Login response doesn't contain access token")
                        print(f"Response: {response_data}")
                        return None
                except json.JSONDecodeError:
                    print(f"⚠ Login response is not JSON: {response.text}")
                    return None
            else:
                print(f"✗ Login failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error text: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request Error during login: {e}")
            return None
    
    def test_user_pending_offers(self, user_id: int, access_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Test the endpoint that's causing the error: /api/offers/user/{userId}/pending
        """
        print(f"Testing: GET {self.base_url}/api/offers/user/{user_id}/pending")
        
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}'
            })
        
        try:
            response = self.session.get(f"{self.base_url}/api/offers/user/{user_id}/pending")
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'data': response_data if 'response_data' in locals() else response.text,
                'success': response.status_code == 200
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return {
                'status_code': None,
                'headers': None,
                'data': str(e),
                'success': False
            }
    
    def test_user_approved_offers(self, user_id: int, access_token: Optional[str] = None) -> Dict[str, Any]:
        """Test approved offers endpoint"""
        print(f"\nTesting: GET {self.base_url}/api/offers/user/{user_id}/approved")
        
        # Authorization header should already be set from login
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}'
            })
        
        try:
            response = self.session.get(f"{self.base_url}/api/offers/user/{user_id}/approved")
            print(f"Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            
            return {
                'status_code': response.status_code,
                'data': response_data if 'response_data' in locals() else response.text,
                'success': response.status_code == 200
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return {
                'status_code': None,
                'data': str(e),
                'success': False
            }
    
    def test_user_rejected_offers(self, user_id: int, access_token: Optional[str] = None) -> Dict[str, Any]:
        """Test rejected offers endpoint"""
        print(f"\nTesting: GET {self.base_url}/api/offers/user/{user_id}/rejected")
        
        # Authorization header should already be set from login
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}'
            })
        
        try:
            response = self.session.get(f"{self.base_url}/api/offers/user/{user_id}/rejected")
            print(f"Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            
            return {
                'status_code': response.status_code,
                'data': response_data if 'response_data' in locals() else response.text,
                'success': response.status_code == 200
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return {
                'status_code': None,
                'data': str(e),
                'success': False
            }
    
    def test_user_purchased_offers(self, user_id: int, access_token: Optional[str] = None) -> Dict[str, Any]:
        """Test purchased offers endpoint"""
        print(f"\nTesting: GET {self.base_url}/api/offers/user/{user_id}/purchases")
        
        # Authorization header should already be set from login
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}'
            })
        
        try:
            response = self.session.get(f"{self.base_url}/api/offers/user/{user_id}/purchases")
            print(f"Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            
            return {
                'status_code': response.status_code,
                'data': response_data if 'response_data' in locals() else response.text,
                'success': response.status_code == 200
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return {
                'status_code': None,
                'data': str(e),
                'success': False
            }
    
    def analyze_hibernate_proxy_issue(self, user_id: int, access_token: Optional[str] = None):
        """
        Specifically analyze the Hibernate proxy issue
        """
        print("\n" + "="*60)
        print("HIBERNATE PROXY ISSUE ANALYSIS")
        print("="*60)
        print("The error 'ByteBuddyInterceptor' indicates Hibernate is returning")
        print("a proxy object instead of the actual entity data.")
        print("This usually happens when:")
        print("1. Lazy loading is triggered outside of a session context")
        print("2. The entity relationships are not properly initialized")
        print("3. JSON serialization tries to access lazy-loaded properties")
        print()
        
        # Test all endpoints to see which ones have the issue
        endpoints = [
            ('pending', self.test_user_pending_offers),
            ('approved', self.test_user_approved_offers), 
            ('rejected', self.test_user_rejected_offers),
            ('purchases', self.test_user_purchased_offers)
        ]
        
        results = {}
        for name, method in endpoints:
            print(f"\n--- Testing {name} offers ---")
            result = method(user_id, access_token)
            results[name] = result
            
        print("\n" + "="*60)
        print("SUMMARY OF API RESPONSES")
        print("="*60)
        for name, result in results.items():
            status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
            print(f"{name.upper()}: {status} (Status: {result['status_code']})")
        
        return results


def main():
    print("API Debug Comparison Tool")
    print("="*50)
    
    # Configuration
    base_url = input("Enter backend URL (default: http://localhost:8080): ").strip()
    if not base_url:
        base_url = "http://localhost:8080"
    
    # Admin login first - use default known credentials
    print("\n--- ADMIN LOGIN ---")
    print("Using known admin credentials: mohamed@admin.com / mohamed0192837465MED")
    admin_email = "mohamed@admin.com"
    admin_password = "mohamed0192837465MED"
    
    # Create comparator instance
    comparator = APIComparator(base_url)
    
    # Login first
    access_token = comparator.login_admin(admin_email, admin_password)
    
    if not access_token:
        print("\n❌ Failed to login. Exiting.")
        return
    
    print(f"\n--- API TESTING ---")
    try:
        user_id = int(input("Enter user ID to test (default: 5): ").strip() or "5")
    except ValueError:
        user_id = 5
    
    # Run the analysis
    results = comparator.analyze_hibernate_proxy_issue(user_id, access_token)
    
    print("\n" + "="*60)
    print("TROUBLESHOOTING SUGGESTIONS")
    print("="*60)
    print("If you see 400 errors with ByteBuddyInterceptor:")
    print()
    print("1. BACKEND FIX - In your Java entities, add @JsonIgnoreProperties or @JsonBackReference")
    print("   to break circular dependencies or lazy-loaded relationships")
    print()
    print("2. BACKEND FIX - Use @EntityGraph or @NamedEntityGraph to fetch related entities")
    print("   eagerly in your repository methods")
    print()
    print("3. BACKEND FIX - In your service methods, ensure all needed properties are")
    print("   initialized before returning the entities")
    print()
    print("4. FRONTEND - The response might contain proxy objects that can't be serialized")
    print("   properly. Check if your backend is returning actual entity data.")
    print()
    print("Example Java fix in your OfferService:")
    print("@EntityGraph(attributePaths = {\"user\", \"offer\"})")
    print("public List<UserOffer> getUserPendingOffers(Long userId) { ... }")


if __name__ == "__main__":
    main()