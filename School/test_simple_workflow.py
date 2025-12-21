import requests
import json
import time

# Base URL for the Spring Boot application
BASE_URL = "http://localhost:8080"

# User credentials
USER_DATA = {
    "firstname": "Simple",
    "lastname": "Tester",
    "email": "simple.tester@example.com",
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

def test_endpoints():
    """Test various endpoints to see which ones work"""
    print("🔍 Testing available endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/actuator/health")
        print(f"Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    # Test auth endpoints
    try:
        response = requests.get(f"{BASE_URL}/api/auth/login")
        print(f"Auth login GET: {response.status_code}")
    except Exception as e:
        print(f"Auth login GET error: {e}")
        
    try:
        response = requests.get(f"{BASE_URL}/api/auth/register")
        print(f"Auth register GET: {response.status_code}")
    except Exception as e:
        print(f"Auth register GET error: {e}")

def main():
    """Main function to run a simple test"""
    print("=" * 50)
    print("🚀 Starting Simple Spring Boot Test")
    print("=" * 50)
    
    # First test available endpoints
    test_endpoints()
    
    # Try to register a user
    print("\n📝 Testing user registration...")
    register_response = register_user()
    
    if register_response:
        print("\n🔐 Testing user login...")
        login_response = login_user()
        
        if login_response:
            token = login_response.get("accessToken")
            if token:
                print(f"✅ Got access token: {token[:20]}...")
            else:
                print("❌ No access token in login response")
        else:
            print("❌ Login failed")
    else:
        print("❌ Registration failed")

if __name__ == "__main__":
    main()