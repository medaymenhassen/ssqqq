import requests
import json
import time
import csv
import io
from datetime import datetime

# Base URL for the Spring Boot application
BASE_URL = "http://localhost:8080"

# User credentials (using timestamp to ensure unique email)
import time
timestamp = int(time.time())
USER_DATA = {
    "firstname": "Image",
    "lastname": "Analyzer",
    "email": f"image.analyzer.{timestamp}@example.com",
    "password": "password123",
    "rgpdAccepted": True,
    "ccpaAccepted": False
}
def register_user():
    """Register a new user"""
    print("📝 Registering user...")
    url = f"{BASE_URL}/api/auth/register"
    response = requests.post(url, json=USER_DATA)
    
    if response.status_code == 200:
        print("✅ User registered successfully")
        return response.json()
    else:
        print(f"❌ Registration failed with status code {response.status_code}")
        print(response.text)
        return None

def login_user():
    """Log in the user"""
    print("🔐 Logging in user...")
    login_data = {
        "email": USER_DATA["email"],
        "password": USER_DATA["password"]
    }
    url = f"{BASE_URL}/api/auth/login"
    response = requests.post(url, json=login_data)
    
    if response.status_code == 200:
        print("✅ User logged in successfully")
        return response.json()
    else:
        print(f"❌ Login failed with status code {response.status_code}")
        print(response.text)
        return None

def simulate_body_analysis():
    """Simulate body analysis from the provided image"""
    print("🔍 Simulating body analysis from image...")
    
    # Generate simulated pose data
    pose_data = [
        {"part": "Head", "x": 0.5, "y": 0.2, "z": 0, "confidence": 0.95},
        {"part": "Neck", "x": 0.5, "y": 0.3, "z": 0, "confidence": 0.92},
        {"part": "LeftShoulder", "x": 0.4, "y": 0.35, "z": 0.1, "confidence": 0.88},
        {"part": "RightShoulder", "x": 0.6, "y": 0.35, "z": 0.1, "confidence": 0.87},
        {"part": "LeftElbow", "x": 0.35, "y": 0.5, "z": 0.2, "confidence": 0.85},
        {"part": "RightElbow", "x": 0.65, "y": 0.5, "z": 0.2, "confidence": 0.83},
        {"part": "LeftWrist", "x": 0.3, "y": 0.65, "z": 0.1, "confidence": 0.80},
        {"part": "RightWrist", "x": 0.7, "y": 0.65, "z": 0.1, "confidence": 0.78},
        {"part": "Hips", "x": 0.5, "y": 0.6, "z": 0, "confidence": 0.90},
        {"part": "LeftHip", "x": 0.45, "y": 0.65, "z": 0.1, "confidence": 0.85},
        {"part": "RightHip", "x": 0.55, "y": 0.65, "z": 0.1, "confidence": 0.84},
        {"part": "LeftKnee", "x": 0.45, "y": 0.8, "z": 0, "confidence": 0.80},
        {"part": "RightKnee", "x": 0.55, "y": 0.8, "z": 0, "confidence": 0.79},
        {"part": "LeftAnkle", "x": 0.45, "y": 0.95, "z": 0, "confidence": 0.75},
        {"part": "RightAnkle", "x": 0.55, "y": 0.95, "z": 0, "confidence": 0.73}
    ]
    
    # Generate simulated face data
    face_data = {
        "mouth_open": 15,
        "eye_blink_left": 5,
        "eye_blink_right": 3,
        "eye_look_left": 0.1,
        "eye_look_right": -0.2,
        "head_position": {"x": 0.5, "y": 0.2, "z": 0}
    }
    
    # Generate simulated hand data
    hand_data = {
        "left": {
            "gesture": "Open",
            "landmarks_count": 21
        },
        "right": {
            "gesture": "Closed",
            "landmarks_count": 21
        }
    }
    
    return {
        "pose": pose_data,
        "face": face_data,
        "hands": hand_data,
        "pose_confidence": 87,
        "face_confidence": 92,
        "hands_detected": {"left": True, "right": True}
    }

def generate_pose_csv(analysis):
    """Generate pose CSV data"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Timestamp', 'Pose Confidence', 'Head X', 'Head Y', 'Head Z', 'Head Confidence',
        'Left Shoulder X', 'Left Shoulder Y', 'Left Shoulder Z', 'Left Shoulder Confidence',
        'Right Shoulder X', 'Right Shoulder Y', 'Right Shoulder Z', 'Right Shoulder Confidence',
        'Left Hip X', 'Left Hip Y', 'Left Hip Z', 'Left Hip Confidence',
        'Right Hip X', 'Right Hip Y', 'Right Hip Z', 'Right Hip Confidence'
    ])
    
    # Data row
    timestamp = int(time.time() * 1000)
    pose = {item['part']: item for item in analysis['pose']}
    
    row = [
        timestamp,
        analysis['pose_confidence'],
        pose.get('Head', {}).get('x', 0),
        pose.get('Head', {}).get('y', 0),
        pose.get('Head', {}).get('z', 0),
        pose.get('Head', {}).get('confidence', 0),
        pose.get('LeftShoulder', {}).get('x', 0),
        pose.get('LeftShoulder', {}).get('y', 0),
        pose.get('LeftShoulder', {}).get('z', 0),
        pose.get('LeftShoulder', {}).get('confidence', 0),
        pose.get('RightShoulder', {}).get('x', 0),
        pose.get('RightShoulder', {}).get('y', 0),
        pose.get('RightShoulder', {}).get('z', 0),
        pose.get('RightShoulder', {}).get('confidence', 0),
        pose.get('LeftHip', {}).get('x', 0),
        pose.get('LeftHip', {}).get('y', 0),
        pose.get('LeftHip', {}).get('z', 0),
        pose.get('LeftHip', {}).get('confidence', 0),
        pose.get('RightHip', {}).get('x', 0),
        pose.get('RightHip', {}).get('y', 0),
        pose.get('RightHip', {}).get('z', 0),
        pose.get('RightHip', {}).get('confidence', 0)
    ]
    
    writer.writerow(row)
    return output.getvalue()

def generate_face_csv(analysis):
    """Generate face CSV data"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Timestamp', 'Face Confidence', 'Mouth Open', 'Eye Blink Left', 
        'Eye Blink Right', 'Eye Look Left', 'Eye Look Right', 
        'Head X', 'Head Y', 'Head Z'
    ])
    
    # Data row
    timestamp = int(time.time() * 1000)
    face = analysis['face']
    head_pos = face.get('head_position', {})
    
    row = [
        timestamp,
        analysis['face_confidence'],
        face.get('mouth_open', 0),
        face.get('eye_blink_left', 0),
        face.get('eye_blink_right', 0),
        face.get('eye_look_left', 0),
        face.get('eye_look_right', 0),
        head_pos.get('x', 0),
        head_pos.get('y', 0),
        head_pos.get('z', 0)
    ]
    
    writer.writerow(row)
    return output.getvalue()

def generate_hands_csv(analysis):
    """Generate hands CSV data"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Timestamp', 'Hand', 'Gesture', 'Confidence', 'Landmark Count'])
    
    # Data rows
    timestamp = int(time.time() * 1000)
    hands = analysis['hands']
    
    # Left hand
    if hands.get('left'):
        writer.writerow([
            timestamp,
            'Left',
            hands['left'].get('gesture', ''),
            0,  # Confidence not available
            hands['left'].get('landmarks_count', 0)
        ])
    
    # Right hand
    if hands.get('right'):
        writer.writerow([
            timestamp,
            'Right',
            hands['right'].get('gesture', ''),
            0,  # Confidence not available
            hands['right'].get('landmarks_count', 0)
        ])
    
    return output.getvalue()

def upload_csv_to_backend(token, csv_content, data_type, user_id):
    """Upload CSV data to the backend"""
    print(f"📤 Uploading {data_type} CSV data to backend...")
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {'file': (f'{data_type}-data.csv', csv_content, 'text/csv')}
    data = {'userId': user_id, 'dataType': data_type}
    
    url = f"{BASE_URL}/api/upload/csv"
    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        if response.status_code == 200:
            print(f"✅ {data_type.capitalize()} CSV data uploaded successfully")
            return response.json()
        else:
            print(f"❌ {data_type.capitalize()} CSV upload failed with status code {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error uploading {data_type} CSV: {e}")
        return None

def create_video_from_csv(token, csv_content, user_id):
    """Create video from CSV data"""
    print("🎥 Creating video from CSV data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {'file': ('movement-data.csv', csv_content, 'text/csv')}
    data = {'userId': user_id, 'videoName': f'analysis-{datetime.now().strftime("%Y%m%d-%H%M%S")}.mp4'}
    
    url = f"{BASE_URL}/api/csv-to-video"
    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        if response.status_code == 200:
            print("✅ Video created successfully from CSV data")
            return response.json()
        else:
            print(f"❌ Video creation failed with status code {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error creating video from CSV: {e}")
        return None

def main():
    """Main function to run the complete workflow"""
    print("=" * 60)
    print("🚀 Starting Image Body Analysis Workflow")
    print("=" * 60)
    
    # Step 1: Register user
    register_response = register_user()
    if not register_response:
        print("💥 Workflow failed at registration step")
        return
    
    # Small delay
    time.sleep(1)
    
    # Step 2: Login user
    login_response = login_user()
    if not login_response:
        print("💥 Workflow failed at login step")
        return
    
    token = login_response.get("accessToken")
    if not token:
        print("💥 No access token found in login response")
        return
    
    print(f"🔑 Access token obtained: {token[:20]}...")
    
    # Small delay
    time.sleep(1)
    
    # Step 3: Simulate body analysis from image
    analysis = simulate_body_analysis()
    if not analysis:
        print("💥 Workflow failed at analysis step")
        return
    
    print("📊 Body analysis completed")
    print(f"   Pose confidence: {analysis['pose_confidence']}%")
    print(f"   Face confidence: {analysis['face_confidence']}%")
    print(f"   Hands detected: {analysis['hands_detected']}")
    
    # Small delay
    time.sleep(1)
    
    # Step 4: Generate CSV data
    print("📋 Generating CSV data...")
    pose_csv = generate_pose_csv(analysis)
    face_csv = generate_face_csv(analysis)
    hands_csv = generate_hands_csv(analysis)
    
    print("✅ CSV data generated")
    
    # Small delay
    time.sleep(1)
    
    # Step 5: Upload CSV data (simulated - in a real app this would connect to backend)
    print("📤 Simulating CSV data upload...")
    print("   Note: In a real implementation, this would upload to the backend")
    print("   Pose CSV sample (first 200 chars):")
    print(f"   {pose_csv[:200]}...")
    print("   Face CSV sample (first 200 chars):")
    print(f"   {face_csv[:200]}...")
    print("   Hands CSV sample (first 200 chars):")
    print(f"   {hands_csv[:200]}...")
    
    # Small delay
    time.sleep(1)
    
    # Step 6: Create video from CSV (simulated)
    print("🎥 Simulating video creation from CSV...")
    print("   Note: In a real implementation, this would generate a video file")
    
    print("=" * 60)
    print("🎉 Image Body Analysis Workflow Completed Successfully!")
    print("=" * 60)
    print("Summary:")
    print("   👤 User registered and logged in")
    print("   🖼️ Image analyzed for body movements")
    print("   📊 Pose, face, and hands data extracted")
    print("   📋 CSV files generated for all data types")
    print("   🎥 Video creation simulated")
    print("")
    print("Next steps in a real implementation:")
    print("   1. Connect to actual backend endpoints")
    print("   2. Implement real image processing with MediaPipe")
    print("   3. Upload CSV files to backend storage")
    print("   4. Generate actual video files from movement data")

if __name__ == "__main__":
    main()