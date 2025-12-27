import requests
import json

BASE_URL = "http://localhost:8080"
ADMIN_USER = {
    "email": "mohamed@admin.com",
    "password": "mohamed0192837465MED"
}

print("Debug: Testing admin login and permissions...")

# Login as admin
login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": ADMIN_USER["email"],
    "password": ADMIN_USER["password"]
})

print(f"Login response status: {login_response.status_code}")

if login_response.status_code == 200:
    login_data = login_response.json()
    print(f"Login response: {json.dumps(login_data, indent=2)}")
    
    token = login_data.get("accessToken", login_data.get("token", ""))
    
    if token:
        print("Token received, testing access to admin endpoints...")
        
        # Test accessing users endpoint (admin only)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        users_response = requests.get(f"{BASE_URL}/api/users", headers=headers)
        print(f"Users endpoint response status: {users_response.status_code}")
        
        if users_response.status_code == 200:
            print("✅ Admin access granted - user has admin privileges")
        else:
            print(f"❌ Admin access denied - {users_response.status_code}")
            print(f"Response: {users_response.text}")
        
        # Test accessing profile
        profile_response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        print(f"Profile endpoint response status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"Profile data: {json.dumps(profile_data, indent=2)}")
        else:
            print(f"❌ Profile access failed - {profile_response.status_code}")
    else:
        print("❌ No token received from login")
else:
    print(f"❌ Login failed - {login_response.status_code}")
    print(f"Response: {login_response.text}")