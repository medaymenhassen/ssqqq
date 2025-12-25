#!/usr/bin/env python3
"""
Script to add sample lesson and offer data via API calls to the Spring Boot backend
This script demonstrates how to add data using the existing API endpoints
"""

import requests
import json

def add_sample_data_via_api():
    """Add sample lesson and offer data via API calls"""
    
    # Base URL for the Spring Boot backend
    base_url = "http://localhost:8080"
    
    print("Adding sample data via Spring Boot API...")
    
    # Sample lesson data
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
    
    # Sample offer data
    offer_data = {
        "title": "Pack Premium - Formation Mécanique Avancée",
        "description": "* Formation Complète en Mécanique\nDécouvrez notre pack premium qui comprends tous les modules de formation en mécanique.\n\n* Contenu Inclus\n- 50 leçons interactives sur la mécanique\n- Animations 3D détaillées\n- Exercices pratiques et évaluations\n- Support technique 24/7\n- Certification à la fin du parcours\n\n* Avantages\n- Accès illimité à tous les contenus\n- Mise à jour régulière du contenu\n- Communauté d'apprenants\n- Suivi personnalisé de votre progression",
        "price": 299.99,
        "durationHours": 6,
        "userTypeId": 1,
        "isActive": True
    }
    
    print("\n1. Adding sample lesson...")
    try:
        lesson_response = requests.post(
            f"{base_url}/api/course-lessons",
            json=lesson_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if lesson_response.status_code in [200, 201]:
            lesson_result = lesson_response.json()
            print("✅ Lesson successfully added!")
            print(f"Lesson ID: {lesson_result.get('id')}, Title: {lesson_result.get('title')}")
        else:
            print(f"❌ Failed to add lesson. Status code: {lesson_response.status_code}")
            print(f"Response: {lesson_response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Spring Boot backend server.")
        print("Please make sure your Spring Boot server is running on http://localhost:8080")
    except Exception as e:
        print(f"❌ Error occurred while adding lesson: {str(e)}")
    
    print("\n2. Adding sample offer...")
    try:
        offer_response = requests.post(
            f"{base_url}/api/offers",
            json=offer_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if offer_response.status_code in [200, 201]:
            offer_result = offer_response.json()
            print("✅ Offer successfully added!")
            print(f"Offer ID: {offer_result.get('id')}, Title: {offer_result.get('title')}")
        else:
            print(f"❌ Failed to add offer. Status code: {offer_response.status_code}")
            print(f"Response: {offer_response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Spring Boot backend server.")
    except Exception as e:
        print(f"❌ Error occurred while adding offer: {str(e)}")
    
    print("\n3. Verifying data...")
    try:
        # Get all lessons
        lessons_response = requests.get(f"{base_url}/api/course-lessons")
        if lessons_response.status_code == 200:
            lessons = lessons_response.json()
            print(f"📚 Found {len(lessons)} lessons in the database")
            for lesson in lessons:
                print(f"   - {lesson.get('title', 'No title')}")
        else:
            print(f"❌ Failed to fetch lessons: {lessons_response.status_code}")
        
        # Get all offers
        offers_response = requests.get(f"{base_url}/api/offers")
        if offers_response.status_code == 200:
            offers = offers_response.json()
            print(f"🏷️  Found {len(offers)} offers in the database")
            for offer in offers:
                print(f"   - {offer.get('title', 'No title')} - €{offer.get('price', '0.00')}")
        else:
            print(f"❌ Failed to fetch offers: {offers_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Spring Boot backend server for verification.")
    except Exception as e:
        print(f"❌ Error occurred during verification: {str(e)}")

def show_api_endpoints():
    """Show the available API endpoints"""
    print("\nAvailable API Endpoints:")
    print("GET    /api/course-lessons     - Get all lessons")
    print("POST   /api/course-lessons     - Create a new lesson")
    print("GET    /api/course-lessons/{id} - Get lesson by ID")
    print("PUT    /api/course-lessons/{id} - Update lesson")
    print("DELETE /api/course-lessons/{id} - Delete lesson")
    print("")
    print("GET    /api/offers             - Get all active offers")
    print("POST   /api/offers             - Create a new offer")
    print("GET    /api/offers/{id}        - Get offer by ID")
    print("PUT    /api/offers/{id}        - Update offer")
    print("DELETE /api/offers/{id}        - Delete offer")

if __name__ == "__main__":
    print("Sample Data API Script")
    print("="*50)
    add_sample_data_via_api()
    show_api_endpoints()