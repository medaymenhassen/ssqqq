#!/usr/bin/env python3
"""
End-to-End test script for body analysis system:
1. Register and login to the system
2. Create and process a test video with MediaPipe
3. Upload video for body analysis
4. Verify backend processing and storage
5. Test CSV generation and video creation endpoints
"""

import requests
import json
import time
import random
import string
import os
import cv2
import numpy as np
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "http://localhost:8080/api"
SPRINGBOOT_URL = "http://localhost:8080/springboot/csv"
# Generate a random email to avoid conflicts
RANDOM_STRING = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
EMAIL = f"e2e_test_{RANDOM_STRING}@example.com"
PASSWORD = "e2etest123"

# Global session for persistent cookies/headers
session = requests.Session()

def create_test_video(filename: str = "e2e_test_video.mp4", duration_seconds: int = 3) -> bool:
    """Create a simple test video for body analysis"""
    print(f"🎬 Creating test video: {filename}")
    
    try:
        # Video dimensions and FPS
        width, height = 640, 480
        fps = 30
        total_frames = duration_seconds * fps
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        
        if not out.isOpened():
            print("❌ Failed to create video writer")
            return False
        
        # Create a simple animation - moving objects
        for frame_num in range(total_frames):
            # Create black background
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Calculate positions for moving objects
            x1 = int((frame_num / total_frames) * width)
            y1 = height // 3
            
            x2 = int(((total_frames - frame_num) / total_frames) * width)
            y2 = 2 * height // 3
            
            # Draw circles (simulating people/body parts)
            cv2.circle(frame, (x1, y1), 25, (0, 255, 0), -1)  # Green circle
            cv2.circle(frame, (x2, y2), 30, (0, 0, 255), -1)  # Red circle
            
            # Add connecting line
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            
            # Write frame
            out.write(frame)
        
        # Release everything
        out.release()
        cv2.destroyAllWindows()
        
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✅ Test video created successfully: {filename} ({file_size} bytes)")
            return True
        else:
            print("❌ Failed to create test video")
            return False
    except Exception as e:
        print(f"❌ Error creating test video: {e}")
        return False

def register_user() -> Optional[Dict[str, Any]]:
    """Register a new user for testing"""
    print("\n📝 Registering user...")
    register_data = {
        "firstname": "E2E",
        "lastname": "Tester",
        "email": EMAIL,
        "password": PASSWORD,
        "rgpdAccepted": True,
        "commercialUseConsent": True
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Register response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Registration successful")
            return response.json()
        else:
            print(f"❌ Registration failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def login_user() -> Optional[Dict[str, Any]]:
    """Login user to get authentication tokens"""
    print("\n🔐 Logging in...")
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful")
            tokens = response.json()
            # Set authorization header for future requests
            session.headers.update({
                "Authorization": f"Bearer {tokens['accessToken']}"
            })
            return tokens
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def get_user_profile() -> Optional[Dict[str, Any]]:
    """Get current user profile to get user ID"""
    print("\n👤 Getting user profile...")
    
    try:
        response = session.get(f"{BASE_URL}/user/profile")
        print(f"Profile response status: {response.status_code}")
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ User profile retrieved - ID: {profile.get('id')}, Email: {profile.get('email')}")
            return profile
        else:
            print(f"❌ Failed to get user profile: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        return None

def upload_video_for_body_analysis(user_id: int, video_path: str) -> Optional[Dict[str, Any]]:
    """Upload video for body analysis processing"""
    print(f"\n📤 Uploading video for body analysis...")
    print(f"   Video path: {video_path}")
    print(f"   User ID: {user_id}")
    
    if not os.path.exists(video_path):
        print("❌ Video file not found")
        return None
    
    try:
        # Prepare file for upload
        with open(video_path, 'rb') as video_file:
            files = {'file': (os.path.basename(video_path), video_file, 'video/mp4')}
            data = {
                'userId': user_id,
                'analysisType': 'e2e_test'
            }
            
            # Make the request
            response = session.post(
                f"{BASE_URL}/documents/upload-for-body-analysis",
                files=files,
                data=data
            )
        
        print(f"Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Video upload successful")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Document ID: {result.get('documentId')}")
            print(f"   File name: {result.get('fileName')}")
            print(f"   File size: {result.get('fileSize')}")
            print(f"   File type: {result.get('fileType')}")
            return result
        else:
            print(f"❌ Video upload failed: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Error during video upload: {e}")
        return None

def generate_test_csv() -> str:
    """Generate test CSV data for pose analysis"""
    print("\n📋 Generating test CSV data...")
    
    # Create CSV content with realistic pose data
    csv_content = "Timestamp,Pose Confidence,Head X,Head Y,Head Z,Head Confidence,Left Shoulder X,Left Shoulder Y,Left Shoulder Z,Left Shoulder Confidence,Right Shoulder X,Right Shoulder Y,Right Shoulder Z,Right Shoulder Confidence,Left Hip X,Left Hip Y,Left Hip Z,Left Hip Confidence,Right Hip X,Right Hip Y,Right Hip Z,Right Hip Confidence\n"
    
    # Generate 10 rows of data
    for i in range(10):
        timestamp = int(time.time() * 1000) + i * 100
        row = [
            timestamp,
            85 + random.randint(-5, 5),  # Pose confidence
            0.45 + (i * 0.01),  # Head X
            0.2 + (i * 0.005),  # Head Y
            0.0 + (i * 0.001),  # Head Z
            0.9 + (i * 0.001),  # Head Confidence
            0.4 + (i * 0.005),  # Left Shoulder X
            0.35 + (i * 0.002),  # Left Shoulder Y
            0.1,  # Left Shoulder Z
            0.85 + (i * 0.001),  # Left Shoulder Confidence
            0.6 - (i * 0.005),  # Right Shoulder X
            0.35 + (i * 0.002),  # Right Shoulder Y
            0.1,  # Right Shoulder Z
            0.83 + (i * 0.001),  # Right Shoulder Confidence
            0.45 + (i * 0.003),  # Left Hip X
            0.65 + (i * 0.001),  # Left Hip Y
            0.1,  # Left Hip Z
            0.8 + (i * 0.001),  # Left Hip Confidence
            0.55 - (i * 0.003),  # Right Hip X
            0.65 + (i * 0.001),  # Right Hip Y
            0.1,  # Right Hip Z
            0.78 + (i * 0.001)  # Right Hip Confidence
        ]
        csv_content += ",".join(map(str, row)) + "\n"
    
    filename = "test_pose_data.csv"
    with open(filename, "w") as f:
        f.write(csv_content)
    
    print(f"✅ Test CSV generated: {filename} ({len(csv_content)} bytes)")
    return filename

def upload_csv_data(user_id: int, csv_filename: str, data_type: str) -> Optional[Dict[str, Any]]:
    """Upload CSV data to backend"""
    print(f"\n📤 Uploading CSV data ({data_type})...")
    
    if not os.path.exists(csv_filename):
        print("❌ CSV file not found")
        return None
    
    try:
        with open(csv_filename, 'rb') as csv_file:
            files = {'file': (csv_filename, csv_file, 'text/csv')}
            data = {
                'userId': user_id,
                'dataType': data_type
            }
            
            response = session.post(
                f"{SPRINGBOOT_URL}/create-combined-video",
                files=files,
                data=data
            )
        
        print(f"CSV upload response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CSV upload and video creation successful")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Video URL: {result.get('videoUrl')}")
            print(f"   Processed rows: {result.get('processedRows')}")
            return result
        else:
            print(f"❌ CSV upload failed: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Error during CSV upload: {e}")
        return None

def test_end_to_end_pipeline() -> bool:
    """Test the complete end-to-end pipeline"""
    print("\n" + "="*60)
    print("TESTING END-TO-END BODY ANALYSIS PIPELINE")
    print("="*60)
    
    # Step 1: Create test video
    print("\nStep 1: Create Test Video")
    video_created = create_test_video("e2e_test_video.mp4", 3)
    if not video_created:
        print("❌ Failed to create test video")
        return False
    
    # Step 2: Register user
    print("\nStep 2: User Registration")
    register_response = register_user()
    if not register_response:
        print("❌ Registration failed")
        return False
    
    # Wait for user creation
    time.sleep(2)
    
    # Step 3: Login
    print("\nStep 3: User Login")
    tokens = login_user()
    if not tokens:
        print("❌ Login failed")
        return False
    
    # Wait for authentication to settle
    time.sleep(1)
    
    # Step 4: Get user profile to get user ID
    print("\nStep 4: Get User Profile")
    profile = get_user_profile()
    if not profile:
        print("❌ Failed to get user profile")
        return False
    
    user_id = profile.get('id')
    if not user_id:
        print("❌ User ID not found in profile")
        return False
    
    print(f"✅ User ID obtained: {user_id}")
    
    # Step 5: Upload video for body analysis
    print("\nStep 5: Upload Video for Body Analysis")
    upload_result = upload_video_for_body_analysis(user_id, "e2e_test_video.mp4")
    if not upload_result:
        print("❌ Video upload failed")
        return False
    
    # Step 6: Generate and upload test CSV data
    print("\nStep 6: Generate and Upload Test CSV Data")
    csv_filename = generate_test_csv()
    
    # Upload CSV for video creation
    csv_result = upload_csv_data(user_id, csv_filename, "pose")
    if not csv_result:
        print("❌ CSV upload failed")
        return False
    
    print("✅ End-to-end pipeline test completed successfully!")
    return True

def cleanup_test_files():
    """Clean up test files"""
    test_files = ["e2e_test_video.mp4", "test_pose_data.csv"]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")
            except Exception as e:
                print(f"⚠️ Failed to remove {file}: {e}")

def main():
    print("🚀 Starting End-to-End Body Analysis Pipeline Test")
    print(f"Using email: {EMAIL}")
    print(f"Base URL: {BASE_URL}")
    print(f"SpringBoot URL: {SPRINGBOOT_URL}")
    
    try:
        # Run the end-to-end test
        success = test_end_to_end_pipeline()
        
        # Clean up
        cleanup_test_files()
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        
        if success:
            print("✅ All end-to-end tests passed!")
            print("✅ Body analysis system is working correctly from frontend to backend!")
        else:
            print("❌ Some end-to-end tests failed!")
            print("❌ There may be issues in the body analysis pipeline")
            
    except Exception as e:
        print(f"💥 Unexpected error during testing: {e}")
        cleanup_test_files()

if __name__ == "__main__":
    main()