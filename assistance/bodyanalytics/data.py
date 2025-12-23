
import os
import time
import random
import logging
import requests
from pathlib import Path
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import quote, urljoin
import traceback

# ============= CONFIGURATION LOGGING =============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ============= CONFIGURATION =============
MORPHOLOGIES = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

BASE_DIR = Path("morphologie_dataset_complete")
API_DATA_DIR = BASE_DIR / "api_images"
WIKI_DATA_DIR = BASE_DIR / "wikipedia_data"
DRAMA_DATA_DIR = BASE_DIR / "drama_data"
TEXT_DATA_DIR = BASE_DIR / "text_data"
STATS_DIR = BASE_DIR / "stats"

# Créer répertoires
for dir_path in [API_DATA_DIR, WIKI_DATA_DIR, DRAMA_DATA_DIR, TEXT_DATA_DIR, STATS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Headers génériques pour éviter les blocages
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Referer': 'https://www.google.com/'
}

# Config API images
PEXELS_API_KEY = "vHFDT4fGZ8rvVfggojWZN8OvFiZPAdCmpvBUL1KoIgNgO25NZ1k85eaM"
UNSPLASH_KEY = "Jjepyi3trI91JMe1P_xVWdjRaaR7lzHQTCobT3vth_0"

# Queries par morphologie (texte aléatoire pour chaque recherche)
MORPHO_QUERIES = {
    "XS": [
        "petite slender woman", "delicate thin female", "graceful lean girl",
        "petit frame petite", "skinny athletic build", "fragile appearance",
        "slender body type", "lightweight female", "dainty person",
        "tiny woman figure", "ultra thin girl", "lean physique female"
    ],
    "S": [
        "slim athletic woman", "toned slender female", "fit lean girl",
        "small athletic build", "slim fit physique", "toned woman body",
        "slender athletic figure", "lean muscular female", "active slim woman",
        "fit slim body", "athletic slender woman", "toned lean physique"
    ],
    "M": [
        "healthy average woman", "balanced build female", "natural proportioned girl",
        "average body weight woman", "normal healthy female", "proportioned body type",
        "average size woman", "normal weight female", "standard body build",
        "medium frame woman", "healthy weight female", "balanced body proportions"
    ],
    "L": [
        "curvy confident woman", "full figured female", "shapely attractive girl",
        "curvy body type woman", "fuller figure female", "athletic muscular woman",
        "strong build woman", "robust feminine figure", "well-built female",
        "sturdy woman body", "powerful feminine physique", "voluptuous woman"
    ],
    "XL": [
        "plus size confident woman", "voluptuous beautiful female", "full bodied girl",
        "plus size woman fashion", "curvy size woman", "larger frame female",
        "full figured beauty", "plus-size body positive", "big beautiful woman",
        "larger size woman", "generous curves female", "plus size physique"
    ],
    "XXL": [
        "generously proportioned woman", "abundantly curved female", "beautifully full girl",
        "very plus size woman", "super curvy female", "extra large woman body",
        "maximum curves woman", "abundantly beautiful female", "generous size woman",
        "large feminine figure", "full body woman", "curvy comfortable woman"
    ],
    "XXXL": [
        "exceptionally full woman", "magnificently proportioned female", "abundantly beautiful girl",
        "extreme plus size woman", "super size woman", "maximum size female",
        "extra generous curves", "big bold woman", "very large woman body",
        "maximum feminine curves", "abundant woman figure", "largest woman build"
    ]
}

WIKI_TOPICS_RANDOM = [
    "Body_type", "Human_morphology", "Somatotype",
    "Physical_fitness", "Anatomy", "Muscle_group",
    "Anthropometry", "Body_mass_index", "Human_body",
    "Endomorph", "Mesomorph", "Ectomorph",
    "Body_shape", "Human_development", "Obesity",
    "Physical_attractiveness", "Sexual_dimorphism",
    "Skeletal_system", "Muscular_system", "Skin"
]

# ============= CLASSE 1: WIKIPEDIA SCRAPER =============

class WikipediaScraper:
    """Scrape données complètes depuis Wikipedia"""
    
    @staticmethod
    def get_random_topics(count: int = 10) -> List[str]:
        """Retourne topics aléatoires"""
        import random
        return random.sample(WIKI_TOPICS_RANDOM, min(count, len(WIKI_TOPICS_RANDOM)))
    
    @staticmethod
    def fetch_article(topic: str, max_retries: int = 3) -> Tuple[bool, Dict]:
        """
        Récupère un article Wikipedia
        Retourne: (success, data)
        """
        for attempt in range(max_retries):
            try:
                # API Wikipedia
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(topic)}"
                
                response = requests.get(url, headers=HEADERS, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'extract' in data:
                        logger.info(f"  ✅ Wikipedia: {data.get('title', topic)}")
                        return True, {
                            'title': data.get('title', topic),
                            'content': data.get('extract', ''),
                            'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                            'image': data.get('thumbnail', {}).get('source', ''),
                            'source': 'wikipedia',
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        logger.warning(f"  ⚠️ Wikipedia '{topic}': pas de contenu")
                        return False, {}
                
                elif response.status_code == 404:
                    logger.warning(f"  ❌ Wikipedia '{topic}': non trouvé")
                    return False, {}
                
                else:
                    logger.warning(f"  ⚠️ Wikipedia status {response.status_code} pour '{topic}'")
                    time.sleep(2)
                    continue
            
            except requests.Timeout:
                logger.warning(f"  ⏱️  Timeout Wikipedia {topic} (tentative {attempt+1}/{max_retries})")
                time.sleep(random.uniform(3, 8))
                continue
            
            except requests.RequestException as e:
                logger.warning(f"  ⚠️ Erreur réseau Wikipedia '{topic}': {e}")
                time.sleep(random.uniform(2, 5))
                continue
            
            except Exception as e:
                logger.error(f"  ❌ Erreur Wikipedia '{topic}': {e}")
                continue
        
        return False, {}
    
    @staticmethod
    def collect_all_wikipedia(target_count: int = 100) -> Dict:
        """Collecte TOUS les articles Wikipedia"""
        logger.info("=" * 70)
        logger.info("📚 WIKIPEDIA SCRAPING - COLLECTE MASSIVE")
        logger.info("=" * 70)
        
        articles = {}
        collected = 0
        
        # Boucle infinie jusqu'au target
        while collected < target_count:
            topics = WikipediaScraper.get_random_topics(count=5)
            
            for topic in topics:
                if collected >= target_count:
                    break
                
                success, data = WikipediaScraper.fetch_article(topic)
                
                if success:
                    articles[data['title']] = data
                    collected += 1
                    logger.info(f"   [{collected}/{target_count}] Articles collectés")
                
                # Respecter rate limit
                time.sleep(random.uniform(1, 3))
        
        # Sauvegarder
        wiki_file = TEXT_DATA_DIR / "wikipedia_articles.json"
        with open(wiki_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ Wikipedia terminé: {collected} articles")
        logger.info(f"   Fichier: {wiki_file}\n")
        
        return articles


# ============= CLASSE 2: VOIRDRAMA SCRAPER =============

class VoirDramaScraper:
    """Scrape vidéos et informations depuis voirdrama.org"""
    
    SITE_URL = "https://voirdrama.org"
    
    @staticmethod
    def search_dramas(query: str, max_retries: int = 3) -> List[Dict]:
        """
        Recherche dramas sur voirdrama
        Retourne: list[{title, url, image, description}]
        """
        for attempt in range(max_retries):
            try:
                search_url = f"{VoirDramaScraper.SITE_URL}/?s={quote(query)}"
                
                logger.info(f"  🔍 Recherche: {query}")
                
                response = requests.get(search_url, headers=HEADERS, timeout=20)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    logger.warning(f"  ⚠️ Status {response.status_code}")
                    time.sleep(random.uniform(3, 8))
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                results = []
                
                # Scraper les résultats (adapter sélecteurs selon structure réelle)
                items = soup.find_all('article', limit=5)
                
                if not items:
                    items = soup.find_all('div', class_='drama-item', limit=5)
                
                if not items:
                    items = soup.find_all('div', class_='post', limit=5)
                
                for item in items:
                    try:
                        title_elem = item.find('h2') or item.find('a')
                        title = title_elem.get_text(strip=True) if title_elem else "Unknown"
                        
                        link_elem = item.find('a')
                        link = link_elem.get('href', '') if link_elem else ''
                        
                        img_elem = item.find('img')
                        image = img_elem.get('src', '') if img_elem else ''
                        
                        description = item.find('p')
                        description = description.get_text(strip=True)[:200] if description else ''
                        
                        if link:
                            results.append({
                                'title': title,
                                'url': urljoin(VoirDramaScraper.SITE_URL, link),
                                'image': image,
                                'description': description,
                                'source': 'voirdrama'
                            })
                    
                    except Exception as e:
                        logger.debug(f"    Erreur parsing item: {e}")
                        continue
                
                if results:
                    logger.info(f"  ✅ {len(results)} dramas trouvés")
                    return results
                else:
                    logger.warning(f"  ⚠️ Aucun result pour '{query}'")
                    return []
            
            except requests.Timeout:
                logger.warning(f"  ⏱️  Timeout voirdrama (tentative {attempt+1}/{max_retries})")
                time.sleep(random.uniform(5, 15))
                continue
            
            except requests.RequestException as e:
                logger.warning(f"  ⚠️ Erreur réseau voirdrama: {e}")
                time.sleep(random.uniform(3, 8))
                continue
            
            except Exception as e:
                logger.error(f"  ❌ Erreur parsing voirdrama: {e}")
                continue
        
        return []
    
    @staticmethod
    def collect_all_dramas(target_count: int = 100) -> Dict:
        """Collecte TOUS les dramas"""
        logger.info("=" * 70)
        logger.info("🎬 VOIRDRAMA SCRAPING - COLLECTE MASSIVE")
        logger.info("=" * 70)
        
        all_dramas = {}
        collected = 0
        
        # Utiliser toutes les queries par morphologie
        all_queries = []
        for morpho, queries in MORPHO_QUERIES.items():
            all_queries.extend(queries)
        
        import random
        random.shuffle(all_queries)
        
        for query in all_queries:
            if collected >= target_count:
                break
            
            dramas = VoirDramaScraper.search_dramas(query)
            
            for drama in dramas:
                if collected >= target_count:
                    break
                
                key = drama['title']
                all_dramas[key] = drama
                collected += 1
                logger.info(f"   [{collected}/{target_count}] Dramas collectés")
            
            # Rate limiting agressif
            time.sleep(random.uniform(3, 12))
        
        # Sauvegarder
        drama_file = DRAMA_DATA_DIR / "voirdrama_scraped.json"
        with open(drama_file, 'w', encoding='utf-8') as f:
            json.dump(all_dramas, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ VoirDrama terminé: {collected} dramas")
        logger.info(f"   Fichier: {drama_file}\n")
        
        return all_dramas


# ============= CLASSE 3: IMAGE DOWNLOADER (API) =============

class APIImageDownloader:
    """Télécharge images depuis Pexels et Unsplash"""
    
    @staticmethod
    def download_image(url: str, folder: Path, name: str, max_retries: int = 2) -> bool:
        """Télécharge une image"""
        for attempt in range(max_retries):
            try:
                folder.mkdir(parents=True, exist_ok=True)
                path = folder / name
                
                response = requests.get(url, headers=HEADERS, timeout=15)
                
                if response.status_code == 200:
                    if len(response.content) > 10000:  # Min 10KB
                        with open(path, 'wb') as f:
                            f.write(response.content)
                        return True
                
                time.sleep(random.uniform(1, 2))
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 4))
        
        return False
    
    @staticmethod
    def fetch_pexels(query: str, per_page: int = 30, max_retries: int = 2) -> List[str]:
        """Récupère URLs Pexels"""
        for attempt in range(max_retries):
            try:
                url = f"https://api.pexels.com/v1/search?query={quote(query)}&per_page={per_page}"
                headers = HEADERS.copy()
                headers['Authorization'] = PEXELS_API_KEY
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return [p["src"]["original"] for p in data.get("photos", [])]
                
                elif response.status_code in [403, 429]:
                    logger.warning(f"  ⚠️ Pexels rate limit/forbidden")
                    time.sleep(60)
                    continue
                
                time.sleep(random.uniform(1, 3))
            
            except Exception as e:
                logger.debug(f"  Pexels error: {e}")
                time.sleep(random.uniform(2, 4))
        
        return []
    
    @staticmethod
    def fetch_unsplash(query: str, per_page: int = 30, max_retries: int = 2) -> List[str]:
        """Récupère URLs Unsplash"""
        for attempt in range(max_retries):
            try:
                url = "https://api.unsplash.com/search/photos"
                params = {"query": query, "per_page": min(per_page, 30)}
                headers = HEADERS.copy()
                headers['Authorization'] = f"Client-ID {UNSPLASH_KEY}"
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return [p["urls"]["full"] for p in data.get("results", [])]
                
                elif response.status_code in [403, 429]:
                    logger.warning(f"  ⚠️ Unsplash rate limit/forbidden")
                    time.sleep(60)
                    continue
                
                time.sleep(random.uniform(1, 3))
            
            except Exception as e:
                logger.debug(f"  Unsplash error: {e}")
                time.sleep(random.uniform(2, 4))
        
        return []
    
    @staticmethod
    def collect_all_images(target_per_morpho: int = 50) -> Dict:
        """Collecte TOUS les images par morphologie"""
        logger.info("=" * 70)
        logger.info("🖼️  API IMAGES SCRAPING - COLLECTE MASSIVE")
        logger.info("=" * 70)
        
        stats = {}
        
        for morpho in MORPHOLOGIES:
            folder = API_DATA_DIR / morpho
            collected = 0
            queries = MORPHO_QUERIES[morpho]
            
            logger.info(f"\n  📁 {morpho}")
            import random
            random.shuffle(queries)
            
            for query in queries:
                if collected >= target_per_morpho:
                    break
                
                # Pexels
                urls = APIImageDownloader.fetch_pexels(query, per_page=10)
                for i, url in enumerate(urls):
                    if collected >= target_per_morpho:
                        break
                    
                    name = f"pexels_{query.replace(' ','_')}_{i+1:03d}.jpg"
                    if APIImageDownloader.download_image(url, folder, name):
                        collected += 1
                        logger.info(f"     ✓ {collected}/{target_per_morpho}")
                    
                    time.sleep(random.uniform(0.5, 2))
                
                # Unsplash
                urls = APIImageDownloader.fetch_unsplash(query, per_page=10)
                for i, url in enumerate(urls):
                    if collected >= target_per_morpho:
                        break
                    
                    name = f"unsplash_{query.replace(' ','_')}_{i+1:03d}.jpg"
                    if APIImageDownloader.download_image(url, folder, name):
                        collected += 1
                        logger.info(f"     ✓ {collected}/{target_per_morpho}")
                    
                    time.sleep(random.uniform(0.5, 2))
                
                time.sleep(random.uniform(2, 8))
            
            stats[morpho] = collected
            logger.info(f"  ✅ {morpho}: {collected} images")
        
        # Sauvegarder stats
        stats_file = STATS_DIR / "image_collection_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"\n✅ Images API terminé\n")
        return stats


# ============= EXÉCUTION PRINCIPALE =============

def main():
    """Exécute collecte COMPLÈTE"""
    
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " DATA COLLECTION COMPLETE - WIKIPEDIA + VOIRDRAMA + IMAGES ".center(68) + "║")
    logger.info("╚" + "=" * 68 + "╝\n")
    
    try:
        # Phase 1: Wikipedia
        wiki_data = WikipediaScraper.collect_all_wikipedia(target_count=50)
        
        # Phase 2: VoirDrama
        drama_data = VoirDramaScraper.collect_all_dramas(target_count=50)
        
        # Phase 3: Images API
        image_stats = APIImageDownloader.collect_all_images(target_per_morpho=30)
        
        # Résumé
        logger.info("\n" + "=" * 70)
        logger.info("📊 RÉSUMÉ DE LA COLLECTE")
        logger.info("=" * 70)
        logger.info(f"  📚 Articles Wikipedia: {len(wiki_data)}")
        logger.info(f"  🎬 Dramas VoirDrama: {len(drama_data)}")
        logger.info(f"  🖼️  Images par morphologie: {sum(image_stats.values())}")
        logger.info(f"\n  💾 Données sauvegardées dans: {BASE_DIR}")
        
        logger.info("\n" + "╔" + "=" * 68 + "╗")
        logger.info("║" + " ✅ COLLECTE TERMINÉE ".center(68) + "║")
        logger.info("║" + " ".center(68) + "║")
        logger.info("║" + " Prochaine étape: ".center(68) + "║")
        logger.info("║" + " ➜ datatraitement_extended.py (pose detection) ".center(68) + "║")
        logger.info("╚" + "=" * 68 + "╝\n")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Collecte interrompue par l'utilisateur")
    except Exception as e:
        logger.error(f"\n❌ Erreur fatale: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()