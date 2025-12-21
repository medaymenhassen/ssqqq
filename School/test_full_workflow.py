import requests
import json

# Base URL for the Spring Boot application
BASE_URL = "http://localhost:8080"

# User credentials
USER_DATA = {
    "firstname": "Test",
    "lastname": "User",
    "email": "test.user@example.com",
    "password": "password123",
    "rgpdAccepted": True,
    "ccpaAccepted": False
}

# Lesson data
LESSON_DATA = {
    "title": "Introduction to Python Testing",
    "description": "Learn how to test Python applications with Spring Boot backend",
    "videoUrl": "https://example.com/video.mp4",
    "animation3dUrl": "https://example.com/animation.obj",
    "contentTitle": "Python Testing Basics",
    "contentDescription": "Understanding the fundamentals of Python testing",
    "displayOrder": 1,
    "lessonOrder": 1,
    "isService": False
}
# Test data
TEST_DATA = {
    "title": "Python Testing Quiz",
    "description": "Test your knowledge of Python testing concepts",
    "passingScore": 70,
    "timeLimitMinutes": 30,
    "courseId": None  # Will be set after lesson creation
}
# Questions data
QUESTIONS_DATA = [
    {
        "questionText": "What is the purpose of unit testing?",
        "questionOrder": 1,
        "points": 10,
        "questionType": "MCQ",
        "courseTestId": None  # Will be set after test creation
    },
    {
        "questionText": "Which Python library is commonly used for testing?",
        "questionOrder": 2,
        "points": 10,
        "questionType": "MCQ",
        "courseTestId": None
    },
    {
        "questionText": "What does TDD stand for?",
        "questionOrder": 3,
        "points": 10,
        "questionType": "MCQ",
        "courseTestId": None
    }
]# Answers data for each question
ANSWERS_DATA = [
    # Answers for question 1
    [
        {
            "answerText": "To verify that individual units of code work correctly",
            "isLogical": "true",
            "isCorrect": "true",
            "answerOrder": 1
        },
        {
            "answerText": "To make the code run faster",
            "isLogical": "true",
            "isCorrect": "false",
            "answerOrder": 2
        },
        {
            "answerText": "To deploy the application",
            "isLogical": "true",
            "isCorrect": "false",
            "answerOrder": 3
        }
    ],
    # Answers for question 2
    [
        {
            "answerText": "unittest",
            "isLogical": "true",
            "isCorrect": "true",
            "answerOrder": 1
        },
        {
            "answerText": "pytest",
            "isLogical": "true",
            "isCorrect": "true",
            "answerOrder": 2
        },
        {
            "answerText": "requests",
            "isLogical": "true",
            "isCorrect": "false",
            "answerOrder": 3
        }
    ],
    # Answers for question 3
    [
        {
            "answerText": "Test-Driven Development",
            "isLogical": "true",
            "isCorrect": "true",
            "answerOrder": 1
        },
        {
            "answerText": "Test Data Distribution",
            "isLogical": "true",
            "isCorrect": "false",
            "answerOrder": 2
        },
        {
            "answerText": "Time-Delayed Deployment",
            "isLogical": "true",
            "isCorrect": "false",
            "answerOrder": 3
        }
    ]]

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

def create_lesson(token):
    """Create a course lesson"""
    print("📚 Creating course lesson...")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/course-lessons"
    response = requests.post(url, json=LESSON_DATA, headers=headers)
    
    if response.status_code == 200:
        lesson = response.json()
        print(f"✅ Lesson created successfully with ID: {lesson['id']}")
        return lesson
    else:
        print(f"❌ Lesson creation failed with status code {response.status_code}")
        print(response.text)
        return None

def create_test(token, lesson_id):
    """Create a course test"""
    print("📝 Creating course test...")
    headers = {"Authorization": f"Bearer {token}"}
    test_data = TEST_DATA.copy()
    test_data["courseId"] = lesson_id
    
    url = f"{BASE_URL}/api/tests/course-tests"
    response = requests.post(url, json=test_data, headers=headers)
    
    if response.status_code == 200:
        test = response.json()
        print(f"✅ Test created successfully with ID: {test['id']}")
        return test
    else:
        print(f"❌ Test creation failed with status code {response.status_code}")
        print(response.text)
        return None

def create_question(token, question_data):
    """Create a test question"""
    print(f"❓ Creating question: {question_data['questionText'][:50]}...")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/tests/questions"
    response = requests.post(url, json=question_data, headers=headers)
    
    if response.status_code == 200:
        question = response.json()
        print(f"✅ Question created successfully with ID: {question['id']}")
        return question
    else:
        print(f"❌ Question creation failed with status code {response.status_code}")
        print(response.text)
        return None

def create_answer(token, answer_data):
    """Create a test answer"""
    print(f"💬 Creating answer: {answer_data['answerText'][:50]}...")
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/api/tests/answers"
    response = requests.post(url, json=answer_data, headers=headers)
    
    if response.status_code == 200:
        answer = response.json()
        print(f"✅ Answer created successfully with ID: {answer['id']}")
        return answer
    else:
        print(f"❌ Answer creation failed with status code {response.status_code}")
        print(response.text)
        return None

def main():
    """Main function to run the complete workflow"""
    print("=" * 50)
    print("🚀 Starting Spring Boot Test Workflow")
    print("=" * 50)
    
    # Step 1: Register user
    register_response = register_user()
    if not register_response:
        print("💥 Workflow failed at registration step")
        return
    
    # Get user ID from registration response
    # Note: The response doesn't directly contain user ID, so we'll need to get it from login
    user_id = 1  # Placeholder - we'll update this after login
    
    # Step 2: Login user
    login_response = login_user()
    if not login_response:
        print("💥 Workflow failed at login step")
        return
    
    # Extract JWT token
    token = login_response.get("accessToken")
    if not token:
        print("💥 No access token found in login response")
        return
    
    # User ID is handled automatically by the service
    pass    
    # Step 3: Create lesson
    lesson = create_lesson(token)
    if not lesson:
        print("💥 Workflow failed at lesson creation step")
        return
    
    lesson_id = lesson["id"]
    TEST_DATA["courseId"] = lesson_id
    
    # Step 4: Create test
    test = create_test(token, lesson_id)
    if not test:
        print("💥 Workflow failed at test creation step")
        return
    
    test_id = test["id"]
    
    # Step 5 & 6: Create questions and answers
    for i, question_data in enumerate(QUESTIONS_DATA):
        # Update question with test ID
        question_data["courseTestId"] = test_id
                # Create question
        question = create_question(token, question_data)
        if not question:
            print(f"💥 Workflow failed at question {i+1} creation step")
            return
        
        question_id = question["id"]
        
        # Update answers with question ID and user ID
        for answer_data in ANSWERS_DATA[i]:
            answer_data["questionId"] = question_id
            answer_data["userId"] = user_id
            
            # Create answer
            answer = create_answer(token, answer_data)
            if not answer:
                print(f"💥 Workflow failed at answer creation for question {i+1}")
                return
    
    print("=" * 50)
    print("🎉 All steps completed successfully!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   👤 User registered and logged in")
    print(f"   📚 Lesson created (ID: {lesson_id})")
    print(f"   📝 Test created (ID: {test_id})")
    print(f"   ❓ 3 Questions created")
    print(f"   💬 9 Answers created (3 for each question)")

if __name__ == "__main__":
    main()