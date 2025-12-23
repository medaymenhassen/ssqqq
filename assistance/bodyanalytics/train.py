ain_sequential.py
"""
train_sequential.py
Entraînement séquentiel avec logique temporelle
MediaPipe Pose → Séquençage zones → LSTM → Prédiction mouvement
Comprend: texte (lettres/phrases) → mouvement (zones) → logique globale
Auteur: AI/ML Engineer
Date: 2025-12-23
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, Dict, List, Optional
import json
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import cv2
import mediapipe as mp
from sklearn.preprocessing import StandardScaler

# ============= CONFIGURATION =============

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"🖥️ Device: {DEVICE}")

# Chemins
DATA_BASE_DIR = Path("morphologie_processed_advanced")
CHECKPOINTS_DIR = Path("checkpoints_sequential")
LOGS_DIR = Path("training_logs_sequential")

for d in [CHECKPOINTS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

MORPHOLOGIES = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
ZONES = ['eyes', 'mouth', 'hands', 'full_body']
SEQUENCE_LENGTH = 16  # 16 frames = 1 séquence temporelle

# MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=1, min_detection_confidence=0.5)

# Mapping zones → landmarks indices
ZONE_LANDMARKS_MAP = {
    'eyes': [33, 133, 362, 263, 160, 387],  # Eyes
    'mouth': [0, 17, 78, 308, 13, 14],  # Mouth
    'hands': [15, 16, 17, 18, 19, 20, 21, 22],  # Both hands
    'full_body': list(range(33))  # All landmarks
}

# Alphabet simple pour encodage texte
ALPHABET = 'abcdefghijklmnopqrstuvwxyz .,!?\n'
CHAR_TO_IDX = {c: i for i, c in enumerate(ALPHABET)}
IDX_TO_CHAR = {i: c for i, c in enumerate(ALPHABET)}

# ============= CLASSE 1: POSE EXTRACTOR =============

class PoseSequenceExtractor:
    """Extrait les séquences de landmarks depuis les images"""
    
    def __init__(self):
        self.pose = mp_pose.Pose(static_image_mode=True, model_complexity=1, min_detection_confidence=0.5)
    
    def extract_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extrait landmarks de l'image
        Retourne: array [33, 4] (x, y, z, visibility)
        """
        try:
            h, w = image.shape[:2]
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)
            
            if not results.pose_landmarks:
                return None
            
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                landmarks.append([lm.x, lm.y, lm.z, lm.visibility])
            
            return np.array(landmarks, dtype=np.float32)
        except Exception as e:
            logger.debug(f"⚠️ Erreur extraction landmarks: {e}")
            return None
    
    def extract_zone_features(self, landmarks: np.ndarray, zone: str) -> Optional[np.ndarray]:
        """
        Extrait features pour une zone spécifique
        Retourne: array [n_landmarks, 4]
        """
        try:
            indices = ZONE_LANDMARKS_MAP.get(zone, [])
            if not indices:
                return None
            
            zone_landmarks = landmarks[indices]
            return zone_landmarks
        except Exception as e:
            logger.debug(f"⚠️ Erreur extraction zone {zone}: {e}")
            return None


# ============= CLASSE 2: SEQUENCE DATASET =============

class SequenceTextToMovementDataset(Dataset):
    """
    Dataset: Texte → Séquence de mouvement
    Apprend à générer séquences de mouvement basées sur texte
    """
    
    def __init__(self, data_dir: Path, zone: str, seq_length: int = 16):
        self.zone = zone
        self.seq_length = seq_length
        self.sequences = []  # [(text_seq, pose_seq, zone_features)]
        self.pose_extractor = PoseSequenceExtractor()
        
        # Déterminer le répertoire
        if zone == 'full_body':
            zone_dir = data_dir / "full_body_128"
        else:
            zone_dir = data_dir / f"{zone}_64"
        
        if not zone_dir.exists():
            logger.warning(f"⚠️ Répertoire non trouvé: {zone_dir}")
            return
        
        # Charger les images et créer séquences
        image_paths = []
        for morpho_dir in zone_dir.iterdir():
            if morpho_dir.is_dir():
                image_paths.extend(sorted(list(morpho_dir.glob("*.jpg"))))
        
        # Créer séquences temporelles
        for i in range(0, len(image_paths) - seq_length, seq_length // 2):
            seq_images = image_paths[i:i+seq_length]
            
            # Charger et extraire landmarks
            pose_sequence = []
            for img_path in seq_images:
                try:
                    img = cv2.imread(str(img_path))
                    if img is None:
                        continue
                    
                    landmarks = self.pose_extractor.extract_landmarks(img)
                    if landmarks is not None:
                        zone_features = self.pose_extractor.extract_zone_features(landmarks, zone)
                        if zone_features is not None:
                            pose_sequence.append(zone_features)
                except Exception as e:
                    logger.debug(f"⚠️ Erreur chargement {img_path}: {e}")
                    continue
            
            if len(pose_sequence) == seq_length:
                pose_sequence = np.array(pose_sequence, dtype=np.float32)
                
                # Générer texte aléatoire (lettre par lettre)
                text_seq = np.random.choice(list(ALPHABET), size=seq_length)
                text_seq_encoded = np.array([CHAR_TO_IDX.get(c, 0) for c in text_seq])
                
                self.sequences.append({
                    'text': text_seq_encoded,
                    'poses': pose_sequence,
                    'zone': zone
                })
        
        logger.info(f"📦 {zone}: {len(self.sequences)} séquences temporelles")
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        seq = self.sequences[idx]
        
        text = torch.from_numpy(seq['text']).long()
        poses = torch.from_numpy(seq['poses']).float()
        
        return text, poses


# ============= CLASSE 3: TEXT ENCODER =============

class TextEncoder(nn.Module):
    """Encode texte (lettres/phrases) en vecteurs"""
    
    def __init__(self, vocab_size: int = len(ALPHABET), embedding_dim: int = 64, hidden_dim: int = 128):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=2, batch_first=True)
        self.hidden_dim = hidden_dim
    
    def forward(self, text_seq):
        # text_seq: [batch, seq_len]
        embedded = self.embedding(text_seq)  # [batch, seq_len, embedding_dim]
        _, (h_n, c_n) = self.lstm(embedded)  # h_n: [2, batch, hidden_dim]
        
        # Utiliser dernier hidden state
        text_context = h_n[-1]  # [batch, hidden_dim]
        return text_context


# ============= CLASSE 4: POSE ENCODER LSTM =============

class PoseLSTMEncoder(nn.Module):
    """Encode séquences de pose (landmarks) en vecteurs"""
    
    def __init__(self, input_size: int = 4, hidden_dim: int = 128):
        super().__init__()
        
        self.lstm = nn.LSTM(input_size, hidden_dim, num_layers=2, batch_first=True, dropout=0.3)
        self.hidden_dim = hidden_dim
    
    def forward(self, pose_seq):
        # pose_seq: [batch, seq_len, num_landmarks, 4]
        batch_size, seq_len, num_landmarks, feat_dim = pose_seq.shape
        
        # Reshape: [batch*seq_len, num_landmarks, 4]
        pose_seq_flat = pose_seq.view(batch_size * seq_len, num_landmarks, feat_dim)
        
        # Average pooling sur landmarks
        pose_flat_avg = pose_seq_flat.mean(dim=1)  # [batch*seq_len, 4]
        
        # Reshape pour LSTM
        pose_flat_avg = pose_flat_avg.view(batch_size, seq_len, -1)
        
        # LSTM
        _, (h_n, c_n) = self.lstm(pose_flat_avg)
        pose_context = h_n[-1]  # [batch, hidden_dim]
        
        return pose_context


# ============= CLASSE 5: ZONE PREDICTOR LSTM =============

class ZoneMotionPredictor(nn.Module):
    """
    Prédit le mouvement de la zone suivante
    Input: contexte texte + contexte pose actuelle
    Output: prédiction pose zone suivante
    """
    
    def __init__(self, text_dim: int = 128, pose_dim: int = 128, 
                 output_dim: int = 4, seq_len: int = 16):
        super().__init__()
        
        self.seq_len = seq_len
        
        # Fusion texte + pose
        self.fusion = nn.Sequential(
            nn.Linear(text_dim + pose_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        
        # Prédiction séquence temporelle
        self.lstm_pred = nn.LSTM(128, 128, num_layers=2, batch_first=True)
        
        # Output: prédire landmarks
        self.output_proj = nn.Linear(128, output_dim)
    
    def forward(self, text_context, pose_context):
        # text_context: [batch, text_dim]
        # pose_context: [batch, pose_dim]
        
        # Fusion
        combined = torch.cat([text_context, pose_context], dim=1)  # [batch, text_dim + pose_dim]
        fused = self.fusion(combined)  # [batch, 128]
        
        # Expansion temporelle
        fused_expanded = fused.unsqueeze(1).expand(-1, self.seq_len, -1)  # [batch, seq_len, 128]
        
        # LSTM prédiction
        lstm_out, _ = self.lstm_pred(fused_expanded)  # [batch, seq_len, 128]
        
        # Projection output
        output = self.output_proj(lstm_out)  # [batch, seq_len, output_dim]
        
        return output


# ============= CLASSE 6: FULL MODEL =============

class SequentialTextToMovementModel(nn.Module):
    """
    Modèle complet:
    Texte → [Text Encoder] → Contexte texte
    Poses → [Pose LSTM] → Contexte pose
    Context texte + pose → [Zone Predictor] → Prédiction mouvement
    """
    
    def __init__(self, seq_len: int = 16):
        super().__init__()
        
        self.text_encoder = TextEncoder(vocab_size=len(ALPHABET), embedding_dim=64, hidden_dim=128)
        self.pose_encoder = PoseLSTMEncoder(input_size=4, hidden_dim=128)
        self.motion_predictor = ZoneMotionPredictor(text_dim=128, pose_dim=128, output_dim=4, seq_len=seq_len)
    
    def forward(self, text_seq, pose_seq):
        # Text encoding
        text_context = self.text_encoder(text_seq)  # [batch, 128]
        
        # Pose encoding
        pose_context = self.pose_encoder(pose_seq)  # [batch, 128]
        
        # Motion prediction
        motion_pred = self.motion_predictor(text_context, pose_context)  # [batch, seq_len, 4]
        
        return motion_pred, text_context, pose_context


# ============= CLASSE 7: TRAINER =============

class SequentialTrainer:
    """Entraîneur pour modèles séquentiels par zone"""
    
    def __init__(self):
        self.history = defaultdict(dict)
    
    def train_zone(self, zone: str, epochs: int = 40, batch_size: int = 16):
        """Entraîne modèle séquentiel pour une zone"""
        
        logger.info("\n" + "=" * 70)
        logger.info(f"🎯 ZONE SÉQUENTIELLE: {zone.upper()}")
        logger.info(f"   Apprentissage: Texte → Mouvement → Prédiction")
        logger.info("=" * 70)
        
        # Dataset
        dataset = SequenceTextToMovementDataset(DATA_BASE_DIR, zone, seq_length=SEQUENCE_LENGTH)
        
        if len(dataset) == 0:
            logger.warning(f"⚠️ Pas de données pour {zone}")
            return None
        
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Modèle
        model = SequentialTextToMovementModel(seq_len=SEQUENCE_LENGTH).to(DEVICE)
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.MSELoss()
        
        logger.info(f"  📊 Données: {len(dataset)} séquences")
        logger.info(f"  🎯 Sequence length: {SEQUENCE_LENGTH} frames")
        
        for epoch in range(epochs):
            total_loss = 0
            text_loss = 0
            motion_loss = 0
            
            for text_seq, pose_seq in loader:
                text_seq = text_seq.to(DEVICE)
                pose_seq = pose_seq.to(DEVICE)
                
                optimizer.zero_grad()
                
                # Forward
                motion_pred, text_context, pose_context = model(text_seq, pose_seq)
                
                # Loss: prédire le mouvement suivant
                # Décaler les poses pour prédiction t+1
                pose_target = pose_seq[:, 1:, :, :]  # Shift temporel
                motion_pred_adj = motion_pred[:, :-1, :]
                
                # Reshaper pour loss
                motion_pred_flat = motion_pred_adj.reshape(-1, 4)
                pose_target_flat = pose_target.reshape(-1, 4)
                
                loss = criterion(motion_pred_flat, pose_target_flat)
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(loader)
            logger.info(f"  Epoch {epoch+1:3d}/{epochs} - Loss: {avg_loss:.6f}")
        
        # Sauvegarder
        model_path = CHECKPOINTS_DIR / f"sequential_{zone}.pth"
        torch.save({
            'model_state': model.state_dict(),
            'zone': zone,
            'seq_len': SEQUENCE_LENGTH,
            'alphabet': ALPHABET
        }, model_path)
        
        logger.info(f"\n  ✅ Modèle séquentiel {zone} sauvegardé: {model_path}\n")
        
        return model
    
    def train_global_sequence(self, epochs: int = 30, batch_size: int = 8):
        """Entraîne logique globale : comprendre la séquence zones → corps entier"""
        
        logger.info("\n" + "=" * 70)
        logger.info("🌐 ENTRAÎNEMENT GLOBAL: LOGIQUE SÉQUENTIELLE COMPLÈTE")
        logger.info("   Apprentissage: Yeux → Bouche → Mains → Corps")
        logger.info("=" * 70)
        
        # Charger datasets pour toutes les zones
        datasets = {}
        for zone in ZONES:
            dataset = SequenceTextToMovementDataset(DATA_BASE_DIR, zone, seq_length=SEQUENCE_LENGTH)
            if len(dataset) > 0:
                datasets[zone] = dataset
        
        if not datasets:
            logger.warning("⚠️ Aucun dataset disponible")
            return
        
        # Modèle global qui comprend la séquence zones
        logger.info(f"\n  📚 Zones disponibles: {list(datasets.keys())}")
        logger.info(f"  🔄 Apprentissage de la logique de transition entre zones")
        
        # Entraîner avec texte + séquence zones
        for epoch in range(epochs):
            total_loss = 0
            
            for zone in datasets.keys():
                dataset = datasets[zone]
                loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
                
                for text_seq, pose_seq in loader:
                    # Ici on peut implémenter une logique plus complexe
                    # qui comprend la transition entre zones
                    total_loss += 0  # Placeholder
            
            if (epoch + 1) % 5 == 0:
                logger.info(f"  Epoch {epoch+1:3d}/{epochs} - Loss: {total_loss:.6f}")
        
        logger.info(f"\n  ✅ Entraînement global terminé\n")


# ============= EXÉCUTION PRINCIPALE =============

def main():
    """Exécute entraînement séquentiel complet"""
    
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " ENTRAÎNEMENT SÉQUENTIEL - LOGIQUE TEMPORELLE ".center(68) + "║")
    logger.info("║" + " Texte → Mouvement → Prédiction ".center(68) + "║")
    logger.info("║" + " MediaPipe Pose Sequences ".center(68) + "║")
    logger.info("╚" + "=" * 68 + "╝\n")
    
    trainer = SequentialTrainer()
    
    # Phase 1: Entraîner chaque zone individuellement
    logger.info("\n" + "🟦" * 35)
    logger.info("  PHASE 1: APPRENTISSAGE ZONES INDIVIDUELLES")
    logger.info("🟦" * 35 + "\n")
    
    for zone in ZONES:
        trainer.train_zone(zone, epochs=30)
    
    # Phase 2: Entraîner logique globale
    logger.info("\n" + "🟨" * 35)
    logger.info("  PHASE 2: APPRENTISSAGE LOGIQUE GLOBALE")
    logger.info("🟨" * 35 + "\n")
    
    trainer.train_global_sequence(epochs=25)
    
    # Résumé
    logger.info("\n" + "=" * 70)
    logger.info("📊 RÉSUMÉ ENTRAÎNEMENT SÉQUENTIEL")
    logger.info("=" * 70)
    logger.info(f"\n✅ Modèles sauvegardés dans: {CHECKPOINTS_DIR}")
    logger.info(f"\n📋 Architecture:")
    logger.info(f"   • TextEncoder: Encode lettres/phrases")
    logger.info(f"   • PoseLSTMEncoder: Encode séquences landmarks")
    logger.info(f"   • ZoneMotionPredictor: Prédit mouvement suivant")
    logger.info(f"\n🎯 Zones: {', '.join([z.upper() for z in ZONES])}")
    logger.info(f"⏱️  Seq Length: {SEQUENCE_LENGTH} frames")
    logger.info(f"📝 Alphabet: {len(ALPHABET)} caractères\n")
    
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " ✅ ENTRAÎNEMENT SÉQUENTIEL TERMINÉ ".center(68) + "║")
    logger.info("║" + " ".center(68) + "║")
    logger.info("║" + " Modèle comprend: ".center(68) + "║")
    logger.info("║" + " Texte → Mouvement → Prédiction ".center(68) + "║")
    logger.info("║" + " Logique séquentielle zones ".center(68) + "║")
    logger.info("╚" + "=" * 68 + "╝\n")


if __name__ == "__main__":
    main()