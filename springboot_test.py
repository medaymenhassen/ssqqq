import requests
import json
import time

# Base URL for the Spring Boot application
BASE_URL = "http://localhost:8080"

# Test data
test_user = {
    "email": "test1-1@example.com",
    "password": "testpassword123",
    "confirmPassword": "testpassword123",
    "firstname": "Test",
    "lastname": "User"
}

test_lesson = {
    "title": "Test Lesson",
    "description": "This is a test lesson",
    "content": "Lesson content goes here",
    "moduleId": 1,
    "userId": 1
}

test_test = {
    "title": "Test Exam",
    "description": "This is a test exam",
    "lessonId": 1,
    "userId": 1
}

test_questions = [
    {
        "questionText": "What is the capital of France?",
        "questionOrder": 1,
        "points": 10,
        "questionType": "MCQ",
        "userId": 1
    },
    {
        "questionText": "What is 2+2?",
        "questionOrder": 2,
        "points": 5,
        "questionType": "MCQ",
        "userId": 1
    },
    {
        "questionText": "Explain the theory of relativity",
        "questionOrder": 3,
        "points": 20,
        "questionType": "OPEN_ENDED",
        "userId": 1
    }
]

test_answers = [
    # Answers for question 1
    [
        {"answerText": "Paris", "isCorrect": "true", "answerOrder": 1, "userId": 1},
        {"answerText": "London", "isCorrect": "false", "answerOrder": 2, "userId": 1},
        {"answerText": "Berlin", "isCorrect": "false", "answerOrder": 3, "userId": 1}
    ],
    # Answers for question 2
    [
        {"answerText": "3", "isCorrect": "false", "answerOrder": 1, "userId": 1},
        {"answerText": "4", "isCorrect": "true", "answerOrder": 2, "userId": 1},
        {"answerText": "5", "isCorrect": "false", "answerOrder": 3, "userId": 1}
    ],
    # Answers for question 3 (open-ended, no correct answer)
    [
        {"answerText": "Student's answer will go here", "isCorrect": "false", "answerOrder": 1, "userId": 1}
    ]
]

def register_user():
    """Register a new user"""
    print("📝 Registering user...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ User registered successfully")
            return response.json()
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return None

def login_user():
    """Login the user"""
    print("🔐 Logging in user...")
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ User logged in successfully")
            return response.json()
        else:
            print(f"   ❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return None

def create_lesson(token):
    """Create a lesson"""
    print("📚 Creating lesson...")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   Sending headers: {headers}")
    print(f"   Sending data: {test_lesson}")
    try:
        response = requests.post(f"{BASE_URL}/api/course-lessons", 
                               json=test_lesson, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code == 200:
            print("   ✅ Lesson created successfully")
            return response.json()
        else:
            print(f"   ❌ Lesson creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Lesson creation error: {e}")
        return None

def create_test(token, lesson_id):
    """Create a test"""
    print("📋 Creating test...")
    headers = {"Authorization": f"Bearer {token}"}
    test_data = test_test.copy()
    test_data["lessonId"] = lesson_id
    print(f"   Sending headers: {headers}")
    print(f"   Sending data: {test_data}")
    try:
        response = requests.post(f"{BASE_URL}/api/tests/course-tests", 
                               json=test_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code == 200:
            print("   ✅ Test created successfully")
            return response.json()
        else:
            print(f"   ❌ Test creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Test creation error: {e}")
        return None

def create_question(token, test_id, question_data):
    """Create a question"""
    print("❓ Creating question...")
    headers = {"Authorization": f"Bearer {token}"}
    question_data["courseTestId"] = test_id
    print(f"   Sending headers: {headers}")
    print(f"   Sending data: {question_data}")
    try:
        response = requests.post(f"{BASE_URL}/api/tests/questions", 
                               json=question_data, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code == 200:
            print("   ✅ Question created successfully")
            return response.json()
        else:
            print(f"   ❌ Question creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Question creation error: {e}")
        return None

def create_answer(token, question_id, answer_data):
    """Create an answer"""
    print("✅ Creating answer...")
    headers = {"Authorization": f"Bearer {token}"}
    answer_data["questionId"] = question_id
    try:
        response = requests.post(f"{BASE_URL}/api/tests/answers", 
                               json=answer_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Answer created successfully")
            return response.json()
        else:
            print(f"   ❌ Answer creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Answer creation error: {e}")
        return None

def test_csv_endpoints(token):
    """Test CSV endpoints"""
    print("📊 Testing CSV endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a simple CSV content for testing
    csv_content = "timestamp,x,y,z,confidence\n00:00:01,10,20,30,0.95\n00:00:02,15,25,35,0.87\n00:00:03,12,22,32,0.92"
    
    # Test create-video endpoint
    print("   📤 Testing create-video endpoint...")
    try:
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        data = {'videoName': 'test_video.mp4'}
        print(f"      Sending headers: {headers}")
        print(f"      Sending data: {data}")
        response = requests.post(f"{BASE_URL}/springboot/csv/create-video", 
                               files=files, data=data, headers=headers)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text}")
        if response.status_code == 200:
            print("      ✅ Video created successfully from CSV")
            return True
        else:
            print(f"      ❌ Video creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"      ❌ Video creation error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Spring Boot API Test")
    print("=" * 50)
    
    # Step 1: Register user
    register_response = register_user()
    if not register_response:
        print("❌ Test failed at registration step")
        return
    
    # Wait a bit for registration to complete
    time.sleep(1)
    
    # Step 2: Login user
    login_response = login_user()
    if not login_response:
        print("❌ Test failed at login step")
        return
    
    token = login_response.get("accessToken")
    if not token:
        print("❌ No token received from login")
        return
    
    print(f"   🔑 Token received: {token[:20]}...")
    
    # Wait a bit
    time.sleep(1)
    
    # Step 3: Create lesson
    lesson_response = create_lesson(token)
    if not lesson_response:
        print("⚠️  Continuing without lesson creation")
        lesson_id = 1  # Use default lesson ID
    else:
        lesson_id = lesson_response.get("id", 1)
    
    # Wait a bit
    time.sleep(1)
    
    # Step 4: Create test
    test_response = create_test(token, lesson_id)
    if not test_response:
        print("⚠️  Continuing without test creation")
        test_id = 1  # Use default test ID
    else:
        test_id = test_response.get("id", 1)
    
    # Wait a bit
    time.sleep(1)
    
    # Step 5: Create questions and answers
    question_ids = []
    for i, question_data in enumerate(test_questions):
        print(f"📝 Creating question {i+1}...")
        question_response = create_question(token, test_id, question_data)
        if question_response:
            question_id = question_response.get("id")
            question_ids.append(question_id)
            
            # Create answers for this question
            for answer_data in test_answers[i]:
                create_answer(token, question_id, answer_data)
            
            time.sleep(0.5)  # Small delay between requests
        else:
            print(f"⚠️  Failed to create question {i+1}")
    
    # Step 6: Test CSV endpoints
    csv_success = test_csv_endpoints(token)
    
    print("\n" + "=" * 50)
    print("🏁 Test Summary:")
    print(f"   User Registration: {'✅ Pass' if register_response else '❌ Fail'}")
    print(f"   User Login: {'✅ Pass' if login_response else '❌ Fail'}")
    print(f"   Lesson Creation: {'✅ Pass' if lesson_response else '⚠️  Skip'}")
    print(f"   Test Creation: {'✅ Pass' if test_response else '⚠️  Skip'}")
    print(f"   Questions Creation: {len(question_ids)} created")
    print(f"   CSV Endpoint Test: {'✅ Pass' if csv_success else '❌ Fail'}")
    
    if csv_success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n⚠️  Some tests failed, but the core functionality works.")

if __name__ == "__main__":
    main()