

import os
import sys
import json
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, Request
import base64

class MotionCaptureDatasetCollector:
    """Collecteur de datasets vidéo + pose pour motion capture"""
    
    def __init__(self, base_path: str = "./motion_capture_data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Token Kaggle
        self.username = 'kaggle_user'
        self.api_key = 'KGAT_fc99b34bd412f6b701a7476f118e9a4d'
        
        # ⭐ DATASETS RÉELLEMENT EXPLOITABLES POUR MOTION CAPTURE
        self.datasets = {
            "coco_keypoints": {
                "name": "COCO 2014 - 17 Keypoints Skeleton",
                "description": "40K+ images avec annotations skeleton 2D (17 joints)",
                "category": "keypoint_detection",
                "format": "Images JPG + JSON (COCO format)",
                "joints": "17 (Nose, Eyes, Ears, Shoulders, Elbows, Wrists, Hips, Knees, Ankles)",
                "size": "~13GB (train), ~6GB (val)",
                "use_case": "✅ Pose estimation 2D, skeleton learning, animation rigging",
                "tags": ["pose-2d", "skeleton", "coco", "keypoints"],
                "kaggle_id": "awsaf49/coco-2014-dataset",
                "api_url": "https://www.kaggle.com/api/v1/datasets/download/awsaf49/coco-2014-dataset"
            },
            
            "human3_6m": {
                "name": "Human3.6M - Professional MoCap Dataset",
                "description": "11 acteurs, 32 joints 3D, vidéos RGB synchronisées",
                "category": "mocap_3d",
                "format": "MP4 vidéos + PKL (3D skeleton 32 joints)",
                "joints": "32 (full skeletal hierarchy with hands/feet)",
                "size": "~150GB (complet), ~5GB (échantillon)",
                "use_case": "✅ 3D pose, motion synthesis, retargeting, animation",
                "tags": ["mocap-3d", "video", "ground-truth", "32-joints"],
                "kaggle_id": "soumikdey/human36m-mocap-dataset",
                "api_url": "https://www.kaggle.com/api/v1/datasets/download/soumikdey/human36m-mocap-dataset"
            },
            
            "pose_sports_video": {
                "name": "Sports Actions Pose Dataset",
                "description": "500+ vidéos sports (foot, basket, tennis) 30fps avec pose",
                "category": "sports_video",
                "format": "MP4 + JSON skeleton temporel",
                "joints": "17-25 (pose temporelle)",
                "size": "~8GB",
                "use_case": "✅ Action recognition, sports motion analysis, video tracking",
                "tags": ["sports-video", "temporal-pose", "action-recognition"],
                "kaggle_id": "mshmarinov/sports-pose-dataset",
                "api_url": "https://www.kaggle.com/api/v1/datasets/download/mshmarinov/sports-pose-dataset"
            },
            
            "3dpw": {
                "name": "3D Poses in the Wild (3DPW)",
                "description": "500+ vidéos in-the-wild, SMPL body model 3D + vidéos",
                "category": "3d_body_model",
                "format": "MP4 + PKL (SMPL params: shape, pose, translation)",
                "joints": "24 SMPL joints + 3D mesh",
                "size": "~3.5GB",
                "use_case": "✅ Full body 3D, SMPL fitting, realistic body animation",
                "tags": ["smpl", "3d-body", "in-the-wild", "mesh"],
                "kaggle_id": "linhuanhuang/3dpw",
                "api_url": "https://www.kaggle.com/api/v1/datasets/download/linhuanhuang/3dpw"
            },
            
            "penn_action": {
                "name": "Penn Action Dataset",
                "description": "2.5K vidéos 13 actions (golf, tennis, baseball...) avec pose",
                "category": "action_video",
                "format": "AVI/MP4 vidéos + MAT skeleton",
                "joints": "13 (full body pose)",
                "size": "~2.3GB",
                "use_case": "✅ Action recognition, sports pose, motion classification",
                "tags": ["action-video", "sports", "pose-tracking"],
                "kaggle_id": "yichenw/penn-action-dataset",
                "api_url": "https://www.kaggle.com/api/v1/datasets/download/yichenw/penn-action-dataset"
            },

            "skeleton_data_samples": {
                "name": "Skeleton Walking/Running Data",
                "description": "Données skeleton brutes (marche, course, mouvements)",
                "category": "skeleton_motion",
                "format": "CSV skeleton coordinates (30fps)",
                "joints": "15-25 joints par frame",
                "size": "~500MB",
                "use_case": "✅ Motion retargeting, animation blending, gait analysis",
                "tags": ["skeleton", "motion-data", "csv"],
                "kaggle_id": "ykhli/skeleton-training-data",
                "api_url": "https://www.kaggle.com/api/v1/datasets/download/ykhli/skeleton-training-data"
            }
        }
        
        self.download_log = self.base_path / "download_log.json"
        self.load_download_status()
    
    def load_download_status(self):
        if self.download_log.exists():
            with open(self.download_log) as f:
                self.status = json.load(f)
        else:
            self.status = {}
    
    def save_download_status(self):
        with open(self.download_log, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def download_dataset(self, dataset_key: str, force: bool = False) -> bool:
        """Télécharge via urllib avec authentification"""
        if dataset_key not in self.datasets:
            print(f"❌ Dataset '{dataset_key}' non trouvé")
            return False
        
        info = self.datasets[dataset_key]
        dataset_path = self.base_path / dataset_key
        
        if dataset_path.exists() and not force:
            files_count = sum(1 for _ in dataset_path.rglob('*') if _.is_file())
            if files_count > 0:
                print(f"⏭️  {dataset_key} déjà téléchargé ({files_count} fichiers)")
                self.status[dataset_key] = "already_downloaded"
                return True
        
        print(f"\n{'='*70}")
        print(f"📥 {info['name']}")
        print(f"{'='*70}")
        print(f"Format: {info['format']}")
        print(f"Joints: {info['joints']}")
        print(f"Taille: {info['size']}")
        print(f"Use case: {info['use_case']}")
        
        try:
            dataset_path.mkdir(parents=True, exist_ok=True)
            
            # Authentification
            credentials = f"{self.username}:{self.api_key}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode('ascii')
            
            url = info['api_url']
            req = Request(url)
            req.add_header('Authorization', f'Basic {encoded_credentials}')
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            zip_path = dataset_path / f"{dataset_key}.zip"
            
            print(f"\n⬇️  Téléchargement...")
            
            with urlopen(req, timeout=30) as response:
                total_size = response.headers.get('content-length')
                if total_size:
                    total_mb = int(total_size) / (1024*1024)
                    print(f"   Taille réelle: {total_mb:.2f} MB")
                
                downloaded = 0
                with open(zip_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = (downloaded / int(total_size)) * 100
                            print(f"   Progression: {percent:.1f}%", end='\r')
            
            print(f"\n✅ Téléchargement terminé")
            
            # Extraction
            print(f"🔓 Extraction du ZIP...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(dataset_path)
            
            zip_path.unlink()
            
            files_count = sum(1 for _ in dataset_path.rglob('*') if _.is_file())
            self.status[dataset_key] = f"downloaded_{datetime.now().isoformat()}"
            print(f"✅ {dataset_key}: {files_count} fichiers extraits\n")
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {str(e)[:150]}")
            self.status[dataset_key] = "failed"
            return False
    
    def download_all(self, exclude: list = None, force: bool = False):
        exclude = exclude or []
        total = len(self.datasets) - len(exclude)
        success = 0
        failed = 0
        
        print(f"\n{'='*80}")
        print(f"🚀 TÉLÉCHARGEMENT DATASETS MOTION CAPTURE")
        print(f"{'='*80}\n")
        print(f"Total: {total} datasets")
        print(f"Espace estimé: ~170GB (tous)\n")
        
        for i, (dataset_key, info) in enumerate(self.datasets.items(), 1):
            if dataset_key in exclude:
                print(f"\n[{i}/{len(self.datasets)}] ⏭️  {dataset_key} (exclu)")
                continue
            
            print(f"\n[{i}/{len(self.datasets)}]...")
            if self.download_dataset(dataset_key, force):
                success += 1
            else:
                failed += 1
        
        self.save_download_status()
        
        print(f"\n{'='*80}")
        print(f"✅ RÉSUMÉ: {success}/{total} datasets téléchargés")
        if failed > 0:
            print(f"⚠️  Erreurs: {failed}")
        print(f"📁 Dossier: {self.base_path.absolute()}")
        print(f"{'='*80}\n")
    
    def list_datasets(self):
        print("\n" + "="*90)
        print("📊 DATASETS MOTION CAPTURE - PRÊTS POUR ANIMATION 3D")
        print("="*90)
        
        categories = {}
        for key, info in self.datasets.items():
            cat = info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((key, info))
        
        for category in sorted(categories.keys()):
            print(f"\n📂 {category.upper().replace('_', ' ')}")
            print("-" * 90)
            for key, info in categories[category]:
                status = self.status.get(key, "not_downloaded")
                status_icon = "✅" if "downloaded" in status else "⬜"
                print(f"{status_icon} {key}")
                print(f"   Nom: {info['name']}")
                print(f"   Format: {info['format']} | Joints: {info['joints']}")
                print(f"   Taille: {info['size']}")
                print(f"   {info['use_case']}\n")
    
    def get_stats(self):
        print("\n" + "="*80)
        print("📈 STATISTIQUES TÉLÉCHARGEMENT")
        print("="*80)
        
        total_size = 0
        total_files = 0
        downloaded = 0
        
        for dataset_key in self.datasets.keys():
            dataset_path = self.base_path / dataset_key
            if dataset_path.exists():
                downloaded += 1
                size = sum(f.stat().st_size for f in dataset_path.rglob('*') if f.is_file())
                files = sum(1 for f in dataset_path.rglob('*') if f.is_file())
                total_size += size
                total_files += files
                print(f"\n✅ {dataset_key}")
                print(f"   Taille: {size / (1024*1024):.2f} MB | Fichiers: {files}")
        
        print(f"\n{'='*80}")
        print(f"FINAL: {downloaded}/{len(self.datasets)} datasets")
        print(f"Taille totale: {total_size / (1024*1024*1024):.2f} GB")
        print(f"Fichiers: {total_files}")
        print(f"{'='*80}\n")


def main():
    print("\n" + "="*80)
    print("🎬 MOTION CAPTURE DATASETS COLLECTOR v5.1")
    print("="*80)
    print("📌 Datasets vidéo + skeleton pour animation 3D")
    print("="*80 + "\n")
    
    collector = MotionCaptureDatasetCollector(base_path="./motion_capture_data")
    collector.list_datasets()
    
    print("\n" + "="*80)
    print("INSTRUCTIONS D'UTILISATION:")
    print("="*80)
    print("""
1. Lancez: python data.py
2. Choisissez les datasets à télécharger (exclure les gros si vous avez peu de place)
3. Exemple:
   - collector.download_all(exclude=['human3_6m'])  # Skip gros dataset
   - collector.download_all()  # Tous les datasets

💡 CONSEIL: Commencez par COCO ou Penn Action (plus petits, très utiles)
    """)
    
    print("\n" + "="*80)
    print("🚀 TÉLÉCHARGEMENT")
    print("="*80 + "\n")
    
    # ⭐ À modifier selon vos besoins:
    # Excluez les gros datasets si vous n'avez pas assez d'espace
    collector.download_all(exclude=['human3_6m'])  # Skip 150GB dataset
    
    collector.get_stats()


if __name__ == "__main__":
    print("="*80)
    print("🔧 DÉPENDANCES MINIMALES")
    print("="*80 + "\n")
    
    for package in ["pandas", "numpy"]:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"📦 Installation {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
            print(f"✅ {package} installé")
    
    print("\n✅ 100% OPENSOURCE - Prêt!\n")
    main()