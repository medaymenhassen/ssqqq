import numpy as np
import pickle
import cv2
from pathlib import Path

# Configuration
ZOOM_DIR = Path("morphologie_zoom_128_fullbody")
NPZ_DIR = Path("morphologie_npz")
PKL_DIR = Path("morphologie_pkl")
LANDMARK_DIR = "landmarks"  # sous-dossier avec fichiers .npy des landmarks

# Créer les dossiers de sortie
NPZ_DIR.mkdir(parents=True, exist_ok=True)
PKL_DIR.mkdir(parents=True, exist_ok=True)

def images_to_npz(morpho_folder, output_file):
    """Convertir toutes les images d'une morphologie en fichier NPZ"""
    images, filenames = [], []
    for img_file in morpho_folder.glob("*.jpg"):
        img = cv2.imread(str(img_file))
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img_rgb)
            filenames.append(img_file.name)
    if not images:
        return 0
    arr = np.array(images, dtype=np.uint8)
    np.savez_compressed(
        output_file,
        images=arr,
        filenames=np.array(filenames),
        shape=arr.shape,
        morphology=morpho_folder.name
    )
    print(f"✓ NPZ images: {morpho_folder.name} -> {len(arr)}")
    return len(arr)

def images_to_pkl(morpho_folder, output_file):
    """Convertir toutes les images d'une morphologie en fichier PKL"""
    data = {
        'morphology': morpho_folder.name,
        'images': [],
        'filenames': [],
        'metadata': {'image_size': (128,128,3), 'total_count': 0}
    }
    for img_file in morpho_folder.glob("*.jpg"):
        img = cv2.imread(str(img_file))
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)/255.0
            data['images'].append(img_rgb)
            data['filenames'].append(img_file.name)
    if not data['images']:
        return 0
    data['images'] = np.array(data['images'])
    data['metadata']['total_count'] = len(data['images'])
    with open(output_file, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"✓ PKL images: {morpho_folder.name} -> {data['metadata']['total_count']}")
    return data['metadata']['total_count']

import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5
)

def landmarks_to_npz(morpho_folder, output_file):
    """Extraire landmarks des images JPG et les convertir en NPZ"""
    points, filenames = [], []
    
    # Traiter directement les fichiers .jpg
    for img_file in morpho_folder.glob("*.jpg"):
        img = cv2.imread(str(img_file))
        if img is not None:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)
            
            if results.pose_landmarks:
                # Extraire les coordonnées des landmarks
                landmarks = []
                for lm in results.pose_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y, lm.z, lm.visibility])
                
                points.append(np.array(landmarks, dtype=np.float32))
                filenames.append(img_file.name)
    
    if not points:
        return 0
    
    arr = np.array(points, dtype=np.float32)
    np.savez_compressed(
        output_file,
        landmarks=arr,
        filenames=np.array(filenames),
        shape=arr.shape,
        morphology=morpho_folder.name
    )
    
    print(f"✓ NPZ landmarks: {morpho_folder.name} -> {len(arr)} sets")
    return len(arr)


def landmarks_to_pkl(morpho_folder, output_file):
    """Extraire landmarks des images JPG et les convertir en fichier PKL"""
    data = {
        'morphology': morpho_folder.name,
        'landmarks': [],
        'filenames': [],
        'metadata': {'total_count': 0}
    }
    
    # Traiter directement les fichiers .jpg
    for img_file in morpho_folder.glob("*.jpg"):
        img = cv2.imread(str(img_file))
        if img is not None:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)
            
            if results.pose_landmarks:
                # Extraire les coordonnées des landmarks
                landmarks = []
                for lm in results.pose_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y, lm.z, lm.visibility])
                
                data['landmarks'].append(np.array(landmarks, dtype=np.float32))
                data['filenames'].append(img_file.name)
    
    if not data['landmarks']:
        return 0
    
    data['landmarks'] = np.array(data['landmarks'])
    data['metadata']['total_count'] = len(data['landmarks'])
    
    with open(output_file, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"✓ PKL landmarks: {morpho_folder.name} -> {data['metadata']['total_count']}")
    return data['metadata']['total_count']

# Traitement pour chaque morphologie
total_npz_imgs = total_pkl_imgs = 0
total_npz_lms = total_pkl_lms = 0

print("🔄 Conversion des images et landmarks en NPZ et PKL...")
print("="*60)

for morpho_folder in ZOOM_DIR.iterdir():
    if not morpho_folder.is_dir():
        continue
    name = morpho_folder.name
    print(f"\n📁 Traitement: {name}")

    # fichiers de sortie
    npz_img = NPZ_DIR / f"{name}_images.npz"
    pkl_img = PKL_DIR / f"{name}_images.pkl"
    npz_lm  = NPZ_DIR / f"{name}_landmarks.npz"
    pkl_lm  = PKL_DIR / f"{name}_landmarks.pkl"

    # images
    total_npz_imgs += images_to_npz(morpho_folder, npz_img)
    total_pkl_imgs += images_to_pkl(morpho_folder, pkl_img)
    # landmarks
    total_npz_lms += landmarks_to_npz(morpho_folder, npz_lm)
    total_pkl_lms += landmarks_to_pkl(morpho_folder, pkl_lm)

print(f"\n🎉 CONVERSION TERMINÉE!")
print(f"📊 Total NPZ images: {total_npz_imgs:,}")
print(f"📊 Total PKL images: {total_pkl_imgs:,}")
print(f"📊 Total NPZ landmarks: {total_npz_lms:,}")
print(f"📊 Total PKL landmarks: {total_pkl_lms:,}")
print(f"📁 NPZ sauvegardés dans: {NPZ_DIR}")
print(f"📁 PKL sauvegardés dans: {PKL_DIR}")
