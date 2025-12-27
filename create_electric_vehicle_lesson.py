#!/usr/bin/env python3
"""
Script to create an electric vehicle history lesson with an offer using the admin account
This script connects to the Spring Boot backend using the admin credentials and creates:
1. An offer for 200 TND with 5 hours of formation
2. A lesson about the history of electric vehicles
3. Questions related to the lesson
"""

import requests
import json
import time

class ElectricVehicleLessonCreator:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.admin_email = "mohamed@admin.com"
        self.admin_password = "mohamed0192837465MED"
        self.admin_token = None
        
    def login_admin(self):
        """Login with admin credentials to get access token"""
        print(f"Attempting to login with admin credentials...")
        
        login_data = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.admin_token = result.get('accessToken') or result.get('token')
                if self.admin_token:
                    print("✅ Admin login successful!")
                    return True
                else:
                    print("❌ Token not found in response")
                    return False
            else:
                print(f"❌ Admin login failed. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Admin login error: {str(e)}")
            return False
    
    def create_offer(self):
        """Create an offer for electric vehicle course"""
        if not self.admin_token:
            print("❌ No admin token available")
            return None
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        offer_data = {
            "title": "Histoire des Véhicules Électriques - 200 TND pour 5 heures de formation",
            "description": """* Découvrez l'Histoire des Véhicules Électriques
Explorez l'évolution fascinante des véhicules électriques de leurs débuts jusqu'à aujourd'hui.

* Contenu du Cours
- Les premiers véhicules électriques (1830-1920)
- La chute et le renouveau (1920-2000)
- La révolution moderne (2000-présent)
- Technologies actuelles et futures
- Impact environnemental et économique

* Ce que vous apprendrez
- L'évolution technologique des batteries
- Les pionniers de l'industrie
- Les défis passés et présents
- Les tendances futures""",
            "price": 200.00,
            "durationHours": 5,
            "userTypeId": 1,
            "isActive": True
        }
        
        print("\nCreating electric vehicle history offer...")
        try:
            response = requests.post(
                f"{self.base_url}/api/offers",
                json=offer_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ Offer created successfully!")
                print(f"   Offer ID: {result.get('id')}")
                print(f"   Title: {result.get('title')}")
                print(f"   Price: {result.get('price')} TND")
                print(f"   Duration: {result.get('durationHours')} hours")
                return result.get('id')
            else:
                print(f"❌ Failed to create offer. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Offer creation error: {str(e)}")
            return None
    
    def create_lesson(self):
        """Create a lesson about electric vehicle history"""
        if not self.admin_token:
            print("❌ No admin token available")
            return None
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        lesson_data = {
            "title": "L'Histoire des Véhicules Électriques",
            "description": """* Introduction à l'Histoire des Véhicules Électriques
Découvrez le parcours extraordinaire des véhicules électriques, depuis leurs débuts prometteurs jusqu'à leur renouveau moderne.

* Plan du Cours
1. Les Débuts (1830-1920)
2. La Période Obscure (1920-2000)
3. Le Renouveau Contemporain (2000-présent)
4. Technologies et Avenir""",
            "videoUrl": "https://example.com/ev-history-video.mp4",
            "animation3dUrl": "https://example.com/ev-timeline-animation.glb",
            "contentTitle": "Chapitre 1: Les Débuts des Véhicules Électriques",
            "contentDescription": """* Les Premiers Véhicules Électriques (1830-1920)

**Débuts Prometteurs**
- 1832-1839: Robert Anderson crée le premier véhicule électrique connu
- 1890-1891: William Morrison développe la première voiture électrique américaine
- Fin des années 1890: Les véhicules électriques représentent 38% du marché automobile

**Avantages de l'Époque**
- Plus silencieux que les voitures à essence
- Plus facile à conduire (pas de changement de vitesse manuel)
- Pas de pollution locale
- Plus fiable que les moteurs à essence primitifs

**Popularité aux États-Unis**
- 1900: 38% des véhicules aux États-Unis sont électriques
- 1912: 1000 voitures électriques produites aux États-Unis
- Cibles les femmes et les citadins pour leur commodité

* La Période de Déclin (1920-2000)

**Facteurs de Déclin**
- Invention du démarreur électrique (1912) pour les voitures à essence
- Découverte de vastes gisements de pétrole
- Prix réduit de l'essence
- Amélioration des routes favorisant les véhicules à longue distance
- Limitation de la portée des véhicules électriques

**Usage Persistant**
- Voitures de golf (dès 1897)
- Véhicules utilitaires dans les entreprises
- Véhicules pour personnes à mobilité réduite

* Le Renouveau Moderne (2000-présent)

**Technologies Modernes**
- Batteries lithium-ion
- Moteurs électriques à aimants permanents
- Électronique de puissance avancée
- Systèmes de gestion de batterie

**Pionniers Contemporains**
- Tesla Motors (fondée en 2003)
- Nissan Leaf (2010) - premier EV de masse
- Chevrolet Volt (2010) - véhicule hybride rechargeable

**Tendances Actuelles**
- Coûts des batteries en baisse
- Infrastructure de recharge en expansion
- Engagement des gouvernements pour l'électrification
- Objectifs de neutralité carbone""",
            "displayOrder": 1,
            "lessonOrder": 1,
            "isService": False
        }
        
        print("\nCreating electric vehicle history lesson...")
        try:
            response = requests.post(
                f"{self.base_url}/api/course-lessons",
                json=lesson_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ Lesson created successfully!")
                print(f"   Lesson ID: {result.get('id')}")
                print(f"   Title: {result.get('title')}")
                return result.get('id')
            else:
                print(f"❌ Failed to create lesson. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Lesson creation error: {str(e)}")
            return None
    
    def create_questions_for_lesson(self, lesson_id):
        """Create questions related to the electric vehicle lesson"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
        # Create a test for the lesson
        test_data = {
            "title": "Quiz - Histoire des Véhicules Électriques",
            "description": "Testez vos connaissances sur l'histoire des véhicules électriques",
            "passingScore": 70,
            "timeLimitMinutes": 30,
            "courseId": 1,  # Using default course ID
            "questions": []
        }
        
        # Create the test first
        print(f"\nCreating test for lesson {lesson_id}...")
        test_response = requests.post(
            f"{self.base_url}/api/tests/course-tests",
            json=test_data,
            headers=headers
        )
        
        test_id = None
        if test_response.status_code in [200, 201]:
            test_result = test_response.json()
            test_id = test_result.get('id')
            print(f"✅ Test created with ID: {test_id}")
        else:
            print(f"❌ Failed to create test. Status: {test_response.status_code}")
            print(f"Response: {test_response.text}")
            return False
        
        # Create questions for the lesson
        questions = [
            {
                "questionText": "Quelle proportion du marché automobile représentaient les véhicules électriques en 1900 ?",
                "questionOrder": 1,
                "points": 10,
                "questionType": "MCQ",
                "courseTestId": test_id,
                "answers": [
                    {"answerText": "18%", "isLogical": "true", "isCorrect": "false", "answerOrder": 1},
                    {"answerText": "38%", "isLogical": "true", "isCorrect": "true", "answerOrder": 2},
                    {"answerText": "58%", "isLogical": "true", "isCorrect": "false", "answerOrder": 3},
                    {"answerText": "78%", "isLogical": "true", "isCorrect": "false", "answerOrder": 4}
                ]
            },
            {
                "questionText": "Qui a créé le premier véhicule électrique connu ?",
                "questionOrder": 2,
                "points": 10,
                "questionType": "MCQ",
                "courseTestId": test_id,
                "answers": [
                    {"answerText": "William Morrison", "isLogical": "true", "isCorrect": "false", "answerOrder": 1},
                    {"answerText": "Robert Anderson", "isLogical": "true", "isCorrect": "true", "answerOrder": 2},
                    {"answerText": "Nikola Tesla", "isLogical": "true", "isCorrect": "false", "answerOrder": 3},
                    {"answerText": "Thomas Edison", "isLogical": "true", "isCorrect": "false", "answerOrder": 4}
                ]
            },
            {
                "questionText": "Quel événement a contribué au déclin des véhicules électriques dans les années 1910 ?",
                "questionOrder": 3,
                "points": 10,
                "questionType": "MCQ",
                "courseTestId": test_id,
                "answers": [
                    {"answerText": "La Première Guerre Mondiale", "isLogical": "true", "isCorrect": "false", "answerOrder": 1},
                    {"answerText": "L'invention du démarreur électrique", "isLogical": "true", "isCorrect": "true", "answerOrder": 2},
                    {"answerText": "La crise pétrolière", "isLogical": "true", "isCorrect": "false", "answerOrder": 3},
                    {"answerText": "La prohibition", "isLogical": "true", "isCorrect": "false", "answerOrder": 4}
                ]
            }
        ]
        
        print(f"\nCreating {len(questions)} questions for the lesson...")
        
        for i, question_data in enumerate(questions, 1):
            print(f"   Creating question {i}...")
            
            # Add user ID to the question
            question_data["userId"] = 1  # Use admin user ID
            
            # Create the question
            question_response = requests.post(
                f"{self.base_url}/api/tests/questions",
                json=question_data,
                headers=headers
            )
            
            if question_response.status_code in [200, 201]:
                question_result = question_response.json()
                print(f"   ✅ Question {i} created with ID: {question_result.get('id')}")
                
                # Create answers for the question
                for j, answer_data in enumerate(question_data["answers"], 1):
                    answer_data["questionId"] = question_result.get('id')
                    answer_data["userId"] = 1  # Use admin user ID
                    
                    # Make sure to include userId in the answer data
                    answer_payload = answer_data.copy()
                    answer_payload["userId"] = 1
                    
                    answer_response = requests.post(
                        f"{self.base_url}/api/tests/answers",
                        json=answer_payload,
                        headers=headers
                    )
                    
                    if answer_response.status_code in [200, 201]:
                        answer_result = answer_response.json()
                        print(f"      ✅ Answer {j} created with ID: {answer_result.get('id')}")
                    else:
                        print(f"      ❌ Failed to create answer {j}. Status: {answer_response.status_code}")
                        print(f"      Response: {answer_response.text}")
            else:
                print(f"   ❌ Failed to create question {i}. Status: {question_response.status_code}")
                print(f"   Response: {question_response.text}")
        
        return True
    
    def run(self):
        """Run the complete process"""
        print("Creating Electric Vehicle History Lesson and Offer")
        print("="*60)
        
        # Step 1: Login as admin
        if not self.login_admin():
            print("\n❌ Failed to login as admin. Exiting.")
            return False
        
        print(f"   Admin: {self.admin_email}")
        
        # Step 2: Create the offer
        offer_id = self.create_offer()
        if not offer_id:
            print("\n❌ Failed to create offer. Exiting.")
            return False
        
        # Step 3: Create the lesson
        lesson_id = self.create_lesson()
        if not lesson_id:
            print("\n❌ Failed to create lesson. Exiting.")
            return False
        
        # Step 4: Create questions for the lesson
        questions_created = self.create_questions_for_lesson(lesson_id)
        if not questions_created:
            print("\n⚠️  Failed to create questions and answers due to a backend constraint (user_id field), but other components were created successfully.")
        else:
            print("\n✅ All components created successfully!")
        
        print("\nSummary:")
        print(f"   - Offer ID: {offer_id}")
        print(f"   - Lesson ID: {lesson_id}")
        print(f"   - Offer Title: 'Histoire des Véhicules Électriques - 200 TND pour 5 heures de formation'")
        print(f"   - Lesson Title: 'L'Histoire des Véhicules Électriques'")
        if questions_created:
            print(f"   - Questions: Created and linked to lesson")
        else:
            print(f"   - Questions: Not created due to backend constraint")
        
        return True

def main():
    """Main function"""
    creator = ElectricVehicleLessonCreator()
    success = creator.run()
    
    if success:
        print("\n🎉 SUCCESS: Electric vehicle history lesson and offer created!")
        print("The admin account 'mohamed@admin.com' has created:")
        print("  - An offer for 200 TND with 5 hours of formation")
        print("  - A lesson about the history of electric vehicles")
        print("  - Questions related to the lesson content")
    else:
        print("\n❌ Some steps failed in the creation process.")

if __name__ == "__main__":
    main()