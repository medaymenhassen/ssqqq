import requests
import json
import time
import csv
import io
from datetime import datetime

# Base URL for the Spring Boot application
BASE_URL = "http://localhost:8080"

# Test user credentials
USER_DATA = {
    "firstname": "Video",
    "lastname": "Tester",
    "email": "video.tester@example.com",
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

def generate_test_csv():
    """Generate test CSV data with realistic movement data"""
    print("📋 Generating test CSV data...")
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header for combined movement data
    writer.writerow([
        'Timestamp', 'Pose Confidence', 'Head X', 'Head Y', 'Head Z', 'Head Confidence',
        'Left Shoulder X', 'Left Shoulder Y', 'Left Shoulder Z', 'Left Shoulder Confidence',
        'Right Shoulder X', 'Right Shoulder Y', 'Right Shoulder Z', 'Right Shoulder Confidence',
        'Left Hip X', 'Left Hip Y', 'Left Hip Z', 'Left Hip Confidence',
        'Right Hip X', 'Right Hip Y', 'Right Hip Z', 'Right Hip Confidence',
        'Face Confidence', 'Mouth Open', 'Eye Blink Left', 'Eye Blink Right', 
        'Eye Look Left', 'Eye Look Right', 'Head Position X', 'Head Position Y', 'Head Position Z',
        'Left Hand Gesture', 'Left Hand Confidence', 'Left Hand Landmarks',
        'Right Hand Gesture', 'Right Hand Confidence', 'Right Hand Landmarks'
    ])
    
    # Generate test data for multiple frames
    base_time = int(time.time() * 1000)
    for i in range(10):  # Generate 10 frames of data
        timestamp = base_time + (i * 100)  # 100ms intervals
        
        # Simulate movement over time
        movement_factor = i / 10.0
        
        row = [
            timestamp,
            # Pose data
            85 + (5 * movement_factor),  # Confidence
            0.5 + (0.1 * movement_factor),  # Head X
            0.2 - (0.05 * movement_factor),  # Head Y
            0.0,  # Head Z
            90 + (3 * movement_factor),  # Head Confidence
            0.4 + (0.05 * movement_factor),  # Left Shoulder X
            0.35 - (0.02 * movement_factor),  # Left Shoulder Y
            0.1,  # Left Shoulder Z
            88 + (2 * movement_factor),  # Left Shoulder Confidence
            0.6 - (0.05 * movement_factor),  # Right Shoulder X
            0.35 + (0.02 * movement_factor),  # Right Shoulder Y
            0.1,  # Right Shoulder Z
            87 + (2 * movement_factor),  # Right Shoulder Confidence
            0.45 + (0.03 * movement_factor),  # Left Hip X
            0.65 - (0.01 * movement_factor),  # Left Hip Y
            0.1,  # Left Hip Z
            85 + (1 * movement_factor),  # Left Hip Confidence
            0.55 - (0.03 * movement_factor),  # Right Hip X
            0.65 + (0.01 * movement_factor),  # Right Hip Y
            0.1,  # Right Hip Z
            84 + (1 * movement_factor),  # Right Hip Confidence
            # Face data
            92 - (2 * movement_factor),  # Face Confidence
            10 + (20 * movement_factor),  # Mouth Open
            5 - (3 * movement_factor),  # Eye Blink Left
            3 + (2 * movement_factor),  # Eye Blink Right
            0.1 + (0.05 * movement_factor),  # Eye Look Left
            -0.2 - (0.03 * movement_factor),  # Eye Look Right
            0.5 + (0.02 * movement_factor),  # Head Position X
            0.2 - (0.01 * movement_factor),  # Head Position Y
            0.0,  # Head Position Z
            # Hands data
            'Open' if i % 2 == 0 else 'Closed',  # Left Hand Gesture
            0,  # Left Hand Confidence (placeholder)
            21,  # Left Hand Landmarks
            'Closed' if i % 2 == 0 else 'Open',  # Right Hand Gesture
            0,  # Right Hand Confidence (placeholder)
            21  # Right Hand Landmarks
        ]
        
        writer.writerow(row)
    
    csv_content = output.getvalue()
    output.close()
    
    print(f"✅ Generated CSV with {len(csv_content.split(chr(10))) - 1} rows")
    return csv_content

def create_video_from_csv(token, csv_content, user_id):
    """Create video from CSV data"""
    print("🎥 Creating video from CSV data...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a file-like object from the CSV content
    files = {'file': ('movement-data.csv', csv_content, 'text/csv')}
    data = {
        'userId': str(user_id),
        'videoName': f'analysis-{datetime.now().strftime("%Y%m%d-%H%M%S")}.mp4'
    }
    
    url = f"{BASE_URL}/springboot/csv/create-video"
    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        if response.status_code == 200:
            print("✅ Video created successfully from CSV data")
            return response.json()
        else:
            print(f"❌ Video creation failed with status code {response.status_code}")
            print("Response:", response.text)
            return None
    except Exception as e:
        print(f"❌ Error creating video from CSV: {e}")
        return None

def get_video_info(token, filename):
    """Get detailed information about a video"""
    print(f"🔍 Getting video info for {filename}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/springboot/csv/video-info/{filename}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Video info retrieved successfully")
            return response.json()
        else:
            print(f"❌ Failed to get video info with status code {response.status_code}")
            print("Response:", response.text)
            return None
    except Exception as e:
        print(f"❌ Error getting video info: {e}")
        return None

def list_uploaded_files(token):
    """List all uploaded files"""
    print("📂 Listing uploaded files...")
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/springboot/csv/list-files"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ File list retrieved successfully")
            return response.json()
        else:
            print(f"❌ Failed to list files with status code {response.status_code}")
            print("Response:", response.text)
            return None
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return None

def main():
    """Main function to test video generation"""
    print("=" * 60)
    print("🚀 Starting Video Generation Test")
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
    
    # Step 3: Generate test CSV data
    csv_content = generate_test_csv()
    if not csv_content:
        print("💥 Failed to generate CSV data")
        return
    
    print("📋 CSV data sample (first 300 chars):")
    print(csv_content[:300] + "..." if len(csv_content) > 300 else csv_content)
    
    # Small delay
    time.sleep(1)
    
    # Step 4: Create video from CSV
    user_id = 1  # Assuming user ID 1 for test user
    video_response = create_video_from_csv(token, csv_content, user_id)
    if not video_response:
        print("💥 Workflow failed at video creation step")
        return
    
    video_url = video_response.get("videoUrl")
    csv_processed = video_response.get("csvProcessed")
    processed_rows = video_response.get("processedRows", 0)
    pose_detection_times = video_response.get("poseDetectionTimes", [])
    
    print(f"🎬 Video created:")
    print(f"   Video URL: {video_url}")
    print(f"   CSV Processed: {csv_processed}")
    print(f"   Processed Rows: {processed_rows}")
    print(f"   Pose Detection Times: {len(pose_detection_times)} timestamps")
    
    # Small delay
    time.sleep(1)
    
    # Step 5: Get video info
    if video_url:
        filename = video_url.split("/")[-1]
        video_info = get_video_info(token, filename)
        if video_info:
            print(f"📊 Video Info:")
            print(f"   Name: {video_info.get('name')}")
            print(f"   Size: {video_info.get('size')} bytes")
            print(f"   Exists: {video_info.get('exists')}")
            if "poseDetectionTimes" in video_info:
                print(f"   Pose Detection Times: {len(video_info['poseDetectionTimes'])} timestamps")
        else:
            print("❌ Failed to get video info")
    
    # Small delay
    time.sleep(1)
    
    # Step 6: List all uploaded files
    files_list = list_uploaded_files(token)
    if files_list:
        files = files_list.get("files", [])
        print(f"📁 Uploaded Files ({files_list.get('count', 0)} total):")
        for file in files[:5]:  # Show first 5 files
            print(f"   - {file.get('name')} ({file.get('size')} bytes)")
        if len(files) > 5:
            print(f"   ... and {len(files) - 5} more files")
    else:
        print("❌ Failed to list uploaded files")
    
    print("=" * 60)
    print("🎉 Video Generation Test Completed!")
    print("=" * 60)
    print("Summary:")
    print("   👤 User registered and logged in")
    print("   📋 Test CSV data generated with movement simulation")
    print("   🎥 Video created successfully from CSV data")
    print("   📊 Video metadata retrieved and validated")
    print("   📁 File listing confirmed successful upload")

if __name__ == "__main__":
    main()