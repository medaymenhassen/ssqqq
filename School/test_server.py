import requests
import time

def test_server_health():
    """Test if the Spring Boot server is running"""
    try:
        response = requests.get("http://localhost:8080/actuator/health", timeout=5)
        if response.status_code == 200:
            print("✅ Spring Boot server is running and healthy")
            print(f"Status: {response.json()}")
            return True
        else:
            print(f"⚠️ Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Spring Boot server at http://localhost:8080")
        print("Please make sure the Spring Boot application is running")
        return False
    except Exception as e:
        print(f"❌ Error testing server health: {e}")
        return False

def test_cors():
    """Test CORS configuration by making a simple OPTIONS request"""
    try:
        headers = {
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = requests.options("http://localhost:8080/api/auth/register", headers=headers, timeout=5)
        if response.status_code in [200, 204]:
            print("✅ CORS is configured correctly")
            return True
        else:
            print(f"⚠️ CORS test returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing CORS: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Spring Boot Server Configuration")
    print("=" * 50)
    
    # Test server health
    health_ok = test_server_health()
    
    if health_ok:
        # Test CORS if server is healthy
        print("\n🌐 Testing CORS configuration...")
        cors_ok = test_cors()
        
        if cors_ok:
            print("\n🎉 All tests passed! Server is ready for the workflow test.")
        else:
            print("\n⚠️ Server is running but there may be CORS issues.")
    else:
        print("\n💥 Server tests failed. Please check if Spring Boot application is running.")