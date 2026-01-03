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

    def check_if_offer_exists(self):
        """Check if an offer with the same title already exists"""
        if not self.admin_token:
            print("❌ No admin token available")
            return None

        headers = {
            'Authorization': f'Bearer {self.admin_token}'
        }

        try:
            response = requests.get(
                f"{self.base_url}/api/offers",
                headers=headers
            )

            if response.status_code == 200:
                offers = response.json()
                for offer in offers:
                    if offer.get('title') == "Histoire des Véhicules Électriques: 1832-2025":
                        print(f"⚠️ Offer already exists with ID: {offer.get('id')}")
                        return offer.get('id')
            return None
        except Exception as e:
            print(f"❌ Offer check error: {str(e)}")
            return None

    def create_offer(self):
        """Create an offer for electric vehicle course if it doesn't exist"""
        # First check if the offer already exists
        existing_offer_id = self.check_if_offer_exists()
        if existing_offer_id:
            print("\nSkipping offer creation - already exists")
            return existing_offer_id

        if not self.admin_token:
            print("❌ No admin token available")
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        # Keep description under 1000 characters
        offer_data = {
            "title": "Histoire des Véhicules Électriques: 1832-2025",
            "description": "Cours complet sur l'évolution des véhicules électriques. 5 modules académiques couvrant les origines, le déclin, la renaissance technologique, l'ère moderne et les perspectives futures.",
            "price": 200.00,
            "durationHours": 15,
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

    def create_module1_lesson(self):
        """Module 1: Origins and Golden Age (1832-1920)"""
        # Check if lesson already exists
        existing_id = self.check_if_lesson_exists("Module 1: Les Origines et l'Âge d'Or (1832-1920)")
        if existing_id:
            print("\nSkipping Module 1 creation - already exists")
            return existing_id

        if not self.admin_token:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        lesson_data = {
            "title": "Module 1: Les Origines et l'Âge d'Or (1832-1920)",
            "description": "Analyse approfondie des débuts technologiques, de l'innovation des batteries plomb-acide et de la domination du marché américain par les véhicules électriques avant 1912.",
            "videoUrl": "https://example.com/content/module1.mp4",
            "animation3dUrl": "https://example.com/content/module1.glb",
            "contentTitle": "Les Débuts Technologiques et l'Âge d'Or",
            "contentDescription": """**LES ORIGINES (1832-1880)**

Robert Anderson en Écosse crée le premier véhicule électrique en 1832-1839 avec cellules galvaniques non rechargeables. L'innovation clé vient avec la batterie au plomb rechargeable:
- Gaston Planté (1859): Première batterie rechargeable
- Camille Faure (1881): Batterie améliorée, pratique commerciale

**L'ÂGE D'OR (1890-1912)**

En 1900, le marché américain compte:
- 2100 véhicules à essence
- 1600 véhicules à vapeur
- 1575 véhicules électriques (38%)

Avantages clés des VE:
✓ Accélération en douceur sans changement de vitesse
✓ Démarrage sans manivelle (dangereux pour essence)
✓ Fiabilité supérieure aux moteurs à essence primitifs
✓ Silencieux et sans pollution
✓ Accessibles aux femmes (pas de force requise)

Fabricants majeurs:
• Baker Motor Vehicle Company (~160 000 véhicules)
• Detroit Electric Vehicle Company (leader du marché)
• Kriéger (France)
• Columbia Electric
• Riker Motor Vehicle Company

**LE TOURNANT CRITIQUE (1912)**

Charles Kettering invente le démarreur électrique pour automobiles à essence. Simultanément:
- Découverte de gisements pétroliers massifs (Texas)
- Prix de l'essence en chute libre
- Amélioration des routes longue distance
- Économies d'échelle favorisant l'essence (Ford)

Conclusion: Un exemple classique de disruption technologique où le meilleur produit cède aux facteurs économiques et infrastructurels.

**SOURCES**
Schiffer, M.B. (1994). "Taking Charge". Princeton University Press.
Mom, G.P.A. (2004). "The Electric Vehicle". Johns Hopkins University Press.""",
            "displayOrder": 1,
            "lessonOrder": 1,
            "isService": False
        }

        print("\nCreating Module 1: Origins and Golden Age...")
        response = requests.post(
            f"{self.base_url}/api/course-lessons",
            json=lesson_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Module 1 created - ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"❌ Module 1 failed. Status: {response.status_code}")
            return None

    def create_module2_lesson(self):
        """Module 2: The Decline (1920-1990)"""
        # Check if lesson already exists
        existing_id = self.check_if_lesson_exists("Module 2: Le Déclin et la Stagnation (1920-1990)")
        if existing_id:
            print("\nSkipping Module 2 creation - already exists")
            return existing_id

        if not self.admin_token:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        lesson_data = {
            "title": "Module 2: Le Déclin et la Stagnation (1920-1990)",
            "description": "Analyse des facteurs qui ont causé le déclin des véhicules électriques et leur quasi-disparition du marché grand public pendant 70 ans.",
            "videoUrl": "https://example.com/content/module2.mp4",
            "animation3dUrl": "https://example.com/content/module2.glb",
            "contentTitle": "Déclin Technologique et Stagnation",
            "contentDescription": """**CAUSES DU DÉCLIN (1912-1930)**

Facteurs technologiques:
• Démarreur électrique (Kettering, 1912) élimine l'avantage principal
• Moteurs à essence plus fiables et puissants
• Transmission automatique simplifiée
• Meilleure autonomie pour long trajet (150+ km)

Facteurs économiques:
• Prix essence divisé par 3 (découverte Texas 1901)
• Économies d'échelle pour l'essence (5x moins cher)
• Production de masse (Ford modèle T - $825 vs $1200 VE)
• Infrastructure pétrolière intégrée à la géopolitique

Facteurs sociétaux:
• Aspiration aux voyages longue distance
• Suburbanisation et mobilité rurale
• Marketing puissant des constructeurs essence
• Perception de l'automobile comme "liberté"

**PERSISTANCE LIMITÉE (1930-1990)**

Les VE survivent dans des niches:
• Véhicules de golf depuis 1897
• Transports urbains utilitaires
• Équipements pour mobilité réduite
• Recherche académique sporadique

Tentatives de renouveau échouées:
- 1966-1975: Crise pétrolière provoque intérêt temporaire
- Prototypes électriques construits (General Motors, Sebring-Vanguard)
- Technologie insuffisante (batteries trop lourdes, autonomie faible)
- Économies non viables sans subvention

**LA STAGNATION (1975-1990)**

L'industrie automobile se concentre sur:
• Réduction de la consommation essence
• Catalyseurs et contrôle pollution
• Injection électronique
• Transmission automatique perfectionnée

Les VE restent une curiosité de laboratoire, financés principalement par organismes gouvernementaux pour la recherche.

**SOURCES**
McShane, C. (1994). "Down the Asphalt Path". Columbia University Press.
Cowan, R.S. (1997). "A Social History of American Technology". Oxford University Press.""",
            "displayOrder": 2,
            "lessonOrder": 2,
            "isService": False
        }

        print("Creating Module 2: The Decline...")
        response = requests.post(
            f"{self.base_url}/api/course-lessons",
            json=lesson_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Module 2 created - ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"❌ Module 2 failed")
            return None

    def create_module3_lesson(self):
        """Module 3: Technological Renaissance (1990-2010)"""
        # Check if lesson already exists
        existing_id = self.check_if_lesson_exists("Module 3: La Renaissance Technologique (1990-2010)")
        if existing_id:
            print("\nSkipping Module 3 creation - already exists")
            return existing_id

        if not self.admin_token:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        lesson_data = {
            "title": "Module 3: La Renaissance Technologique (1990-2010)",
            "description": "Retour des VE grâce aux avancées technologiques en batteries lithium-ion et à la prise de conscience environnementale.",
            "videoUrl": "https://example.com/content/module3.mp4",
            "animation3dUrl": "https://example.com/content/module3.glb",
            "contentTitle": "Retour des Véhicules Électriques",
            "contentDescription": """**LES INNOVATIONS CLÉS (1990-2000)**

Batterie lithium-ion (Whittingham, 1976; commerciale 1991):
• Densité énergétique 3-5x supérieure au plomb
• Légère et recharging rapide
• Révolutionne l'électronique portable (ordinateurs, téléphones)

Impact catalyseur:
- 1996: General Motors EV1 (prototype amélioré)
- 1997: Toyota Prius (hybride) - première production massive
- 1999: Nissan Leaf en développement
- Mandats de Californie pour zéro-émission

**PRISE DE CONSCIENCE ENVIRONNEMENTALE (2000-2005)**

Facteurs de changement:
✓ Protocole de Kyoto (1997) - objectifs CO2
✓ Rapport du GIEC - consensus changement climatique
✓ Qualité de l'air urbain - crise sanitaire
✓ Consommation pétrolière insoutenable
✓ Coûts de la dépollution essence

Politiques gouvernementales:
• Incitations d'achat pour VE
• Restrictions de circulation pour essence
• Mandats de production
• Investissements en R&D

**L'ÉMERGENCE DE TESLA (2003-2010)**

Martin Eberhard et Marc Tarpenning fondent Tesla:
- 2008: Tesla Roadster lancé (0-100 en 3.9s)
- Révolutionne la perception des VE = performance
- Démontre viabilité commerciale
- Attire investissements majeurs (Daimler, Toyota)

**PROGRESSION VERS LA MASSE (2005-2010)**

- 2005: Prius devient voiture la plus vendue au Japon
- 2010: Nissan Leaf (180 km autonomie)
- 2010: Chevrolet Volt (hybride rechargeable)
- Infrastructure de recharge commence
- Coût batteries baisse de 50%

Conclusion: Convergence de trois facteurs = Renaissance:
1. Technologies enfin matures
2. Conscience environnementale
3. Volonté politique et investissements

**SOURCES**
Gartman, D. (1994). "Auto Opium". Routledge.
Mom, G.P.A. (2004). "The Electric Vehicle". Johns Hopkins University Press.""",
            "displayOrder": 3,
            "lessonOrder": 3,
            "isService": False
        }

        print("Creating Module 3: Technological Renaissance...")
        response = requests.post(
            f"{self.base_url}/api/course-lessons",
            json=lesson_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Module 3 created - ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"❌ Module 3 failed")
            return None

    def create_module4_lesson(self):
        """Module 4: Modern Era (2010-2025)"""
        # Check if lesson already exists
        existing_id = self.check_if_lesson_exists("Module 4: L'Ère Moderne et la Transformation (2010-2025)")
        if existing_id:
            print("\nSkipping Module 4 creation - already exists")
            return existing_id

        if not self.admin_token:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        lesson_data = {
            "title": "Module 4: L'Ère Moderne et la Transformation (2010-2025)",
            "description": "Analyse de l'adoption massive, de la concurrence accrue et de la transformation complète du secteur automobile.",
            "videoUrl": "https://example.com/content/module4.mp4",
            "animation3dUrl": "https://example.com/content/module4.glb",
            "contentTitle": "Transformation Complète du Secteur",
            "contentDescription": """**L'EXPLOSION DE LA CROISSANCE (2010-2020)**

Croissance des ventes:
• 2010: 17 000 VE vendus mondialement
• 2020: 3,2 millions de VE vendus
• CAGR: 47% (croissance annuelle composée)

Acteurs majeurs:
- Tesla: Part de marché dominante
- Volkswagen: Plan électrification massive
- BYD (Chine): Leader en volume
- Hyundai/Kia: Entrée aggressive
- Toyota: Extension hybride
- Nissan, Renault, BMW, Audi

**AVANCÉES TECHNOLOGIQUES (2015-2025)**

Batteries:
• Autonomie: 150 km → 700+ km
• Coût: $1000/kWh → $100/kWh
• Densité énergétique: x2 amélioration
• Chimie: Lithium, Sodium-ion, État solide en R&D

Performances:
• Accélération: 0-100 en 2.6s (Tesla Model S Plaid)
• Vitesse de charge: 30 min pour 80%
• Infrastructure: 500 000+ bornes publiques

Infrastructure et politiques:
✓ Mandats européens: 55% réduction CO2 (2030)
✓ UK, France: Interdiction essence en 2030-2035
✓ Chine: 50% VE en 2035
✓ USA: Inflation Reduction Act - subventions massives

**DÉFIS PERSISTANTS (2020-2025)**

Économiques:
• Prix initial encore 20-30% supérieur
• Inégalités d'accès (pays riches vs pauvres)
• Fiabilité des batteries long terme incertaine

Environnementaux:
• Mine de lithium = impact écologique
• Recyclage des batteries encore inefficace
• Électricité doit provenir de sources renouvelables

Géopolitiques:
• Dépendance à la Chine pour batteries (80%)
• Rare earth elements pour moteurs
• Tension commerciale USA-Chine

**TENDANCES ACTUELLES (2023-2025)**

• Tesla perd part de marché face à compétition
• Électrification des poids-lourds commence
• Aviation électrique en développement
• Hybride rechargeable remporte succès temporaire
• Problèmes de chaîne d'approvisionnement

Conclusion: Les VE ne sont plus une alternative, mais l'avenir inévitable. La question n'est plus "SI" mais "QUAND" et "COMMENT".

**SOURCES**
Données IEA World EV Outlook 2024
Reuters/Bloomberg analyses secteur automobile 2020-2025
McKinsey & Company - Future of Mobility reports""",
            "displayOrder": 4,
            "lessonOrder": 4,
            "isService": False
        }

        print("Creating Module 4: Modern Era...")
        response = requests.post(
            f"{self.base_url}/api/course-lessons",
            json=lesson_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Module 4 created - ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"❌ Module 4 failed")
            return None

    def create_module5_lesson(self):
        """Module 5: Future Perspectives"""
        # Check if lesson already exists
        existing_id = self.check_if_lesson_exists("Module 5: Perspectives Futures et Impact Géopolitique")
        if existing_id:
            print("\nSkipping Module 5 creation - already exists")
            return existing_id

        if not self.admin_token:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        lesson_data = {
            "title": "Module 5: Perspectives Futures et Impact Géopolitique",
            "description": "Vision prospective des véhicules électriques et leur impact sur l'économie mondiale, l'environnement et la géopolitique de l'énergie.",
            "videoUrl": "https://example.com/content/module5.mp4",
            "animation3dUrl": "https://example.com/content/module5.glb",
            "contentTitle": "L'Avenir des Véhicules Électriques",
            "contentDescription": """**SCÉNARIOS TECHNOLOGIQUES (2025-2050)**

Batteries de nouvelle génération:
• État solide: Densité x2, coût -30%, charge 15 min
• Sodium-ion: Moins cher, plus abondant que lithium
• Lithium-air: Densité énergétique extrême
• Supercapaciteurs: Compléments pour charge rapide

Impact: Coût VE = Essence en 2030-2035 mondialement

Infrastructure décentralisée:
• Recharge à domicile (80% des trajets quotidiens)
• Recharge ultra-rapide longue distance
• Vehicle-to-grid (voitures = batteries mobiles)
• Smart grid intégrant énergies renouvelables

**IMPACTS ENVIRONNEMENTAUX (2025-2050)**

Émissions:
• Réduction CO2 transport: 50% (2030), 80% (2050)
• Amélioration qualité air urbain dramatique
• Réduction dépendance pétrolière: 60% (2050)

Minéralité et recyclage:
• 90% batteries recyclables (2030)
• Extraction lithium durable développée
• Économie circulaire des matériaux clés

Paradoxe environnemental:
- VE électriques seulement si électricité verte
- Nécessite transition énergies renouvelables massifs
- Lien direct: Transport-Énergie-Climat

**TRANSFORMATIONS GÉOPOLITIQUES (2025-2050)**

Fin de l'ère pétrolière:
• OPEP perd pouvoir géopolitique
• Pétrole reste utilisé: chimie, plastique
• Mais rente énergétique disparaît

Nouvelles dépendances:
• Lithium: Chili, Argentine, Australie, Chine
• Cobalt: Congo (80% mondial) = risques de conflit
• Terres rares: Chine contrôle 70%
• Politique "minéralière" remplace politique pétrolière

Réalignement géopolitique:
✓ Pays producteurs de lithium gagnants
✓ Pays sans ressources = consommateurs
✓ Électricité = enjeu central (hydroélectricité, nucléaire)
✓ Chaîne d'approvisionnement batterie critique

**DISRUPTIONS SECTORIELLES (2025-2050)**

Industrie automobile:
• Consolidation: 50% des constructeurs disparaissent
• Émergence de nouveaux acteurs (Tesla model)
• Électronique > mécanique dans la valeur
• Délocalisation vers où est l'énergie

Transport et mobilité:
• Voitures autonomes électriques (2040-2050?)
• Partage de véhicules (réduction parc auto)
• Logistique dernière mile révolutionnée
• Poids-lourds électriques dominent (2045)

Services énergétiques:
• Modèle "batterie-comme-service"
• Échange rapide batteries vs recharge
• Optimisation consommation par IA

**SCÉNARIOS CONTRASTÉS (2050)**

Scénario optimiste:
✓ 95% VE en 2050
✓ Électricité 100% renouvelable
✓ Recyclage circulaire complet
✓ Réduction CO2 transport: 90%
Probabilité: 25%

Scénario probable:
✓ 80% VE en 2050
✓ Électricité 60-70% renouvelable
✓ Défis recyclage partiels résolus
✓ Réduction CO2 transport: 70-75%
Probabilité: 50%

Scénario pessimiste:
✓ 60% VE en 2050
✓ Électricité 40% renouvelable
✓ Batteries à problèmes non résolus
✓ Réduction CO2 transport: 50%
Probabilité: 25%

**IMPLICATIONS POUR LE TUNISIEN**

Tunisie contexte:
• Peu de ressources minérales (pas lithium)
• Électricité mixte (gaz + 30% renouvelable)
• Infrastructure recharge: en retard

Opportunités:
✓ Énergie solaire abondante
✓ Potentiel hub régional batteries
✓ Emplois secteur électricité croissants
✓ Transport urbain électrifié viable

Défis:
✗ Technologie importée
✗ Coût initial VE prohibitif
✗ Infrastructure recharge insuffisante
✗ Formation technique nécessaire

**CONCLUSION**

Les véhicules électriques ne représentent plus une alternative technologique, mais une transformation systémique de la mobilité, de l'énergie et de la géopolitique mondiale. Comprendre cette évolution historique permet de mieux anticiper les disruptions futures.

**SOURCES**
IEA (2024) Global EV Outlook
Blumberg, J. et al. (2023) "The Energy Transition"
BP Energy Outlook 2024
IPCC Special Report on Climate Change 2023""",
            "displayOrder": 5,
            "lessonOrder": 5,
            "isService": False
        }

        print("Creating Module 5: Future Perspectives...")
        response = requests.post(
            f"{self.base_url}/api/course-lessons",
            json=lesson_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Module 5 created - ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"❌ Module 5 failed")
            return None

    def check_if_test_exists(self, title):
        """Check if a test with the same title already exists"""
        if not self.admin_token:
            print("❌ No admin token available")
            return None

        headers = {
            'Authorization': f'Bearer {self.admin_token}'
        }

        try:
            response = requests.get(
                f"{self.base_url}/api/tests/course-tests",
                headers=headers
            )

            if response.status_code == 200:
                tests = response.json()
                for test in tests:
                    if test.get('title') == title:
                        print(f"⚠️ Test already exists with ID: {test.get('id')}")
                        return test.get('id')
            return None
        except Exception as e:
            print(f"❌ Test check error: {str(e)}")
            return None

    def create_module1_questions(self, lesson_id):
        """Create questions for Module 1"""
        # Check if test already exists
        existing_id = self.check_if_test_exists(f"Test Module 1: Histoire des VE - Origins")
        if existing_id:
            print("\nSkipping Module 1 questions creation - already exists")
            return existing_id

        if not self.admin_token or not lesson_id:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        test_data = {
            "title": f"Test Module 1: Histoire des VE - Origins",
            "description": "Questions sur les origines des véhicules électriques (1832-1920)",
            "lessonId": lesson_id,
            "durationMinutes": 30,
            "maxAttempts": 3,
            "passingScore": 70
        }

        print("\nCreating Module 1 test...")
        response = requests.post(
            f"{self.base_url}/api/tests/course-tests",
            json=test_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            test_id = result.get('id')
            print(f"✅ Module 1 test created - ID: {test_id}")
            
            # Create questions for this test
            questions = [
                {
                    "question": "Quel est l'année de création du premier véhicule électrique par Robert Anderson?",
                    "options": ["1832", "1859", "1881", "1900"],
                    "correctAnswer": "1832",
                    "explanation": "Robert Anderson a créé le premier véhicule électrique en Écosse entre 1832 et 1839."
                },
                {
                    "question": "Quel type de batterie a été inventé par Gaston Planté en 1859?",
                    "options": ["Batterie lithium-ion", "Batterie plomb-acide rechargeable", "Batterie sodium-ion", "Batterie à état solide"],
                    "correctAnswer": "Batterie plomb-acide rechargeable",
                    "explanation": "Gaston Planté a inventé la première batterie rechargeable au plomb en 1859."
                },
                {
                    "question": "En 1900, quel pourcentage du marché américain était constitué de véhicules électriques?",
                    "options": ["18%", "25%", "38%", "50%"],
                    "correctAnswer": "38%",
                    "explanation": "En 1900, environ 38% du marché américain des véhicules était constitué de véhicules électriques."
                }
            ]
            
            for i, q_data in enumerate(questions):
                self.create_question(test_id, q_data)
            
            return test_id
        else:
            print(f"❌ Module 1 test creation failed. Status: {response.status_code}")
            return None

    def create_module2_questions(self, lesson_id):
        """Create questions for Module 2"""
        # Check if test already exists
        existing_id = self.check_if_test_exists(f"Test Module 2: Histoire des VE - Decline")
        if existing_id:
            print("\nSkipping Module 2 questions creation - already exists")
            return existing_id

        if not self.admin_token or not lesson_id:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        test_data = {
            "title": f"Test Module 2: Histoire des VE - Decline",
            "description": "Questions sur le déclin des véhicules électriques (1920-1990)",
            "lessonId": lesson_id,
            "durationMinutes": 30,
            "maxAttempts": 3,
            "passingScore": 70
        }

        print("\nCreating Module 2 test...")
        response = requests.post(
            f"{self.base_url}/api/tests/course-tests",
            json=test_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            test_id = result.get('id')
            print(f"✅ Module 2 test created - ID: {test_id}")
            
            # Create questions for this test
            questions = [
                {
                    "question": "Quel inventeur a créé le démarreur électrique pour les voitures à essence en 1912?",
                    "options": ["Robert Anderson", "Charles Kettering", "Gaston Planté", "Camille Faure"],
                    "correctAnswer": "Charles Kettering",
                    "explanation": "Charles Kettering a inventé le démarreur électrique pour automobiles à essence en 1912."
                },
                {
                    "question": "Quel facteur a contribué à la chute du prix de l'essence après 1912?",
                    "options": ["Fin de la Première Guerre mondiale", "Découverte de gisements pétroliers massifs", "Création de l'OPEP", "Invention du moteur diesel"],
                    "correctAnswer": "Découverte de gisements pétroliers massifs",
                    "explanation": "La découverte de gisements pétroliers massifs, notamment au Texas, a fait chuter le prix de l'essence."
                },
                {
                    "question": "Dans quelle niche les véhicules électriques ont-ils persisté pendant leur déclin?",
                    "options": ["Voitures de sport", "Véhicules militaires", "Véhicules de golf et utilitaires", "Avions légers"],
                    "correctAnswer": "Véhicules de golf et utilitaires",
                    "explanation": "Les VE ont persisté dans des niches comme les véhicules de golf et les transports urbains utilitaires."
                }
            ]
            
            for i, q_data in enumerate(questions):
                self.create_question(test_id, q_data)
            
            return test_id
        else:
            print(f"❌ Module 2 test creation failed")
            return None

    def create_module3_questions(self, lesson_id):
        """Create questions for Module 3"""
        # Check if test already exists
        existing_id = self.check_if_test_exists(f"Test Module 3: Histoire des VE - Renaissance")
        if existing_id:
            print("\nSkipping Module 3 questions creation - already exists")
            return existing_id

        if not self.admin_token or not lesson_id:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        test_data = {
            "title": f"Test Module 3: Histoire des VE - Renaissance",
            "description": "Questions sur la renaissance technologique des VE (1990-2010)",
            "lessonId": lesson_id,
            "durationMinutes": 30,
            "maxAttempts": 3,
            "passingScore": 70
        }

        print("\nCreating Module 3 test...")
        response = requests.post(
            f"{self.base_url}/api/tests/course-tests",
            json=test_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            test_id = result.get('id')
            print(f"✅ Module 3 test created - ID: {test_id}")
            
            # Create questions for this test
            questions = [
                {
                    "question": "Quelle innovation technologique a permis la renaissance des VE dans les années 1990?",
                    "options": ["Moteur à combustion amélioré", "Batterie lithium-ion", "Turbo diesel", "Injection électronique"],
                    "correctAnswer": "Batterie lithium-ion",
                    "explanation": "La batterie lithium-ion a permis une densité énergétique 3-5x supérieure au plomb."
                },
                {
                    "question": "Quel événement environnemental a contribué à la prise de conscience pour les VE?",
                    "options": ["Crise de l'eau", "Protocole de Kyoto en 1997", "Problèmes de bruit", "Crise des terres rares"],
                    "correctAnswer": "Protocole de Kyoto en 1997",
                    "explanation": "Le Protocole de Kyoto de 1997 a marqué une prise de conscience environnementale."
                },
                {
                    "question": "Quelle entreprise a fondé Tesla en 2003?",
                    "options": ["Elon Musk", "Martin Eberhard et Marc Tarpenning", "Jeff Bezos", "Bill Gates"],
                    "correctAnswer": "Martin Eberhard et Marc Tarpenning",
                    "explanation": "Martin Eberhard et Marc Tarpenning ont fondé Tesla en 2003."
                }
            ]
            
            for i, q_data in enumerate(questions):
                self.create_question(test_id, q_data)
            
            return test_id
        else:
            print(f"❌ Module 3 test creation failed")
            return None

    def create_module4_questions(self, lesson_id):
        """Create questions for Module 4"""
        # Check if test already exists
        existing_id = self.check_if_test_exists(f"Test Module 4: Histoire des VE - Modern Era")
        if existing_id:
            print("\nSkipping Module 4 questions creation - already exists")
            return existing_id

        if not self.admin_token or not lesson_id:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        test_data = {
            "title": f"Test Module 4: Histoire des VE - Modern Era",
            "description": "Questions sur l'ère moderne des VE (2010-2025)",
            "lessonId": lesson_id,
            "durationMinutes": 30,
            "maxAttempts": 3,
            "passingScore": 70
        }

        print("\nCreating Module 4 test...")
        response = requests.post(
            f"{self.base_url}/api/tests/course-tests",
            json=test_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            test_id = result.get('id')
            print(f"✅ Module 4 test created - ID: {test_id}")
            
            # Create questions for this test
            questions = [
                {
                    "question": "Quel est le pourcentage de réduction des émissions CO2 du transport visé d'ici 2050?",
                    "options": ["30%", "50%", "70-75%", "90%"],
                    "correctAnswer": "70-75%",
                    "explanation": "Le scénario probable prévoit une réduction de 70-75% des émissions CO2 du transport d'ici 2050."
                },
                {
                    "question": "Quel pays est devenu leader mondial en volume de VE vendus?",
                    "options": ["États-Unis", "Allemagne", "Japon", "Chine"],
                    "correctAnswer": "Chine",
                    "explanation": "BYD en Chine est devenu leader mondial en volume de VE vendus."
                },
                {
                    "question": "Quelle est l'autonomie maximale atteinte par les VE modernes?",
                    "options": ["300+ km", "500+ km", "700+ km", "1000+ km"],
                    "correctAnswer": "700+ km",
                    "explanation": "Les VE modernes peuvent atteindre une autonomie de 700+ km."
                }
            ]
            
            for i, q_data in enumerate(questions):
                self.create_question(test_id, q_data)
            
            return test_id
        else:
            print(f"❌ Module 4 test creation failed")
            return None

    def create_module5_questions(self, lesson_id):
        """Create questions for Module 5"""
        # Check if test already exists
        existing_id = self.check_if_test_exists(f"Test Module 5: Histoire des VE - Future")
        if existing_id:
            print("\nSkipping Module 5 questions creation - already exists")
            return existing_id

        if not self.admin_token or not lesson_id:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        test_data = {
            "title": f"Test Module 5: Histoire des VE - Future",
            "description": "Questions sur les perspectives futures des VE",
            "lessonId": lesson_id,
            "durationMinutes": 30,
            "maxAttempts": 3,
            "passingScore": 70
        }

        print("\nCreating Module 5 test...")
        response = requests.post(
            f"{self.base_url}/api/tests/course-tests",
            json=test_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            test_id = result.get('id')
            print(f"✅ Module 5 test created - ID: {test_id}")
            
            # Create questions for this test
            questions = [
                {
                    "question": "Quel type de batterie est prévu pour doubler la densité énergétique dans le futur?",
                    "options": ["Batterie sodium-ion", "Batterie à état solide", "Batterie lithium-air", "Supercapaciteur"],
                    "correctAnswer": "Batterie à état solide",
                    "explanation": "Les batteries à état solide devraient doubler la densité énergétique dans le futur."
                },
                {
                    "question": "Quel pays est producteur majeur de lithium selon les scénarios géopolitiques?",
                    "options": ["Arabie Saoudite", "Chili", "Australie", "Chili, Argentine et Australie"],
                    "correctAnswer": "Chili, Argentine et Australie",
                    "explanation": "Chili, Argentine et Australie sont les principaux producteurs de lithium selon les scénarios."
                },
                {
                    "question": "Quel pourcentage de VE est prévu en 2050 selon le scénario probable?",
                    "options": ["60%", "80%", "95%", "100%"],
                    "correctAnswer": "80%",
                    "explanation": "Le scénario probable prévoit 80% de VE en 2050."
                }
            ]
            
            for i, q_data in enumerate(questions):
                self.create_question(test_id, q_data)
            
            return test_id
        else:
            print(f"❌ Module 5 test creation failed")
            return None

    def create_question(self, test_id, question_data):
        """Create a question for a specific test"""
        if not self.admin_token or not test_id:
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }

        # Map fields to match Spring Boot API expectations (camelCase)
        question_payload = {
            "questionText": question_data["question"],
            "options": question_data["options"],
            "correctAnswer": question_data["correctAnswer"],
            "explanation": question_data.get("explanation", ""),
            "courseTestId": test_id,
            "points": 5  # Add default points value
        }

        print(f"Creating question: {question_data['question'][:50]}...")
        response = requests.post(
            f"{self.base_url}/api/tests/questions",
            json=question_payload,
            headers=headers
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"  ✅ Question created - ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"  ❌ Question creation failed. Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return None

    def run(self):
        """Run the complete process"""
        print("="*70)
        print("COGNITIEX COMPLETE COURSE CREATION")
        print("Electric Vehicle History: 5 Academic Modules")
        print("="*70)

        # Step 1: Login
        if not self.login_admin():
            print("\n❌ Failed to login. Exiting.")
            return False

        print(f"   Admin: {self.admin_email}")
        print(f"   Backend: {self.base_url}")

        # Step 2: Create offer
        offer_id = self.create_offer()
        if not offer_id:
            return False

        # Step 3: Create all 5 modules
        print("\n" + "-"*70)
        print("CREATING 5 ACADEMIC MODULES")
        print("-"*70)

        modules = [
            self.create_module1_lesson(),
            self.create_module2_lesson(),
            self.create_module3_lesson(),
            self.create_module4_lesson(),
            self.create_module5_lesson()
        ]

        successful_modules = [m for m in modules if m is not None]
        
        # Step 4: Create questions for each successful module
        print("\n" + "-"*70)
        print("CREATING QUESTIONS FOR EACH MODULE")
        print("-"*70)
        
        successful_tests = 0
        if len(successful_modules) >= 1 and successful_modules[0]:
            test1 = self.create_module1_questions(successful_modules[0])
            if test1:
                successful_tests += 1
        
        if len(successful_modules) >= 2 and successful_modules[1]:
            test2 = self.create_module2_questions(successful_modules[1])
            if test2:
                successful_tests += 1
        
        if len(successful_modules) >= 3 and successful_modules[2]:
            test3 = self.create_module3_questions(successful_modules[2])
            if test3:
                successful_tests += 1
        
        if len(successful_modules) >= 4 and successful_modules[3]:
            test4 = self.create_module4_questions(successful_modules[3])
            if test4:
                successful_tests += 1
        
        if len(successful_modules) >= 5 and successful_modules[4]:
            test5 = self.create_module5_questions(successful_modules[4])
            if test5:
                successful_tests += 1
        
        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        print(f"✅ Offer Created: ID {offer_id}")
        print(f"   Title: Histoire des Véhicules Électriques: 1832-2025")
        print(f"   Price: 200 TND | Duration: 15 heures")
        print(f"\n✅ Modules Created: {len(successful_modules)}/5")
        print(f"   • Module 1: Les Origines et l'Âge d'Or (1832-1920)")
        print(f"   • Module 2: Le Déclin et la Stagnation (1920-1990)")
        print(f"   • Module 3: La Renaissance Technologique (1990-2010)")
        print(f"   • Module 4: L'Ère Moderne et la Transformation (2010-2025)")
        print(f"   • Module 5: Perspectives Futures et Impact Géopolitique")
        print(f"\n✅ Tests Created: {successful_tests}/5")
        print(f"   • Module 1: Test on origins and early development")
        print(f"   • Module 2: Test on decline period")
        print(f"   • Module 3: Test on technological renaissance")
        print(f"   • Module 4: Test on modern era")
        print(f"   • Module 5: Test on future perspectives")
        print("="*70)

        return True


def main():
    creator = ElectricVehicleLessonCreator()
    success = creator.run()

    if success:
        print("\n🎉 SUCCESS: Complete course created on CognitiEx!")
    else:
        print("\n❌ Course creation encountered issues.")


# ====================================
# AJOUT DES LECONS COGNITIEX
# ====================================

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

**PRINCIPES DE BASE DE LA PERSUASION ET DES BIAIS COGNITIFS (APPROCHE HARVARD)**

1. **Norme de réciprocité** : Comme l'explique Robert Cialdini, nous avons une compulsion innée à répondre aux comportements des autres de la même manière. Dans l'apprentissage, cela peut influencer la manière dont les apprenants réagissent aux stimuli éducatifs.

2. **Effet d'ancrage** : Démontré dans les recherches de la Harvard Law School, notre tendance à nous appuyer excessivement sur la première information rencontrée influence nos décisions futures. Cela affecte l'apprentissage dès les premières expériences avec un concept.

3. **Aversion à la perte** : D'après les recherches d'Amos Tversky et Daniel Kahneman (prix Nobel), les gens sont plus motivés à éviter les pertes qu'à accumuler des gains. Cela peut être utilisé dans les stratégies d'apprentissage.

4. **Scarcité perçue** : Comme documenté par Cialdini, les opportunités semblent plus précieuses lorsqu'elles sont moins disponibles. Cela peut motiver l'engagement dans l'apprentissage.

5. **Biais de confirmation** : Les apprenants cherchent des informations qui confirment leurs croyances existantes, ce qui peut limiter l'acquisition de nouvelles connaissances.

**1. Exemple technique : Qoder, Cursor et l'illusion de robustesse**

Les environnements de développement assistés par IA tels que Qoder ou Cursor produisent du code rapidement, souvent correct en apparence.

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
            "description": "Formalisation mathématique de l'accumulation d'incompréhensions dans les systèmes cognitifs humains.",
            "videoUrl": "https://example.com/content/cognitiex_modele.mp4",
            "animation3dUrl": "https://example.com/content/cognitiex_modele.glb",
            "contentTitle": "Modèle Cognitif Cognitiex - Formalisation Mathématique",
            "contentDescription": """**1. Hypothèses de base - APPLICATION DES PRINCIPES HARVARD SUR LES BIAIS COGNITIFS**

Nous modélisons l'apprentissage comme un système dynamique discret évoluant dans le temps, intégrant les découvertes de la Harvard Law School sur les biais cognitifs et les stratégies de persuasion.

**APPLICATION DES BIAIS COGNITIFS DE HARVARD AU MODÈLE MATHÉMATIQUE**

- **Effet d'ancrage (Harvard Negotiation Project)** : L'état initial d'un concept xᵢ(0) influence fortement toutes les évaluations futures, créant un "point d'ancrage" qui affecte la compréhension subséquente.

- **Biais de confirmation** : Lorsque l'apprenant rencontre des informations contraires à ses connaissances antérieures, il y a une résistance ("résistance cognitive") qui peut être modélisée comme une force proportionnelle à l'écart avec les croyances antérieures.

- **Aversion à la perte (Tversky & Kahneman - Harvard)** : La perte perçue de compétence ou de statut affecte plus fortement l'état cognitif que le gain équivalent de connaissance.

- **Norme de réciprocité (Cialdini - Harvard)** : Lorsqu'un système éducatif fournit de la valeur, l'apprenant ressent une obligation psychologique de répondre positivement, ce qui peut être intégré dans le modèle comme un facteur motivationnel.

- **Scarcité perçue** : La disponibilité limitée d'informations ou de ressources peut augmenter la motivation à apprendre, influençant les poids cognitifs wᵢ.

Hypothèses principales :
- L'apprentissage est non linéaire.
- Les erreurs cognitives sont locales, mais leurs effets sont globaux.
- La performance observable est un retard par rapport à l'état réel du système cognitif.
- L'échec est un effet émergent, non un événement instantané.
- Les biais cognitifs influencent les transitions d'état et les poids des concepts.

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
                    "questionText": "Expliquez le concept central du 'Manifeste Cognitiex' concernant l'accumulation de micro-erreurs dans les systèmes cognitifs et logiciels, et comment les principes de persuasion de Harvard (norme de réciprocité, effet d'ancrage) s'appliquent à l'apprentissage.",
                    "questionType": "OPEN_ENDED",
                    "points": 10,
                    "expectedAnswerType": "LONG_TEXT",
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Décrivez comment les biais cognitifs identifiés par la Harvard Law School influencent l'apprentissage humain selon le Manifeste Cognitiex.",
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
                    "questionText": "La 'norme de réciprocité' est un principe de persuasion identifié par la Harvard Law School.",
                    "questionType": "MCQ",
                    "points": 5,
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Quelle analogie est faite entre les environnements de développement IA et l'apprentissage humain ?",
                    "questionType": "MCQ",
                    "points": 7,
                    "lessonId": lesson_id
                },
                {
                    "questionText": "L'effet d'ancrage est un biais cognitif étudié par la Harvard Law School.",
                    "questionType": "MCQ",
                    "points": 5,
                    "lessonId": lesson_id
                }
            ]
        else:  # Modèle Cognitif Cognitiex
            questions = [
                {
                    "questionText": "Formulez mathématiquement le modèle de charge cognitive effective dans le 'Modèle Cognitif Cognitiex' et expliquez comment les principes des biais cognitifs de Harvard (effet d'ancrage, aversion à la perte) sont intégrés dans le modèle.",
                    "questionType": "OPEN_ENDED",
                    "points": 12,
                    "expectedAnswerType": "MATHEMATICAL_FORMULA",
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Expliquez comment l'effet d'ancrage de Harvard influence le modèle mathématique de l'apprentissage dans le Modèle Cognitif Cognitiex.",
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
                    "questionText": "Le modèle Cognitif Cognitiex intègre les principes des biais cognitifs de Harvard comme l'effet d'ancrage.",
                    "questionType": "MCQ",
                    "points": 5,
                    "lessonId": lesson_id
                },
                {
                    "questionText": "Quel est le seuil critique θ dans le modèle de charge cognitive ?",
                    "questionType": "MCQ",
                    "points": 8,
                    "lessonId": lesson_id
                },
                {
                    "questionText": "L'aversion à la perte est un principe de la théorie des perspectives de Tversky et Kahneman (Harvard).",
                    "questionType": "MCQ",
                    "points": 5,
                    "lessonId": lesson_id
                }
            ]

        print(f"\nCreating questions for lesson '{lesson_title}' (ID: {lesson_id})...")
        
        created_count = 0
        for i, question in enumerate(questions, 1):
            try:
                # Remove lessonId from the payload as it might not be needed in the request body
                # Map fields to match Spring Boot API expectations (camelCase)
                question_payload = {
                    "questionText": question["questionText"],
                    "questionType": question["questionType"],
                    "points": question["points"],
                    "courseLessonId": lesson_id
                }
                
                # Add expectedAnswerType only for open-ended questions
                if "expectedAnswerType" in question:
                    question_payload["expectedAnswerType"] = question["expectedAnswerType"]

                response = requests.post(
                    f"{self.base_url}/api/tests/questions",
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
            # Map fields to match Spring Boot API expectations (camelCase)
            answer_payload = {
                "answerText": answer["answerText"],
                "isCorrect": answer["isCorrect"],
                "questionId": question_id,
                "answerOrder": answer["answerOrder"]
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/tests/answers",
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


def main_with_both_courses():
    print("Choose which course to create:")
    print("1. Electric Vehicle Course")
    print("2. Cognitiex Course") 
    print("3. Both")
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    success_ev = True
    success_cognitiex = True
    
    if choice == "1" or choice == "3":
        print("\nCreating Electric Vehicle Course...")
        ev_creator = ElectricVehicleLessonCreator()
        success_ev = ev_creator.run()
    
    if choice == "2" or choice == "3":
        print("\nCreating Cognitiex Course...")
        cognitiex_creator = CognitiexLessonCreator()
        success_cognitiex = cognitiex_creator.run()
    
    if choice == "1":
        if success_ev:
            print("\n🎉 SUCCESS: Electric Vehicle course created on CognitiEx!")
        else:
            print("\n❌ Electric Vehicle course creation encountered issues.")
    elif choice == "2":
        if success_cognitiex:
            print("\n🎉 SUCCESS: Cognitiex course created on CognitiEx!")
        else:
            print("\n❌ Cognitiex course creation encountered issues.")
    elif choice == "3":
        if success_ev and success_cognitiex:
            print("\n🎉 SUCCESS: Both courses created on CognitiEx!")
        else:
            print("\n❌ Some course creation encountered issues.")
    else:
        print("Invalid choice. Please run again and enter 1, 2, or 3.")


if __name__ == "__main__":
    main_with_both_courses()