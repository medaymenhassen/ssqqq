import requests
import json
import time

# Base URL for the Spring Boot application
BASE_URL = "http://localhost:8080"

def test_get_all_course_lessons():
    """Test getting all course lessons"""
    print("📚 Testing GET /api/course-lessons...")
    
    # First, let's try without authentication (should work for getAll)
    url = f"{BASE_URL}/api/course-lessons"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("✅ Successfully retrieved course lessons without authentication")
        lessons = response.json()
        print(f"   Found {len(lessons)} lessons")
        if len(lessons) > 0:
            print(f"   Sample lesson: {lessons[0]['title'] if 'title' in lessons[0] else 'No title'}")
    elif response.status_code == 400:
        print("❌ Bad Request error when getting course lessons")
        print(f"   Response: {response.text}")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(f"   Response: {response.text}")

def main():
    """Main function to test the course lessons endpoint"""
    print("=" * 60)
    print("🚀 Testing Course Lessons Endpoint")
    print("=" * 60)
    
    test_get_all_course_lessons()
    
    print("=" * 60)
    print("🎉 Test Completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()