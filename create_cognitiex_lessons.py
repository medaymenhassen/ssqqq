#!/usr/bin/env python3
"""
Script to create Cognitiex lessons with SQL-based questions
This script logs in with admin credentials and creates:
1. 'Manifeste Cognitiex' lesson
2. 'Modèle Cognitif Cognitiex' lesson
3. SQL-based questions for each lesson (both open-ended and multiple choice)
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
            "description": "Une approche systémique et scientifique de l'apprentissage humain basée sur les sciences cognitives, la psychologie expérimentale et l'ingénierie logicielle moderne.",
            "videoUrl": "https://example.com/content/cognitiex_manifeste.mp4",
            "animation3dUrl": "https://example.com/content/cognitiex_manifeste.glb",
            "contentTitle": "Manifeste Cognitiex - Approche Systémique de l'Apprentissage",
            "contentDescription": """**RÉSUMÉ EXÉCUTIF**

Cognitiex repose sur une hypothèse issue des sciences cognitives, de la psychologie expérimentale et de l'ingénierie logicielle moderne :
les défaillances majeures émergent rarement d'une erreur unique, mais d'une accumulation de micro-erreurs non détectées au niveau du processus.

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
l'échec cesse d'être une fatalité et devient un événement évitable."""[:2000]  # Truncate to fit database limit,
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
            "description": "Formalisation mathématique de l'accumulation d'incompréhensions dans les systèmes cognitifs humains.",
            "videoUrl": "https://example.com/content/cognitiex_modele.mp4",
            "animation3dUrl": "https://example.com/content/cognitiex_modele.glb",
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

    def create_questions_for_lesson(self, lesson_id, lesson_title):
        """Create SQL-based questions for a specific lesson"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        # Define questions based on the lesson
        if lesson_title == "Manifeste Cognitiex":
            questions = [
                {
                    "questionText": "Expliquez le concept central du 'Manifeste Cognitiex' concernant l'accumulation de micro-erreurs dans les systèmes cognitifs et logiciels.",
                    "questionType": "OPEN_ENDED",
                    "points": 10,
                    "expectedAnswerType": "LONG_TEXT",
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Quel est le rôle de l'IA dans le système Cognitiex selon le manifeste ?",
                    "questionType": "OPEN_ENDED",
                    "points": 8,
                    "expectedAnswerType": "MEDIUM_TEXT",
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Selon le manifeste, la difficulté perçue est proportionnelle à la difficulté objective.",
                    "questionType": "MCQ",
                    "points": 5,
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Quelle analogie est faite entre les environnements de développement IA et l'apprentissage humain ?",
                    "questionType": "MCQ",
                    "points": 7,
                    "lessonId": lesson_id
                }
            ]
        else:  # Modèle Cognitif Cognitiex
            questions = [
                {
                    "questionText": "Formulez mathématiquement le modèle de charge cognitive effective dans le 'Modèle Cognitif Cognitiex'.",
                    "questionType": "OPEN_ENDED",
                    "points": 12,
                    "expectedAnswerType": "MATHEMATICAL_FORMULA",
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Expliquez le concept de 'graphe de connaissances' et son utilisation dans le modèle cognitif.",
                    "questionType": "OPEN_ENDED",
                    "points": 10,
                    "expectedAnswerType": "DESCRIPTIVE_TEXT",
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Dans le modèle, xᵢ(t) = 1 signifie une incompréhension totale.",
                    "questionType": "MCQ",
                    "points": 5,
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Quel est le seuil critique θ dans le modèle de charge cognitive ?",
                    "questionType": "MCQ",
                    "points": 8,
                    "lessonId": lesson_id
                }
            ]

        print(f"\nCreating questions for lesson '{lesson_title}' (ID: {lesson_id})...")
        
        created_count = 0
        for i, question in enumerate(questions, 1):
            try:
                # Remove lessonId from the payload as it might not be needed in the request body
                question_payload = {
                    "questionText": question["questionText"],
                    "questionType": question["questionType"],
                    "points": question["points"],
                    "lessonId": lesson_id
                }
                
                # Add expectedAnswerType only for open-ended questions
                if "expectedAnswerType" in question:
                    question_payload["expectedAnswerType"] = question["expectedAnswerType"]

                response = requests.post(
                    f"{self.base_url}/api/test-questions",
                    json=question_payload,
                    headers=headers
                )

                if response.status_code in [200, 201]:
                    result = response.json()
                    print(f"   ✅ Question {i} created: {result.get('id')}")
                    created_count += 1
                    
                    # If it's an MCQ, create answer options
                    if question["questionType"] == "MCQ":
                        self.create_mcq_answers(result.get('id'), question["questionText"])
                else:
                    print(f"   ❌ Failed to create question {i}. Status: {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"   ❌ Error creating question {i}: {str(e)}")
        
        print(f"✅ Created {created_count}/{len(questions)} questions for '{lesson_title}'")
        return created_count == len(questions)

    def create_mcq_answers(self, question_id, question_text):
        """Create answer options for MCQ questions"""
        if not self.admin_token:
            return False

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        # Determine correct answers based on the question
        if "n'est pas proportionnelle" in question_text or "signifie une incompréhension totale" in question_text:
            # This is a false statement, so correct answer is "False"
            answers = [
                {"answerText": "Vrai", "isCorrect": False, "answerOrder": 1},
                {"answerText": "Faux", "isCorrect": True, "answerOrder": 2}
            ]
        else:
            # Default answers for other questions
            answers = [
                {"answerText": "Vrai", "isCorrect": True, "answerOrder": 1},
                {"answerText": "Faux", "isCorrect": False, "answerOrder": 2},
                {"answerText": "Partiellement", "isCorrect": False, "answerOrder": 3},
                {"answerText": "Ne sais pas", "isCorrect": False, "answerOrder": 4}
            ]

        for answer in answers:
            answer_payload = {
                "answerText": answer["answerText"],
                "isCorrect": answer["isCorrect"],
                "questionId": question_id,
                "answerOrder": answer["answerOrder"]
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/test-answers",
                    json=answer_payload,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    print(f"      Created answer: {result.get('id')}")
                else:
                    print(f"      Failed to create answer. Status: {response.status_code}")
            except Exception as e:
                print(f"      Error creating answer: {str(e)}")

    def run(self):
        """Run the complete lesson creation process"""
        print("="*60)
        print("COGNITIEX LESSON CREATION SCRIPT")
        print("="*60)
        
        # Login
        if not self.login_admin():
            print("❌ Cannot proceed without admin login")
            return False
        
        print()
        
        # Create first lesson
        manifeste_id = self.create_manifeste_lesson()
        if manifeste_id:
            print(f"✅ 'Manifeste Cognitiex' lesson created with ID: {manifeste_id}")
            # Create questions for first lesson
            self.create_questions_for_lesson(manifeste_id, "Manifeste Cognitiex")
        else:
            print("❌ Failed to create 'Manifeste Cognitiex' lesson")
        
        print()
        
        # Create second lesson
        modele_id = self.create_modele_cognitif_lesson()
        if modele_id:
            print(f"✅ 'Modèle Cognitif Cognitiex' lesson created with ID: {modele_id}")
            # Create questions for second lesson
            self.create_questions_for_lesson(modele_id, "Modèle Cognitif Cognitiex")
        else:
            print("❌ Failed to create 'Modèle Cognitif Cognitiex' lesson")
        
        print()
        print("="*60)
        if manifeste_id and modele_id:
            print("🎉 ALL LESSONS CREATED SUCCESSFULLY!")
            print(f"   • Manifeste Cognitiex: ID {manifeste_id}")
            print(f"   • Modèle Cognitif Cognitiex: ID {modele_id}")
        else:
            print("⚠️  SOME LESSONS WERE NOT CREATED SUCCESSFULLY")
        print("="*60)
        
        return bool(manifeste_id and modele_id)


def main():
    creator = CognitiexLessonCreator()
    success = creator.run()
    
    if success:
        print("\n✅ Script completed successfully!")
    else:
        print("\n❌ Script completed with errors!")
        exit(1)


if __name__ == "__main__":
    main()