#!/usr/bin/env python3
"""
Script to create Cognitiex lessons with the manifest and cognitive model content
This script connects to the Spring Boot backend using the admin account and creates:
1. A lesson about the Cognitiex Manifest
2. A lesson about the Cognitive Model with mathematical formalization
3. Questions related to each lesson
"""

import requests
import json
import time


class CognitiexLessonCreator:
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

    def check_if_lesson_exists(self, title):
        """Check if a lesson with the same title already exists"""
        if not self.admin_token:
            print("❌ No admin token available")
            return None

        headers = {
            'Authorization': f'Bearer {self.admin_token}'
        }

        try:
            response = requests.get(
                f"{self.base_url}/api/course-lessons",
                headers=headers
            )

            if response.status_code == 200:
                lessons = response.json()
                for lesson in lessons:
                    if lesson.get('title') == title:
                        print(f"⚠️ Lesson already exists with ID: {lesson.get('id')}")
                        return lesson.get('id')
            return None
        except Exception as e:
            print(f"❌ Lesson check error: {str(e)}")
            return None

    def create_manifeste_lesson(self):
        """Create the 'Manifeste Cognitiex' lesson"""
        # Check if lesson already exists
        existing_id = self.check_if_lesson_exists("Manifeste Cognitiex")
        if existing_id:
            print("\nSkipping 'Manifeste Cognitiex' creation - already exists")
            return existing_id

        if not self.admin_token:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        lesson_data = {
            "title": "Manifeste Cognitiex",
            "description": "Une approche systémique et scientifique de l'apprentissage humain",
            "videoUrl": "https://example.com/content/cognitiex-manifeste.mp4",
            "animation3dUrl": "https://example.com/content/cognitiex-manifeste.glb",
            "contentTitle": "Manifeste Cognitiex - Approche Systémique de l'Apprentissage",
            "contentDescription": """**RÉSUMÉ EXÉCUTIF**

Cognitiex repose sur une hypothèse issue des sciences cognitives, de la psychologie expérimentale et de l'ingénierie logicielle moderne :
les défaillances majeures émergent rarement d'une erreur unique, mais d'une accumulation de micro-erreurs non détectées au niveau du processus.

Ce principe est aujourd'hui observable aussi bien dans les systèmes logiciels assistés par IA que dans les systèmes cognitifs humains.

**1. Exemple technique : Qoder, Cursor et l'illusion de robustesse**

Les environnements de développement assistés par IA tels que Qoder ou Cursor produisent du code rapidement, souvent correct en apparence.

Dans de nombreux cas :
- le code compile,
- les tests unitaires passent,
- les fonctionnalités isolées semblent opérationnelles.

Pourtant, lors de l'intégration ou du déploiement :
- le système devient instable,
- les dépendances entrent en conflit,
- les erreurs se multiplient de manière non locale,
- le débogage devient coûteux, voire impossible.

La cause n'est pas une "grande erreur", mais :
- une série de micro-incohérences logiques,
- des hypothèses implicites non alignées,
- des choix locaux valides mais globalement incompatibles.

Ces erreurs sont :
- trop petites pour être détectées individuellement,
- souvent invisibles même pour un expert lors d'une revue ponctuelle,
- mais cumulativement destructrices pour le système global.

**2. Transposition cognitive : le même mécanisme dans l'apprentissage**

L'apprentissage humain présente une dynamique strictement comparable.

Un élève peut :
- comprendre partiellement une notion,
- compenser temporairement une lacune,
- réussir des exercices locaux,
- obtenir des résultats acceptables à court terme.

Cependant, chaque incompréhension non corrigée introduit une incohérence conceptuelle dans le système cognitif.

À mesure que les connaissances s'empilent :
- les contradictions augmentent,
- la charge cognitive explose,
- la cohérence interne se dégrade.

Comme dans un projet généré avec Qoder ou Cursor,
le système semble fonctionner... jusqu'au moment où il doit généraliser, transférer ou raisonner à un niveau supérieur.

C'est à ce stade que l'échec devient visible.

**3. La perception de difficulté comme effet émergent**

Les recherches en sciences cognitives montrent que la difficulté perçue n'est pas proportionnelle à la difficulté objective.

Elle est un effet émergent résultant de :
- la somme des incompréhensions antérieures,
- la fragmentation des représentations mentales,
- l'instabilité du modèle interne de l'apprenant.

L'élève n'échoue pas parce que le contenu est trop complexe,
mais parce que son système cognitif n'est plus cohérent, exactement comme un codebase instable.

**4. Limites de l'évaluation classique**

Les évaluations traditionnelles jouent le rôle des tests unitaires :
- elles vérifient des compétences locales,
- elles ne mesurent pas la cohérence globale,
- elles détectent rarement les erreurs structurelles.

Un élève peut donc "réussir" tout en accumulant des défauts invisibles,
de la même manière qu'un projet IA-assisted peut sembler fonctionnel avant l'intégration finale.

**5. Hypothèse centrale de Cognitiex**

Cognitiex part de l'hypothèse suivante :

Les incompréhensions cognitives génèrent des signaux faibles observables avant l'échec explicite, de la même manière que les incohérences logicielles génèrent des symptômes avant le crash du système.

Ces signaux peuvent être :
- comportementaux,
- interactionnels,
- temporels,
- multimodaux.

L'enjeu n'est pas de noter, mais de diagnostiquer.

**6. Rôle de l'intelligence artificielle**

Dans Cognitiex, l'IA joue le rôle d'un outil d'analyse systémique, comparable à un analyseur statique et dynamique avancé en ingénierie logicielle.

Elle permet :
- d'identifier des patterns invisibles à l'observation humaine directe,
- de détecter des instabilités cognitives locales,
- d'intervenir avant que l'échec global ne se manifeste.

L'IA ne remplace pas l'apprenant,
elle améliore la qualité du système d'apprentissage.

**7. Implications**

Un apprenant dont les incompréhensions sont détectées et corrigées précocement :
- conserve une architecture cognitive cohérente,
- développe une confiance basée sur la compréhension réelle,
- maintient une capacité élevée de transfert et d'abstraction.

Comme en ingénierie logicielle,
la robustesse ne dépend pas de la vitesse de production, mais de la stabilité du système.

**Conclusion**

Les outils comme Qoder et Cursor révèlent une vérité fondamentale :
la performance apparente masque souvent une fragilité structurelle.

Cognitiex applique ce constat à l'apprentissage humain,
en traitant la compréhension comme une architecture à maintenir cohérente.

Lorsque les micro-erreurs sont détectées tôt,
l'échec cesse d'être une fatalité et devient un événement évitable.""",
            "displayOrder": 1,
            "lessonOrder": 1,
            "isService": False
        }

        print("\nCreating 'Manifeste Cognitiex' lesson...")
        try:
            response = requests.post(
                f"{self.base_url}/api/course-lessons",
                json=lesson_data,
                headers=headers
            )

            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ 'Manifeste Cognitiex' lesson created successfully!")
                print(f"   Lesson ID: {result.get('id')}")
                print(f"   Title: {result.get('title')}")
                return result.get('id')
            else:
                print(f"❌ Failed to create 'Manifeste Cognitiex' lesson. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 'Manifeste Cognitiex' lesson creation error: {str(e)}")
            return None

    def create_modele_cognitif_lesson(self):
        """Create the 'Modèle Cognitif Cognitiex' lesson"""
        # Check if lesson already exists
        existing_id = self.check_if_lesson_exists("Modèle Cognitif Cognitiex")
        if existing_id:
            print("\nSkipping 'Modèle Cognitif Cognitiex' creation - already exists")
            return existing_id

        if not self.admin_token:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        lesson_data = {
            "title": "Modèle Cognitif Cognitiex",
            "description": "Formalisation mathématique de l'accumulation d'incompréhensions",
            "videoUrl": "https://example.com/content/cognitiex-modele.mp4",
            "animation3dUrl": "https://example.com/content/cognitiex-modele.glb",
            "contentTitle": "Modèle Cognitif Cognitiex - Formalisation Mathématique",
            "contentDescription": """**1. Hypothèses de base**

Nous modélisons l'apprentissage comme un système dynamique discret évoluant dans le temps.

Hypothèses principales :
- L'apprentissage est non linéaire.
- Les erreurs cognitives sont locales, mais leurs effets sont globaux.
- La performance observable est un retard par rapport à l'état réel du système cognitif.
- L'échec est un effet émergent, non un événement instantané.

**2. Représentation formelle du système cognitif**

**2.1 Graphe de connaissances**

On définit un graphe orienté :

G = (V, E)

V = {c₁, c₂, ..., cₙ} : concepts
E ⊂ V × V : dépendances conceptuelles

Chaque concept cᵢ possède un état de compréhension :

xᵢ(t) ∈ [0,1]

xᵢ(t) = 1 : compréhension stable
xᵢ(t) = 0 : incompréhension totale

**3. Micro-incompréhensions et bruit cognitif**

Lors de l'apprentissage d'un concept cᵢ, une perturbation locale peut apparaître :

εᵢ(t) ∼ N(0, σᵢ²)

Cette perturbation représente :
- une approximation erronée,
- une analogie mal formée,
- une dépendance mal comprise.

L'état réel devient :

x̃ᵢ(t) = xᵢ(t) - εᵢ(t)

Individuellement, εᵢ(t) est faible et souvent indétectable.

**4. Accumulation et propagation (analogie Qoder / Cursor)**

La compréhension d'un concept dépend de ses prérequis :

xᵢ(t+1) = f(x̃ᵢ(t), ∏ⱼ∈Parents(i) x̃ⱼ(t))

Ainsi :
- une erreur locale se propage,
- les erreurs deviennent corrélées,
- la cohérence globale diminue.

C'est exactement le phénomène observé dans les codebases générées par Qoder ou Cursor :
- chaque fonction est localement valide,
- l'intégration globale devient instable.

**5. Charge cognitive et instabilité systémique**

On définit la charge cognitive effective :

CL(t) = Σᵢ₌₁ⁿ (1 - xᵢ(t)) ⋅ wᵢ

où wᵢ est le poids cognitif du concept.

Il existe un seuil critique θ tel que :

CL(t) > θ ⇒ instabilité cognitive

Au-delà de ce seuil :
- baisse de performance soudaine,
- évitement,
- perte de motivation,
- impression subjective de difficulté excessive.

**6. Dissociation performance / état réel**

La performance observable P(t) est définie comme :

P(t) = g(x(t)) + η(t)

avec :
η(t) : stratégies compensatoires (mémorisation, imitation, chance)

Ainsi :
P(t) peut rester élevée alors que x(t) se dégrade

C'est l'illusion de robustesse, exactement comme :
- tests unitaires qui passent,
- déploiement impossible.

**7. Signaux faibles observables**

On définit un vecteur de signaux multimodaux :

S(t) = [s₁(t), s₂(t), ..., sₖ(t)]

Ces signaux sont fonctions de l'état latent :

S(t) = h(x(t)) + ξ(t)

Ils incluent :
- latence de réponse,
- variabilité comportementale,
- incohérences interactionnelles.

L'objectif de Cognitiex est d'estimer x(t) à partir de S(t).

**8. Rôle de l'IA : estimation de l'état latent**

Le problème est un problème classique d'estimation d'état :

x̂(t) = argmax P(x(t) | S(0:t))

Méthodes possibles :
- modèles bayésiens dynamiques,
- filtres de Kalman non linéaires,
- réseaux neuronaux temporels,
- modèles hybrides graphe + deep learning.

L'IA agit comme :
- un analyseur statique et dynamique du système cognitif.

**9. Intervention précoce (maintenance cognitive)**

Une intervention est déclenchée si :

d/dt CL(t) > α

ou si une chute locale est détectée :

xᵢ(t) < β

L'intervention vise :
- un concept précis,
- une dépendance spécifique,
- sans surcharge globale.

**10. Résultat théorique**

Sous détection et correction précoces :

lim t→∞ CL(t) < θ

Le système reste :
- stable,
- cohérent,
- performant.

**Conclusion formelle**

L'échec cognitif n'est pas une défaillance ponctuelle mais une transition de phase d'un système instable.

Cognitiex :
- modélise l'apprentissage comme un système dynamique,
- détecte les instabilités avant le point critique,
- applique une maintenance préventive cognitive.

Exactement comme on corrige une codebase générée par Qoder ou Cursor avant le déploiement final.""",
            "displayOrder": 2,
            "lessonOrder": 2,
            "isService": False
        }

        print("\nCreating 'Modèle Cognitif Cognitiex' lesson...")
        try:
            response = requests.post(
                f"{self.base_url}/api/course-lessons",
                json=lesson_data,
                headers=headers
            )

            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ 'Modèle Cognitif Cognitiex' lesson created successfully!")
                print(f"   Lesson ID: {result.get('id')}")
                print(f"   Title: {result.get('title')}")
                return result.get('id')
            else:
                print(f"❌ Failed to create 'Modèle Cognitif Cognitiex' lesson. Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 'Modèle Cognitif Cognitiex' lesson creation error: {str(e)}")
            return None

    def create_manifeste_questions(self, lesson_id):
        """Create questions for the Manifeste lesson"""
        if not self.admin_token or not lesson_id:
            print("❌ No admin token or lesson ID available")
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        print(f"\nCreating questions for 'Manifeste Cognitiex' lesson (ID: {lesson_id})...")

        # Create questions for the manifest lesson
        questions = [
            {
                "question": "Expliquez le concept central du 'Manifeste Cognitiex' concernant l'accumulation de micro-erreurs dans les systèmes cognitifs et logiciels.",
                "questionType": "OPEN_ENDED",
                "points": 10,
                "lessonId": lesson_id
            },
            {
                "question": "Quel est le rôle de l'IA dans le système Cognitiex selon le manifeste ?",
                "questionType": "OPEN_ENDED",
                "points": 8,
                "lessonId": lesson_id
            },
            {
                "question": "Selon le manifeste, la difficulté perçue est proportionnelle à la difficulté objective.",
                "options": ["Vrai", "Faux"],
                "correctAnswer": "Faux",
                "explanation": "La difficulté perçue n'est pas proportionnelle à la difficulté objective, elle est un effet émergent résultant de la somme des incompréhensions antérieures.",
                "lessonId": lesson_id
            },
            {
                "question": "Quelle analogie est faite entre les environnements de développement IA et l'apprentissage humain ?",
                "options": ["Aucune analogie", "Les deux systèmes accumulent des micro-erreurs", "Ils sont tous deux linéaires", "Ils fonctionnent de manière identique"],
                "correctAnswer": "Les deux systèmes accumulent des micro-erreurs",
                "explanation": "L'analogie est que les deux systèmes présentent des dynamiques comparables où les micro-erreurs s'accumulent.",
                "lessonId": lesson_id
            }
        ]

        created_questions = 0
        for i, q_data in enumerate(questions):
            if q_data.get("questionType") == "OPEN_ENDED":
                # Create an open-ended question
                question_payload = {
                    "questionText": q_data["question"],
                    "questionType": q_data["questionType"],
                    "points": q_data["points"],
                    "lessonId": lesson_id,
                    "expectedAnswerType": "LONG_TEXT"
                }
            else:
                # Create an MCQ question
                question_payload = {
                    "questionText": q_data["question"],
                    "questionType": "MCQ",
                    "points": 5,  # Default points for MCQ
                    "lessonId": lesson_id
                }

            print(f"Creating question: {q_data['question'][:50]}...")
            response = requests.post(
                f"{self.base_url}/api/test-questions",
                json=question_payload,
                headers=headers
            )

            if response.status_code in [200, 201]:
                result = response.json()
                print(f"  ✅ Question created - ID: {result.get('id')}")
                created_questions += 1
                
                # If it's an MCQ, create answer options
                if "options" in q_data:
                    self.create_mcq_answers(result.get('id'), q_data)
            else:
                print(f"  ❌ Question creation failed. Status: {response.status_code}")
                print(f"  Response: {response.text}")

        print(f"✅ Created {created_questions}/{len(questions)} questions for 'Manifeste Cognitiex'")
        return created_questions == len(questions)

    def create_modele_questions(self, lesson_id):
        """Create questions for the Cognitive Model lesson"""
        if not self.admin_token or not lesson_id:
            print("❌ No admin token or lesson ID available")
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        print(f"\nCreating questions for 'Modèle Cognitif Cognitiex' lesson (ID: {lesson_id})...")

        # Create questions for the cognitive model lesson
        questions = [
            {
                "question": "Formulez mathématiquement le modèle de charge cognitive effective dans le 'Modèle Cognitif Cognitiex'.",
                "questionType": "OPEN_ENDED",
                "points": 12,
                "lessonId": lesson_id
            },
            {
                "question": "Expliquez le concept de 'graphe de connaissances' et son utilisation dans le modèle cognitif.",
                "questionType": "OPEN_ENDED",
                "points": 10,
                "lessonId": lesson_id
            },
            {
                "question": "Dans le modèle, xᵢ(t) = 1 signifie une incompréhension totale.",
                "options": ["Vrai", "Faux"],
                "correctAnswer": "Faux",
                "explanation": "xᵢ(t) = 1 signifie une compréhension stable, xᵢ(t) = 0 signifie une incompréhension totale.",
                "lessonId": lesson_id
            },
            {
                "question": "Quelle est l'équation de base pour l'estimation d'état dans le modèle cognitif ?",
                "options": ["x̂(t) = argmax P(x(t) | S(0:t))", "x(t) = f(x(t-1))", "CL(t) = Σ(1-xᵢ(t))", "S(t) = h(x(t)) + ξ(t)"],
                "correctAnswer": "x̂(t) = argmax P(x(t) | S(0:t))",
                "explanation": "L'équation de base pour l'estimation d'état est x̂(t) = argmax P(x(t) | S(0:t)).",
                "lessonId": lesson_id
            }
        ]

        created_questions = 0
        for i, q_data in enumerate(questions):
            if q_data.get("questionType") == "OPEN_ENDED":
                # Create an open-ended question
                question_payload = {
                    "questionText": q_data["question"],
                    "questionType": q_data["questionType"],
                    "points": q_data["points"],
                    "lessonId": lesson_id,
                    "expectedAnswerType": "MATHEMATICAL_FORMULA" if "mathématiquement" in q_data["question"] else "DESCRIPTIVE_TEXT"
                }
            else:
                # Create an MCQ question
                question_payload = {
                    "questionText": q_data["question"],
                    "questionType": "MCQ",
                    "points": 5,  # Default points for MCQ
                    "lessonId": lesson_id
                }

            print(f"Creating question: {q_data['question'][:50]}...")
            response = requests.post(
                f"{self.base_url}/api/test-questions",
                json=question_payload,
                headers=headers
            )

            if response.status_code in [200, 201]:
                result = response.json()
                print(f"  ✅ Question created - ID: {result.get('id')}")
                created_questions += 1
                
                # If it's an MCQ, create answer options
                if "options" in q_data:
                    self.create_mcq_answers(result.get('id'), q_data)
            else:
                print(f"  ❌ Question creation failed. Status: {response.status_code}")
                print(f"  Response: {response.text}")

        print(f"✅ Created {created_questions}/{len(questions)} questions for 'Modèle Cognitif Cognitiex'")
        return created_questions == len(questions)

    def create_mcq_answers(self, question_id, question_data):
        """Create answer options for MCQ questions"""
        if not self.admin_token or not question_id:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        # Create answers for the question
        for i, option in enumerate(question_data["options"]):
            answer_payload = {
                "answerText": option,
                "isCorrect": option == question_data["correctAnswer"],
                "questionId": question_id,
                "answerOrder": i + 1
            }

            response = requests.post(
                f"{self.base_url}/api/test-answers",
                json=answer_payload,
                headers=headers
            )

            if response.status_code in [200, 201]:
                result = response.json()
                print(f"    ✅ Answer created: {option} (Correct: {answer_payload['isCorrect']})")
            else:
                print(f"    ❌ Answer creation failed. Status: {response.status_code}")

    def run(self):
        """Run the complete process"""
        print("="*70)
        print("COGNITIEX COMPLETE LESSON CREATION")
        print("Manifeste Cognitiex & Modèle Cognitif Cognitiex")
        print("="*70)

        # Step 1: Login
        if not self.login_admin():
            print("\n❌ Failed to login. Exiting.")
            return False

        print(f"   Admin: {self.admin_email}")
        print(f"   Backend: {self.base_url}")

        # Step 2: Create lessons
        print("\n" + "-"*70)
        print("CREATING COGNITIEX LESSONS")
        print("-"*70)

        manifeste_id = self.create_manifeste_lesson()
        modele_id = self.create_modele_cognitif_lesson()

        successful_lessons = []
        if manifeste_id:
            successful_lessons.append(manifeste_id)
        if modele_id:
            successful_lessons.append(modele_id)

        # Step 3: Create questions for each successful lesson
        print("\n" + "-"*70)
        print("CREATING QUESTIONS FOR EACH LESSON")
        print("-"*70)

        successful_questions = 0
        if manifeste_id:
            if self.create_manifeste_questions(manifeste_id):
                successful_questions += 1

        if modele_id:
            if self.create_modele_questions(modele_id):
                successful_questions += 1

        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        print(f"✅ Lessons Created: {len(successful_lessons)}/2")
        if manifeste_id:
            print(f"   • Manifeste Cognitiex: ID {manifeste_id}")
        if modele_id:
            print(f"   • Modèle Cognitif Cognitiex: ID {modele_id}")
        print(f"\n✅ Question Sets Created: {successful_questions}/2")
        if manifeste_id:
            print(f"   • Manifeste Cognitiex: Questions created")
        if modele_id:
            print(f"   • Modèle Cognitif Cognitiex: Questions created")
        print("="*70)

        return len(successful_lessons) == 2


def main():
    creator = CognitiexLessonCreator()
    success = creator.run()

    if success:
        print("\n🎉 SUCCESS: Complete Cognitiex course created on CognitiEx!")
    else:
        print("\n❌ Course creation encountered issues.")


if __name__ == "__main__":
    main()