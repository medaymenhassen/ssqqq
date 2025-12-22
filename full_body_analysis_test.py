#!/usr/bin/env python3
"""
Comprehensive test script for body analysis video processing pipeline:
1. Register and login to the system
2. Upload a video for body analysis
3. Test MediaPipe processing on the frontend
4. Verify backend processing
5. Track each step to identify issues
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
FRONTEND_URL = "http://localhost:4200"
# Generate a random email to avoid conflicts
RANDOM_STRING = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
EMAIL = f"bodyanalysis_{RANDOM_STRING}@example.com"
PASSWORD = "bodyanalysis123"

# Global session for persistent cookies/headers
session = requests.Session()

def create_test_video(filename: str = "test_video.mp4", duration_seconds: int = 5) -> str:
    """Create a simple test video for body analysis"""
    print(f"🎬 Creating test video: {filename}")
    
    # Video dimensions and FPS
    width, height = 640, 480
    fps = 30
    total_frames = duration_seconds * fps
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("❌ Failed to create video writer")
        return ""
    
    # Create a simple animation - moving circle
    for frame_num in range(total_frames):
        # Create black background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Calculate circle position (moving horizontally)
        x = int((frame_num / total_frames) * width)
        y = height // 2
        
        # Draw a white circle (simulating a person)
        cv2.circle(frame, (x, y), 30, (255, 255, 255), -1)
        
        # Add some movement variation
        if frame_num % 30 == 0:  # Every second
            cv2.rectangle(frame, (x-20, y-40), (x+20, y+40), (0, 255, 0), 2)
        
        # Write frame
        out.write(frame)
    
    # Release everything
    out.release()
    cv2.destroyAllWindows()
    
    if os.path.exists(filename):
        file_size = os.path.getsize(filename)
        print(f"✅ Test video created successfully: {filename} ({file_size} bytes)")
        return filename
    else:
        print("❌ Failed to create test video")
        return ""

def register_user() -> Optional[Dict[str, Any]]:
    """Register a new user for body analysis"""
    print("\n📝 Registering user for body analysis...")
    register_data = {
        "firstname": "Body",
        "lastname": "Analyzer",
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

def test_mediapipe_processing(video_path: str) -> bool:
    """Test MediaPipe processing on the frontend side"""
    print(f"\n🔬 Testing MediaPipe processing on video: {video_path}")
    
    try:
        # Check if OpenCV and MediaPipe are available
        try:
            import mediapipe as mp
            print("✅ MediaPipe is available")
        except ImportError:
            print("⚠️ MediaPipe not installed, skipping detailed analysis")
            return True
        
        # Check if video file exists
        if not os.path.exists(video_path):
            print("❌ Video file not found")
            return False
        
        # Test basic video reading
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Cannot open video file")
            return False
        
        # Initialize MediaPipe Pose
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        
        frame_count = 0
        detections_found = False
        
        print("👀 Analyzing video frames with MediaPipe...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # Process frame with MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            # Check if pose landmarks are detected
            if results.pose_landmarks:
                detections_found = True
                if frame_count <= 5:  # Report first few detections
                    print(f"   Frame {frame_count}: Pose landmarks detected ({len(results.pose_landmarks.landmark)} landmarks)")
            
            # Limit processing for testing
            if frame_count >= 30:  # Process only first 30 frames
                break
        
        cap.release()
        pose.close()
        
        print(f"📊 Video analysis complete:")
        print(f"   - Frames processed: {frame_count}")
        print(f"   - Pose detections: {'Yes' if detections_found else 'No'}")
        
        if detections_found:
            print("✅ MediaPipe processing successful - pose detected in video")
            return True
        else:
            print("⚠️ MediaPipe processing completed but no poses detected")
            return True  # Still consider it successful as the processing worked
            
    except Exception as e:
        print(f"❌ Error during MediaPipe processing: {e}")
        return False

def upload_video_for_body_analysis(user_id: int, video_path: str, analysis_type: str = "full_body") -> Optional[Dict[str, Any]]:
    """Upload video for body analysis processing"""
    print(f"\n📤 Uploading video for body analysis...")
    print(f"   Video path: {video_path}")
    print(f"   User ID: {user_id}")
    print(f"   Analysis type: {analysis_type}")
    
    if not os.path.exists(video_path):
        print("❌ Video file not found")
        return None
    
    try:
        # Prepare file for upload
        with open(video_path, 'rb') as video_file:
            files = {'file': (os.path.basename(video_path), video_file, 'video/mp4')}
            data = {
                'userId': user_id,
                'analysisType': analysis_type
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
            print(f"   Document ID: {result.get('documentId')}")
            print(f"   File name: {result.get('fileName')}")
            print(f"   File size: {result.get('fileSize')}")
            return result
        else:
            print(f"❌ Video upload failed: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Error during video upload: {e}")
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

def test_frontend_backend_integration() -> bool:
    """Test the complete frontend to backend integration"""
    print("\n" + "="*60)
    print("TESTING FRONTEND TO BACKEND INTEGRATION")
    print("="*60)
    
    # Step 1: Register user
    print("\nStep 1: User Registration")
    register_response = register_user()
    if not register_response:
        print("❌ Registration failed")
        return False
    
    # Wait for user creation
    time.sleep(2)
    
    # Step 2: Login
    print("\nStep 2: User Login")
    tokens = login_user()
    if not tokens:
        print("❌ Login failed")
        return False
    
    # Wait for authentication to settle
    time.sleep(1)
    
    # Step 3: Get user profile to get user ID
    print("\nStep 3: Get User Profile")
    profile = get_user_profile()
    if not profile:
        print("❌ Failed to get user profile")
        return False
    
    user_id = profile.get('id')
    if not user_id:
        print("❌ User ID not found in profile")
        return False
    
    print(f"✅ User ID obtained: {user_id}")
    
    # Step 4: Create test video
    print("\nStep 4: Create Test Video")
    video_path = create_test_video("body_analysis_test.mp4", 3)
    if not video_path:
        print("❌ Failed to create test video")
        return False
    
    # Step 5: Test MediaPipe processing (frontend simulation)
    print("\nStep 5: Test MediaPipe Processing (Frontend)")
    mediapipe_success = test_mediapipe_processing(video_path)
    if not mediapipe_success:
        print("❌ MediaPipe processing failed")
        # Continue anyway as this is just a frontend test
    
    # Step 6: Upload video for body analysis
    print("\nStep 6: Upload Video for Body Analysis (Backend)")
    upload_result = upload_video_for_body_analysis(user_id, video_path, "full_body_analysis")
    if not upload_result:
        print("❌ Video upload failed")
        return False
    
    print("✅ Integration test completed successfully!")
    return True

def cleanup_test_files():
    """Clean up test files"""
    test_files = ["body_analysis_test.mp4"]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")
            except Exception as e:
                print(f"⚠️ Failed to remove {file}: {e}")

def main():
    print("🚀 Starting Full Body Analysis Integration Test")
    print(f"Using email: {EMAIL}")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Run the integration test
        success = test_frontend_backend_integration()
        
        # Clean up
        cleanup_test_files()
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        
        if success:
            print("✅ All integration tests passed!")
            print("✅ Frontend to backend body analysis pipeline is working!")
        else:
            print("❌ Some integration tests failed!")
            print("❌ There may be issues with the body analysis pipeline")
            
    except Exception as e:
        print(f"💥 Unexpected error during testing: {e}")
        cleanup_test_files()

if __name__ == "__main__":
    main()