import requests
import json
import time

# Base URL for the Spring Boot application
BASE_URL = "http://localhost:8080"

def test_get_all_test_questions():
    """Test getting all test questions"""
    print("❓ Testing GET /api/tests/questions...")
    
    # First, let's try without authentication
    url = f"{BASE_URL}/api/tests/questions"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✅ Successfully retrieved test questions without authentication")
        questions = response.json()
        print(f"   Found {len(questions)} questions")
        if len(questions) > 0:
            print(f"   Sample question: {questions[0]['questionText'] if 'questionText' in questions[0] else 'No question text'}")
    elif response.status_code == 403:
        print("❌ Forbidden error when getting test questions")
        print(f"   Response: {response.text}")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(f"   Response: {response.text}")

def main():
    """Main function to test the test questions endpoint"""
    print("=" * 60)
    print("🚀 Testing Test Questions Endpoint")
    print("=" * 60)
    
    test_get_all_test_questions()
    
    print("=" * 60)
    print("🎉 Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()