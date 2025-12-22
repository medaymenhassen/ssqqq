#!/usr/bin/env python3
"""
Test script to verify frontend-backend communication and CORS
"""

import requests
import json

def test_cors():
    """Test CORS configuration"""
    print("🧪 Testing CORS configuration...")
    
    # Test preflight OPTIONS request
    try:
        response = requests.options("http://localhost:8080/api/auth/login", 
                                  headers={
                                      "Origin": "http://localhost:4200",
                                      "Access-Control-Request-Method": "POST",
                                      "Access-Control-Request-Headers": "Content-Type"
                                  })
        print(f"OPTIONS response status: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
        print(f"Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'NOT SET')}")
    except Exception as e:
        print(f"❌ Error during CORS test: {e}")

def test_basic_connectivity():
    """Test basic connectivity to backend"""
    print("\n🌐 Testing basic connectivity...")
    
    try:
        response = requests.get("http://localhost:8080/api/auth/login", timeout=5)
        print(f"GET /api/auth/login response status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error during connectivity test: {e}")

def test_post_request():
    """Test POST request to auth endpoint"""
    print("\n📧 Testing POST request...")
    
    try:
        response = requests.post("http://localhost:8080/api/auth/login", 
                               json={"email": "test@test.com", "password": "test"},
                               headers={"Content-Type": "application/json"})
        print(f"POST /api/auth/login response status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Server responded correctly with 401 for invalid credentials")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error during POST test: {e}")

def main():
    print("🚀 Starting frontend-backend communication tests...")
    
    test_cors()
    test_basic_connectivity()
    test_post_request()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()