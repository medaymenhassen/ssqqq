#!/usr/bin/env python3
"""
Script to reset authentication and create sample data with fresh tokens
This handles token expiration issues by creating a new user session
"""

import requests
import json
import time

def create_fresh_user():
    """Create a new user with a unique email to avoid token conflicts"""
    base_url = "http://localhost:8080"
    
    # Use a timestamp to ensure unique email
    timestamp = str(int(time.time()))
    email = f"freshuser_{timestamp}@example.com"
    
    user_data = {
        "email": email,
        "firstname": "Fresh",
        "lastname": "User",
        "password": "password123",
        "rgpdAccepted": True,
        "ccpaAccepted": True,
        "commercialUseConsent": True
    }
    
    print(f"1. Creating fresh user with email: {email}...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            token = result.get('accessToken') or result.get('token')
            if token:
                print("✅ Fresh user created successfully!")
                print(f"   Email: {email}")
                print(f"   Token obtained: {token[:20]}...")
                return token, email, "password123"
            else:
                print("❌ Token not found in registration response")
                return None, None, None
        else:
            print(f"❌ User creation failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None, None
    except Exception as e:
        print(f"❌ User creation error: {str(e)}")
        return None, None, None

def get_fresh_token():
    """Get a fresh token by creating a new user"""
    base_url = "http://localhost:8080"
    
    # Try creating a fresh user first
    token, email, password = create_fresh_user()
    
    if token:
        return token, email, password
    
    # If fresh user creation failed, try with a known admin account
    print("\n⚠️  Trying with default admin credentials...")
    
    login_data = {
        "email": "admin@example.com",
        "password": "password123"
    }
    
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
                print("✅ Got fresh token with admin credentials!")
                return token, "admin@example.com", "password123"
            else:
                print("❌ Token not found in login response")
                return None, None, None
        else:
            print(f"❌ Login failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None, None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None, None, None

def create_offer_with_fresh_token(token):
    """Create an offer with fresh token"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    offer_data = {
        "title": f"Fresh Pack - Formation Mécanique Avancée - {int(time.time())}",
        "description": "* Formation Complète en Mécanique\nDécouvrez notre pack premium qui comprends tous les modules de formation en mécanique.\n\n* Contenu Inclus\n- 50 leçons interactives sur la mécanique\n- Animations 3D détaillées\n- Exercices pratiques et évaluations\n- Support technique 24/7\n- Certification à la fin du parcours\n\n* Avantages\n- Accès illimité à tous les contenus\n- Mise à jour régulière du contenu\n- Communauté d'apprenants\n- Suivi personnalisé de votre progression",
        "price": 299.99,
        "durationHours": 6,
        "userTypeId": 1,
        "isActive": True
    }
    
    print("\n2. Creating offer with fresh token...")
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

def create_lesson_with_fresh_token(token):
    """Create a lesson with fresh token"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    lesson_data = {
        "title": f"Fresh Lesson - Introduction à la Mécanique - {int(time.time())}",
        "description": "* Fondements de la Mécanique\nCe cours introduit les concepts fondamentaux de la mécanique.\n\n* Objectifs\n- Comprendre les lois du mouvement\n- Apprendre à calculer les forces\n- Appliquer les principes de la dynamique",
        "videoUrl": "https://example.com/mechanics-intro.mp4",
        "animation3dUrl": "https://example.com/mechanics-intro.glb",
        "contentTitle": "Mécanique - Chapitre 1: Introduction",
        "contentDescription": "* Concepts de Base\n- Position, vitesse et accélération\n- Forces et mouvement\n- Lois de Newton\n\n* Applications Pratiques\n- Mouvement rectiligne uniforme\n- Chute libre\n- Pendule simple",
        "displayOrder": 1,
        "lessonOrder": 1,
        "isService": False
    }
    
    print("\n3. Creating lesson with fresh token...")
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

def create_test_question_with_fresh_token(token, lesson_id):
    """Create a test question with fresh token"""
    base_url = "http://localhost:8080"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    question_data = {
        "questionText": f"Quelle est la première loi de Newton ? - {int(time.time())}",
        "questionType": "MCQ",
        "points": 5,
        "courseLessonId": lesson_id,
        "questionOrder": 1
    }
    
    print("\n4. Creating test question with fresh token...")
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
    
    print("\n5. Verifying data (public access)...")
    
    # Get all offers
    try:
        offers_response = requests.get(f"{base_url}/api/offers")
        if offers_response.status_code == 200:
            offers = offers_response.json()
            print(f"✅ Found {len(offers)} offers accessible publicly")
            for i, offer in enumerate(offers[-3:]):  # Show last 3 offers
                print(f"   - {offer.get('title', 'No title')} - €{offer.get('price', '0.00')}")
            if len(offers) > 3:
                print(f"   ... and {len(offers)-3} more offers")
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
            for i, lesson in enumerate(lessons[-3:]):  # Show last 3 lessons
                print(f"   - {lesson.get('title', 'No title')}")
            if len(lessons) > 3:
                print(f"   ... and {len(lessons)-3} more lessons")
        else:
            print(f"❌ Failed to fetch lessons: {lessons_response.status_code}")
    except Exception as e:
        print(f"❌ Lessons verification error: {str(e)}")

def main():
    """Main execution flow with fresh authentication"""
    print("Reset Authentication and Create Data")
    print("="*50)
    
    # Step 1: Get fresh token
    token, email, password = get_fresh_token()
    if not token:
        print("❌ Cannot proceed without a valid authentication token")
        return
    
    print(f"✅ Using fresh authentication token for user: {email}")
    
    # Step 2: Create offer
    offer_id = create_offer_with_fresh_token(token)
    
    # Step 3: Create lesson
    lesson_id = create_lesson_with_fresh_token(token)
    
    # Step 4: Create test question (if lesson was created)
    if lesson_id:
        question_id = create_test_question_with_fresh_token(token, lesson_id)
    
    # Step 5: Verify data is accessible
    verify_data()
    
    print("\n" + "="*50)
    print("Process completed with fresh authentication!")
    print("The homepage should now display the newly created offers and lessons.")

if __name__ == "__main__":
    main()