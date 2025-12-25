#!/usr/bin/env python3
"""
Script to add sample lesson and offer data via API calls with proper authentication
This script demonstrates the full workflow: register, login, get JWT token, then create data
"""

import requests
import json

def register_user():
    """Register a new user"""
    base_url = "http://localhost:8080"
    
    user_data = {
        "email": "testuser@example.com",
        "firstname": "Test",
        "lastname": "User",
        "password": "password123",
        "rgpdAccepted": True,
        "ccpaAccepted": True,
        "commercialUseConsent": True
    }
    
    print("1. Registering user...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            print("✅ User registered successfully!")
            return True, "testuser@example.com", "password123"
        elif response.status_code == 400 and "Email already registered" in response.text:
            print("⚠️  User already exists, will try to login with test credentials")
            return True, "testuser@example.com", "password123"  # Return success but indicate existing user
        else:
            print(f"❌ Registration failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None, None
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return False, None, None

def login_user(email, password):
    """Login user and get JWT token"""
    base_url = "http://localhost:8080"
    
    login_data = {
        "email": email,
        "password": password
    }
    
    print("\n2. Logging in user...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('accessToken') or result.get('token')
            if token:
                print("✅ Login successful! JWT token obtained.")
                return token
            else:
                print("❌ Token not found in response")
                print(f"Response: {result}")
                return None
        else:
            print(f"❌ Login failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def create_offer_with_auth(token):
    """Create an offer with authentication"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    offer_data = {
        "title": "Pack Premium - Formation Mécanique Avancée",
        "description": "* Formation Complète en Mécanique\nDécouvrez notre pack premium qui comprends tous les modules de formation en mécanique.\n\n* Contenu Inclus\n- 50 leçons interactives sur la mécanique\n- Animations 3D détaillées\n- Exercices pratiques et évaluations\n- Support technique 24/7\n- Certification à la fin du parcours\n\n* Avantages\n- Accès illimité à tous les contenus\n- Mise à jour régulière du contenu\n- Communauté d'apprenants\n- Suivi personnalisé de votre progression",
        "price": 299.99,
        "durationHours": 6,
        "userTypeId": 1,
        "isActive": True
    }
    
    print("\n3. Creating offer with authentication...")
    try:
        response = requests.post(
            f"{base_url}/api/offers",
            json=offer_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Offer created successfully!")
            print(f"Offer ID: {result.get('id')}, Title: {result.get('title')}")
            return result.get('id')
        else:
            print(f"❌ Failed to create offer. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Offer creation error: {str(e)}")
        return None

def create_lesson_with_auth(token):
    """Create a lesson with authentication"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    lesson_data = {
        "title": "Introduction à la Mécanique",
        "description": "* Fondements de la Mécanique\nCe cours introduit les concepts fondamentaux de la mécanique.\n\n* Objectifs\n- Comprendre les lois du mouvement\n- Apprendre à calculer les forces\n- Appliquer les principes de la dynamique",
        "videoUrl": "https://example.com/mechanics-intro.mp4",
        "animation3dUrl": "https://example.com/mechanics-intro.glb",
        "contentTitle": "Mécanique - Chapitre 1: Introduction",
        "contentDescription": "* Concepts de Base\n- Position, vitesse et accélération\n- Forces et mouvement\n- Lois de Newton\n\n* Applications Pratiques\n- Mouvement rectiligne uniforme\n- Chute libre\n- Pendule simple",
        "displayOrder": 1,
        "lessonOrder": 1,
        "isService": False
    }
    
    print("\n4. Creating lesson with authentication...")
    try:
        response = requests.post(
            f"{base_url}/api/course-lessons",
            json=lesson_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Lesson created successfully!")
            print(f"Lesson ID: {result.get('id')}, Title: {result.get('title')}")
            return result.get('id')
        else:
            print(f"❌ Failed to create lesson. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Lesson creation error: {str(e)}")
        return None

def create_test_question_with_auth(token, lesson_id):
    """Create a test question with authentication"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    question_data = {
        "questionText": "Quelle est la première loi de Newton ?",
        "questionType": "MCQ",  # Multiple Choice Question
        "points": 5,
        "courseLessonId": lesson_id,  # Link to the lesson we just created (using correct field name)
        "questionOrder": 1
    }
    
    print("\n5. Creating test question with authentication...")
    try:
        response = requests.post(
            f"{base_url}/api/tests/questions",
            json=question_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Test question created successfully!")
            print(f"Question ID: {result.get('id')}, Text: {result.get('questionText')}")
            return result.get('id')
        else:
            print(f"❌ Failed to create test question. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Test question creation error: {str(e)}")
        return None

def verify_data():
    """Verify that data was created and is accessible publicly"""
    base_url = "http://localhost:8080"
    
    print("\n6. Verifying data (public access)...")
    
    # Get all offers
    try:
        offers_response = requests.get(f"{base_url}/api/offers")
        if offers_response.status_code == 200:
            offers = offers_response.json()
            print(f"✅ Found {len(offers)} offers accessible publicly")
            for offer in offers:
                print(f"   - {offer.get('title', 'No title')} - €{offer.get('price', '0.00')}")
        else:
            print(f"❌ Failed to fetch offers: {offers_response.status_code}")
    except Exception as e:
        print(f"❌ Offers verification error: {str(e)}")
    
    # Get all lessons
    try:
        lessons_response = requests.get(f"{base_url}/api/course-lessons")
        if lessons_response.status_code == 200:
            lessons = lessons_response.json()
            print(f"✅ Found {len(lessons)} lessons accessible publicly")
            for lesson in lessons:
                print(f"   - {lesson.get('title', 'No title')}")
        else:
            print(f"❌ Failed to fetch lessons: {lessons_response.status_code}")
    except Exception as e:
        print(f"❌ Lessons verification error: {str(e)}")

def main():
    """Main execution flow"""
    print("Sample Data Creation with Authentication")
    print("="*50)
    
    # Step 1: Register user
    registration_success, email, password = register_user()
    if not registration_success:
        # Try to login with default admin credentials if registration fails
        email = "admin@example.com"
        password = "password123"
        print("⚠️  Trying default admin credentials...")
    
    # Step 2: Login and get token
    token = login_user(email, password)
    if not token:
        print("❌ Cannot proceed without authentication token")
        print("\nNote: You may need to manually register/login via the API or UI first")
        print("Available auth endpoints might be:")
        print("- POST /api/auth/register")
        print("- POST /api/auth/login")
        print("- POST /api/auth/authenticate")
        return
    
    # Step 3: Create offer
    offer_id = create_offer_with_auth(token)
    
    # Step 4: Create lesson
    lesson_id = create_lesson_with_auth(token)
    
    # Step 5: Create test question (if lesson was created)
    if lesson_id:
        question_id = create_test_question_with_auth(token, lesson_id)
    
    # Step 6: Verify data is accessible
    verify_data()
    
    print("\n" + "="*50)
    print("Process completed!")
    print("The homepage should now display the created offers and lessons.")

if __name__ == "__main__":
    main()