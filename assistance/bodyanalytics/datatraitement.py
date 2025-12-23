
import cv2
import mediapipe as mp
import logging
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional, List
import json
from datetime import datetime
from collections import defaultdict

# ============= CONFIGURATION LOGGING =============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ============= CONFIGURATION =============

MORPHOLOGIES = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

# Répertoires sources
STATIC_IMAGES_DIR = Path("morphologie_dataset_api")
VIDEO_FRAMES_DIR = Path("morphologie_dataset_extended/temp_video_frames")

# Répertoires de sortie
OUTPUT_BASE_DIR = Path("morphologie_processed_advanced")
OUTPUT_FULL_BODY = OUTPUT_BASE_DIR / "full_body_128"
OUTPUT_EYES = OUTPUT_BASE_DIR / "eyes_64"
OUTPUT_MOUTH = OUTPUT_BASE_DIR / "mouth_64"
OUTPUT_HANDS = OUTPUT_BASE_DIR / "hands_64"

STATS_DIR = Path("datatraitement_advanced_stats")
STATS_DIR.mkdir(parents=True, exist_ok=True)

# Créer tous les répertoires
for output_dir in [OUTPUT_BASE_DIR, OUTPUT_FULL_BODY, OUTPUT_EYES, OUTPUT_MOUTH, OUTPUT_HANDS, STATS_DIR]:
    output_dir.mkdir(parents=True, exist_ok=True)

# MediaPipe initializers
mp_pose = mp.solutions.pose
mp_face_detection = mp.solutions.face_detection
mp_hands = mp.solutions.hands

pose = mp_pose.Pose(static_image_mode=True, model_complexity=1, min_detection_confidence=0.5)
face_detector = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.5)

# Landmarks indices MediaPipe Pose
POSE_LANDMARKS = {
    'eyes': [33, 133, 362, 263],  # left eye, right eye
    'mouth': [78, 308],  # lips corners
    'hands': list(range(15, 21)) + list(range(16, 22)),  # hands
    'body': list(range(0, 33))
}

# ============= CLASSE 1: ZONE DETECTOR =============

class ZoneDetector:
    """Détecte et extrait régions d'intérêt (yeux, bouche, mains, corps)"""
    
    def __init__(self):
        self.pose = mp_pose.Pose(static_image_mode=True, model_complexity=1, min_detection_confidence=0.5)
        self.face_detector = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
        self.hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.5)
    
    def detect_pose_landmarks(self, image: np.ndarray) -> Optional[Dict]:
        """Détecte tous les landmarks pose"""
        try:
            h, w = image.shape[:2]
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)
            
            if not results.pose_landmarks:
                return None
            
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                landmarks.append({
                    'x': lm.x * w,
                    'y': lm.y * h,
                    'z': lm.z,
                    'visibility': lm.visibility
                })
            
            return {'landmarks': landmarks, 'valid': len(landmarks) == 33}
        except Exception as e:
            logger.debug(f"⚠️ Erreur pose detection: {e}")
            return None
    
    def detect_face_region(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Détecte région du visage"""
        try:
            h, w = image.shape[:2]
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_detector.process(rgb)
            
            if not results.detections:
                return None
            
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            
            x_min = int(max(bbox.xmin * w - 10, 0))
            x_max = int(min((bbox.xmin + bbox.width) * w + 10, w))
            y_min = int(max(bbox.ymin * h - 10, 0))
            y_max = int(min((bbox.ymin + bbox.height) * h + 10, h))
            
            return x_min, x_max, y_min, y_max
        except Exception as e:
            logger.debug(f"⚠️ Erreur face detection: {e}")
            return None
    
    def extract_eyes(self, image: np.ndarray, landmarks: list) -> Optional[np.ndarray]:
        """Extrait région des yeux"""
        try:
            h, w = image.shape[:2]
            
            # Points des yeux
            eye_indices = [33, 133, 362, 263, 160, 387]  # left+right eyes+corners
            points = []
            
            for idx in eye_indices:
                if idx < len(landmarks):
                    points.append([landmarks[idx]['x'], landmarks[idx]['y']])
            
            if len(points) < 4:
                return None
            
            points = np.array(points, dtype=np.float32)
            x_min = int(max(np.min(points[:, 0]) - 20, 0))
            x_max = int(min(np.max(points[:, 0]) + 20, w))
            y_min = int(max(np.min(points[:, 1]) - 15, 0))
            y_max = int(min(np.max(points[:, 1]) + 15, h))
            
            crop = image[y_min:y_max, x_min:x_max]
            if crop.size == 0:
                return None
            
            # Redimensionner à 64x64
            resized = cv2.resize(crop, (64, 64), interpolation=cv2.INTER_AREA)
            return resized
        except Exception as e:
            logger.debug(f"⚠️ Erreur extraction yeux: {e}")
            return None
    
    def extract_mouth(self, image: np.ndarray, landmarks: list) -> Optional[np.ndarray]:
        """Extrait région de la bouche"""
        try:
            h, w = image.shape[:2]
            
            # Points de la bouche
            mouth_indices = [0, 17, 78, 308, 13, 14]  # mouth points
            points = []
            
            for idx in mouth_indices:
                if idx < len(landmarks):
                    points.append([landmarks[idx]['x'], landmarks[idx]['y']])
            
            if len(points) < 3:
                return None
            
            points = np.array(points, dtype=np.float32)
            x_min = int(max(np.min(points[:, 0]) - 15, 0))
            x_max = int(min(np.max(points[:, 0]) + 15, w))
            y_min = int(max(np.min(points[:, 1]) - 10, 0))
            y_max = int(min(np.max(points[:, 1]) + 10, h))
            
            crop = image[y_min:y_max, x_min:x_max]
            if crop.size == 0:
                return None
            
            # Redimensionner à 64x64
            resized = cv2.resize(crop, (64, 64), interpolation=cv2.INTER_AREA)
            return resized
        except Exception as e:
            logger.debug(f"⚠️ Erreur extraction bouche: {e}")
            return None
    
    def extract_hands(self, image: np.ndarray, landmarks: list) -> List[np.ndarray]:
        """Extrait régions des mains"""
        hands_crops = []
        try:
            h, w = image.shape[:2]
            
            # Indices des mains dans MediaPipe Pose
            left_hand_indices = [15, 17, 19, 21]  # left hand points
            right_hand_indices = [16, 18, 20, 22]  # right hand points
            
            for hand_indices in [left_hand_indices, right_hand_indices]:
                points = []
                for idx in hand_indices:
                    if idx < len(landmarks) and landmarks[idx]['visibility'] > 0.5:
                        points.append([landmarks[idx]['x'], landmarks[idx]['y']])
                
                if len(points) < 2:
                    continue
                
                points = np.array(points, dtype=np.float32)
                x_min = int(max(np.min(points[:, 0]) - 20, 0))
                x_max = int(min(np.max(points[:, 0]) + 20, w))
                y_min = int(max(np.min(points[:, 1]) - 20, 0))
                y_max = int(min(np.max(points[:, 1]) + 20, h))
                
                crop = image[y_min:y_max, x_min:x_max]
                if crop.size > 0:
                    resized = cv2.resize(crop, (64, 64), interpolation=cv2.INTER_AREA)
                    hands_crops.append(resized)
        
        except Exception as e:
            logger.debug(f"⚠️ Erreur extraction mains: {e}")
        
        return hands_crops
    
    def extract_full_body(self, image: np.ndarray, landmarks: list) -> Optional[np.ndarray]:
        """Extrait corps complet avec padding"""
        try:
            h, w = image.shape[:2]
            
            points = []
            for lm in landmarks:
                points.append([lm['x'], lm['y']])
            
            points = np.array(points, dtype=np.float32)
            
            x_min = int(max(np.min(points[:, 0]) - 0.05 * w, 0))
            x_max = int(min(np.max(points[:, 0]) + 0.05 * w, w))
            y_min = int(max(np.min(points[:, 1]) - 0.05 * h, 0))
            y_max = int(min(np.max(points[:, 1]) + 0.05 * h, h))
            
            crop = image[y_min:y_max, x_min:x_max]
            if crop.size == 0:
                return None
            
            # Padding pour carré
            ch, cw = crop.shape[:2]
            if ch > cw:
                pad_left = (ch - cw) // 2
                pad_right = ch - cw - pad_left
                canvas = cv2.copyMakeBorder(crop, 0, 0, pad_left, pad_right, cv2.BORDER_CONSTANT)
            else:
                pad_top = (cw - ch) // 2
                pad_bottom = cw - ch - pad_top
                canvas = cv2.copyMakeBorder(crop, pad_top, pad_bottom, 0, 0, cv2.BORDER_CONSTANT)
            
            resized = cv2.resize(canvas, (128, 128), interpolation=cv2.INTER_AREA)
            return resized
        except Exception as e:
            logger.debug(f"⚠️ Erreur extraction corps: {e}")
            return None


# ============= CLASSE 2: BATCH PROCESSOR =============

class AdvancedImageProcessor:
    """Traite images avec détection multi-zone"""
    
    def __init__(self):
        self.zone_detector = ZoneDetector()
    
    def process_image(self, img: np.ndarray) -> Dict[str, Optional[np.ndarray]]:
        """
        Traite une image et extrait toutes les zones
        Retourne: {full_body, eyes, mouth, hands}
        """
        result = {
            'full_body': None,
            'eyes': None,
            'mouth': None,
            'hands': []
        }
        
        # Redimensionner si trop gros
        h, w = img.shape[:2]
        if max(h, w) > 800:
            scale = 800 / max(h, w)
            img = cv2.resize(img, (int(w*scale), int(h*scale)))
        
        # Détection pose
        pose_data = self.zone_detector.detect_pose_landmarks(img)
        if not pose_data or not pose_data['valid']:
            return result
        
        landmarks = pose_data['landmarks']
        
        # Extraction zones
        result['full_body'] = self.zone_detector.extract_full_body(img, landmarks)
        result['eyes'] = self.zone_detector.extract_eyes(img, landmarks)
        result['mouth'] = self.zone_detector.extract_mouth(img, landmarks)
        result['hands'] = self.zone_detector.extract_hands(img, landmarks)
        
        return result
    
    def process_batch(self, input_dir: Path, morpho: str) -> Dict:
        """Traite un batch d'images et sauvegarde par zone"""
        
        stats = {
            'total': 0,
            'full_body': 0,
            'eyes': 0,
            'mouth': 0,
            'hands': 0,
            'failed': 0
        }
        
        for img_file in sorted(input_dir.glob("*.jpg")):
            stats['total'] += 1
            
            try:
                img = cv2.imread(str(img_file))
                if img is None:
                    stats['failed'] += 1
                    continue
                
                # Traiter
                zones = self.process_image(img)
                
                # Sauvegarder full_body
                if zones['full_body'] is not None:
                    output_dir = OUTPUT_FULL_BODY / morpho
                    output_dir.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(output_dir / img_file.name), zones['full_body'])
                    stats['full_body'] += 1
                
                # Sauvegarder eyes
                if zones['eyes'] is not None:
                    output_dir = OUTPUT_EYES / morpho
                    output_dir.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(output_dir / f"eyes_{img_file.stem}.jpg"), zones['eyes'])
                    stats['eyes'] += 1
                
                # Sauvegarder mouth
                if zones['mouth'] is not None:
                    output_dir = OUTPUT_MOUTH / morpho
                    output_dir.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(output_dir / f"mouth_{img_file.stem}.jpg"), zones['mouth'])
                    stats['mouth'] += 1
                
                # Sauvegarder hands
                if zones['hands']:
                    output_dir = OUTPUT_HANDS / morpho
                    output_dir.mkdir(parents=True, exist_ok=True)
                    for i, hand in enumerate(zones['hands']):
                        cv2.imwrite(str(output_dir / f"hand{i}_{img_file.stem}.jpg"), hand)
                    stats['hands'] += len(zones['hands'])
                
                if stats['full_body'] % 50 == 0:
                    logger.info(f"   ✓ {stats['full_body']} images traitées")
            
            except Exception as e:
                stats['failed'] += 1
                logger.debug(f"⚠️ Erreur: {e}")
        
        return stats


# ============= PIPELINE PRINCIPAL =============

class AdvancedDataProcessingPipeline:
    """Pipeline avancé avec détection multi-zone"""
    
    def __init__(self):
        self.processor = AdvancedImageProcessor()
        self.stats_global = defaultdict(dict)
    
    def process_all_images(self):
        """Traite images statiques + vidéos"""
        
        logger.info("=" * 70)
        logger.info("🔬 TRAITEMENT AVANCÉ - DÉTECTION MULTI-ZONE")
        logger.info("=" * 70)
        
        for morpho in MORPHOLOGIES:
            logger.info(f"\n  📁 Morphologie: {morpho}")
            
            stats_total = {
                'total': 0, 'full_body': 0, 'eyes': 0, 'mouth': 0, 'hands': 0, 'failed': 0
            }
            
            # Traiter images statiques
            static_dir = STATIC_IMAGES_DIR / morpho
            if static_dir.exists():
                logger.info(f"     📷 Images statiques...")
                stats = self.processor.process_batch(static_dir, morpho)
                for key in stats:
                    stats_total[key] += stats[key]
            
            # Traiter frames vidéo
            video_dir = VIDEO_FRAMES_DIR / morpho / "frames"
            if video_dir.exists():
                logger.info(f"     🎬 Frames vidéo...")
                stats = self.processor.process_batch(video_dir, morpho)
                for key in stats:
                    stats_total[key] += stats[key]
            
            self.stats_global[morpho] = stats_total
            
            logger.info(f"\n     ✅ {morpho}:")
            logger.info(f"        Corps complet: {stats_total['full_body']}")
            logger.info(f"        Yeux: {stats_total['eyes']}")
            logger.info(f"        Bouche: {stats_total['mouth']}")
            logger.info(f"        Mains: {stats_total['hands']}")
    
    def generate_report(self):
        """Génère rapport final"""
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 RAPPORT FINAL")
        logger.info("=" * 70)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'morphologies': self.stats_global,
            'output_directories': {
                'full_body': str(OUTPUT_FULL_BODY),
                'eyes': str(OUTPUT_EYES),
                'mouth': str(OUTPUT_MOUTH),
                'hands': str(OUTPUT_HANDS)
            }
        }
        
        # Sauvegarder
        report_file = STATS_DIR / "advanced_processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n📋 Rapport: {report_file}")
        
        return report


# ============= EXÉCUTION =============

def main():
    """Exécute pipeline avancé"""
    
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " TRAITEMENT AVANCÉ - DÉTECTION MULTI-ZONE ".center(68) + "║")
    logger.info("║" + " (Corps + Yeux + Bouche + Mains) ".center(68) + "║")
    logger.info("╚" + "=" * 68 + "╝")
    
    try:
        pipeline = AdvancedDataProcessingPipeline()
        pipeline.process_all_images()
        report = pipeline.generate_report()
        
        logger.info("\n" + "╔" + "=" * 68 + "╗")
        logger.info("║" + " ✅ TRAITEMENT TERMINÉ ".center(68) + "║")
        logger.info("║" + " ".center(68) + "║")
        logger.info("║" + " Prochaine étape: ".center(68) + "║")
        logger.info("║" + " ➜ train_progressive.py ".center(68) + "║")
        logger.info("╚" + "=" * 68 + "╝\n")
        
    except Exception as e:
        logger.error(f"\n❌ Erreur: {e}", exc_info=True)


if __name__ == "__main__":
    main()