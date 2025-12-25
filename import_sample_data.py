#!/usr/bin/env python3
"""
Script to import sample lesson and offer data via API calls to the Django backend
This script adds the example data we created earlier to the database
"""

import requests
import json
import time

def import_sample_data():
    """Import sample lesson and offer data via API calls"""
    
    # Base URL for the Django backend (assuming it's running on default port)
    base_url = "http://localhost:8000"
    
    # First, let's try to register an admin user or use an existing one
    # For now, we'll assume we can make direct API calls without authentication
    # for testing purposes
    
    print("Importing sample data...")
    
    # Try to load the example lesson we created earlier
    try:
        with open('mechanics_lesson_api_payload.json', 'r', encoding='utf-8') as f:
            lesson_data = json.load(f)
    except FileNotFoundError:
        print("Lesson example file not found, creating sample lesson...")
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
    
    # Try to load the example offer we created earlier
    try:
        with open('offer_api_payload.json', 'r', encoding='utf-8') as f:
            offer_data = json.load(f)
    except FileNotFoundError:
        print("Offer example file not found, creating sample offer...")
        offer_data = {
            "title": "Pack Premium - Formation Mécanique Avancée",
            "description": "* Formation Complète en Mécanique\nDécouvrez notre pack premium qui comprends tous les modules de formation en mécanique.\n\n* Contenu Inclus\n- 50 leçons interactives sur la mécanique\n- Animations 3D détaillées\n- Exercices pratiques et évaluations\n- Support technique 24/7\n- Certification à la fin du parcours\n\n* Avantages\n- Accès illimité à tous les contenus\n- Mise à jour régulière du contenu\n- Communauté d'apprenants\n- Suivi personnalisé de votre progression",
            "price": 299.99,
            "duration": "6 mois",
            "features": [
                "50 leçons interactives",
                "Animations 3D détaillées", 
                "Exercices pratiques",
                "Support technique 24/7",
                "Certification incluse",
                "Accès illimité",
                "Mise à jour continue"
            ],
            "imageUrl": "https://example.com/premium-pack-image.jpg",
            "videoUrl": "https://example.com/premium-pack-video.mp4",
            "isActive": True
        }
    
    print("\n1. Attempting to add sample lesson...")
    try:
        lesson_response = requests.post(
            f"{base_url}/api/course-lessons/",
            json=lesson_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if lesson_response.status_code in [200, 201]:
            print("✅ Lesson successfully added!")
            print(f"Response: {lesson_response.json()}")
        else:
            print(f"❌ Failed to add lesson. Status code: {lesson_response.status_code}")
            print(f"Response: {lesson_response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django backend server.")
        print("Please make sure your Django backend server is running on http://localhost:8000")
        print("\nTo start the Django server:")
        print("1. Navigate to the assistance directory: cd assistance")
        print("2. Activate your virtual environment: .venv\\Scripts\\activate")
        print("3. Run: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error occurred while adding lesson: {str(e)}")
    
    print("\n2. Attempting to add sample offer...")
    try:
        offer_response = requests.post(
            f"{base_url}/api/offers/",
            json=offer_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if offer_response.status_code in [200, 201]:
            print("✅ Offer successfully added!")
            print(f"Response: {offer_response.json()}")
        else:
            print(f"❌ Failed to add offer. Status code: {offer_response.status_code}")
            print(f"Response: {offer_response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django backend server.")
        print("Please make sure your Django backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error occurred while adding offer: {str(e)}")
    
    print("\n3. Verifying data import...")
    try:
        # Check lessons
        lessons_response = requests.get(f"{base_url}/api/course-lessons/")
        if lessons_response.status_code == 200:
            lessons = lessons_response.json()
            print(f"📚 Found {len(lessons)} lessons in the database")
        else:
            print(f"❌ Failed to fetch lessons: {lessons_response.status_code}")
        
        # Check offers
        offers_response = requests.get(f"{base_url}/api/offers/")
        if offers_response.status_code == 200:
            offers = offers_response.json()
            print(f"🏷️  Found {len(offers)} offers in the database")
        else:
            print(f"❌ Failed to fetch offers: {offers_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django backend server for verification.")
    except Exception as e:
        print(f"❌ Error occurred during verification: {str(e)}")

def start_django_server():
    """Helper function to start the Django server"""
    print("\nTo start the Django server, run these commands in a new terminal:")
    print("cd e:\\final\\3Dproject\\assistance")
    print(".venv\\Scripts\\activate")  # For Windows
    print("python manage.py runserver")

if __name__ == "__main__":
    print("Sample Data Import Script")
    print("="*50)
    import_sample_data()
    start_django_server()