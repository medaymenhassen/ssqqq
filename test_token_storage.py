import requests
import json

def test_token_storage():
    """Test token storage and authentication flow"""
    
    print("🔍 Testing token storage and authentication flow...")
    
    # Step 1: Login
    user_email = "udevetyffi-0610@yopmail.com"
    user_password = "udevetyffi-0610@yopmail.com"
    
    login_data = {
        "email": user_email,
        "password": user_password
    }
    
    print("1. Logging in user...")
    login_response = requests.post("http://localhost:8080/api/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        access_token = login_result.get('accessToken', login_result.get('token', ''))
        refresh_token = login_result.get('refreshToken', login_result.get('token', ''))
        
        print(f"✅ Login successful")
        print(f"Access token length: {len(access_token) if access_token else 0}")
        print(f"Has refresh token: {'Yes' if refresh_token and refresh_token != access_token else 'No'}")
        
        # Step 2: Test the token by accessing protected endpoints
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("\n2. Testing token with various endpoints...")
        
        # Test user profile
        profile_response = requests.get("http://localhost:8080/api/user/profile", headers=headers)
        print(f"Profile access: {profile_response.status_code}")
        
        # Test offers endpoint with auth
        offers_response = requests.get("http://localhost:8080/api/offers", headers=headers)
        print(f"Offers access: {offers_response.status_code}")
        
        # Step 3: Decode the JWT token to see its contents
        if access_token:
            import base64
            try:
                # Split the token and decode the payload
                token_parts = access_token.split('.')
                if len(token_parts) == 3:
                    # Add padding if needed
                    payload = token_parts[1]
                    # Add padding to make length multiple of 4
                    payload += '=' * (4 - len(payload) % 4)
                    
                    decoded_payload = base64.b64decode(payload)
                    payload_json = json.loads(decoded_payload)
                    
                    print(f"\n3. JWT Token Payload:")
                    print(f"  Subject (email): {payload_json.get('sub', 'N/A')}")
                    print(f"  Role: {payload_json.get('role', 'N/A')}")
                    print(f"  Expiration: {payload_json.get('exp', 'N/A')}")
                    print(f"  Issued at: {payload_json.get('iat', 'N/A')}")
                    
            except Exception as e:
                print(f"❌ Error decoding token: {e}")
        
        # Step 4: Test if we can purchase an offer that the user doesn't already have
        print("\n4. Testing purchase with a different approach...")
        
        # First, let's create a new user to test with (if possible)
        # Or find an offer the user hasn't purchased yet
        if offers_response.status_code == 200:
            offers = offers_response.json()
            print(f"Found {len(offers)} offers")
            
            # Try to find an offer that might not be purchased yet
            # For now, let's just verify the user state
            print("User state verified - token is valid and working with API")
    
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")

def simulate_frontend_auth():
    """Simulate what happens in the frontend authentication"""
    
    print("\n🔍 Simulating frontend authentication...")
    
    # The issue is likely that after login, the Angular app needs to:
    # 1. Store the token in localStorage
    # 2. Load the current user profile to set up the authentication state
    # 3. Maintain this state across page navigations
    
    print("Frontend authentication flow:")
    print("1. User logs in via login form")
    print("2. AuthService.login() is called")
    print("3. Token is stored in localStorage")
    print("4. loadCurrentUser() is called to set up user state")
    print("5. User is redirected (in this case to /bodyanalytics)")
    print("6. When user navigates to offers page and clicks 'Acheter',")
    print("   the authentication state should still be valid")
    
    print("\nPotential issues:")
    print("- Token not stored properly in localStorage")
    print("- User state not properly initialized after login")
    print("- Redirect after login might be causing state loss")
    print("- Authentication interceptor not adding token to purchase request")
    print("- Browser storage (localStorage) not accessible due to security policies")

def check_cors_issues():
    """Check for potential CORS issues"""
    
    print("\n🔍 Checking for CORS issues...")
    
    # Make a request with proper headers to check CORS
    headers = {
        'Origin': 'http://localhost:4200',
        'Referer': 'http://localhost:4200/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.options("http://localhost:8080/api/auth/login", headers=headers)
    print(f"CORS preflight response: {response.status_code}")
    
    # Check CORS headers in a regular request
    response = requests.get("http://localhost:8080/api/offers")
    cors_headers = [header for header in response.headers if 'cors' in header.lower() or 'allow' in header.lower()]
    print(f"CORS-related headers: {cors_headers}")

if __name__ == "__main__":
    print("Testing token storage and authentication flow...")
    print("="*60)
    
    test_token_storage()
    simulate_frontend_auth()
    check_cors_issues()
    
    print("\n" + "="*60)
    print("The most likely cause of the redirect to login is:")
    print("1. The token is not being properly stored in localStorage after login")
    print("2. The Angular authentication state is not being maintained")
    print("3. The redirect to /bodyanalytics after login might be interfering with auth state")