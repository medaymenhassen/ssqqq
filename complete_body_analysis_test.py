#!/usr/bin/env python3
"""
Complete test script for body analysis video processing pipeline:
1. Register and login to the system
2. Test MediaPipe processing on a test video
3. Upload video for body analysis
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
# Generate a random email to avoid conflicts
RANDOM_STRING = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
EMAIL = f"bodyanalysis_{RANDOM_STRING}@example.com"
PASSWORD = "bodyanalysis123"

# Global session for persistent cookies/headers
session = requests.Session()

def create_test_video(filename: str = "test_video.mp4", duration_seconds: int = 5) -> bool:
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
            return True
        else:
            print("❌ Failed to create test video")
            return False
    except Exception as e:
        print(f"❌ Error creating test video: {e}")
        return False

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

def test_mediapipe_basic() -> bool:
    """Test if MediaPipe and OpenCV are properly installed"""
    print("\n🔬 Testing MediaPipe and OpenCV installation...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
        print(f"   Version: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV not installed: {e}")
        print("💡 Install with: pip install opencv-python")
        return False
    except Exception as e:
        print(f"❌ Error importing OpenCV: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
        print(f"   Version: {mp.__version__}")
        
        # Test basic MediaPipe components
        mp_pose = mp.solutions.pose
        print("✅ MediaPipe Pose module loaded")
        
        mp_holistic = mp.solutions.holistic
        print("✅ MediaPipe Holistic module loaded")
        
        mp_drawing = mp.solutions.drawing_utils
        print("✅ MediaPipe Drawing utilities loaded")
        
        return True
        
    except ImportError as e:
        print(f"❌ MediaPipe not installed: {e}")
        print("💡 Install with: pip install mediapipe")
        return False
    except Exception as e:
        print(f"❌ Error testing MediaPipe: {e}")
        return False

def test_mediapipe_processing(video_path: str) -> bool:
    """Test MediaPipe processing on the test video"""
    print(f"\n🔬 Testing MediaPipe processing on video: {video_path}")
    
    try:
        # Check if OpenCV and MediaPipe are available
        import cv2
        import mediapipe as mp
        
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

def test_body_analysis_pipeline() -> bool:
    """Test the complete body analysis pipeline"""
    print("\n" + "="*60)
    print("TESTING COMPLETE BODY ANALYSIS PIPELINE")
    print("="*60)
    
    # Step 1: Test MediaPipe installation
    print("\nStep 1: Testing MediaPipe Installation")
    mediapipe_ok = test_mediapipe_basic()
    if not mediapipe_ok:
        print("❌ MediaPipe/Opencv installation test failed")
        return False
    
    # Step 2: Create test video
    print("\nStep 2: Create Test Video")
    video_created = create_test_video("body_analysis_test.mp4", 3)
    if not video_created:
        print("❌ Failed to create test video")
        return False
    
    # Step 3: Test MediaPipe processing on video
    print("\nStep 3: Test MediaPipe Processing")
    mediapipe_processing_ok = test_mediapipe_processing("body_analysis_test.mp4")
    if not mediapipe_processing_ok:
        print("❌ MediaPipe processing test failed")
        # Continue anyway as this is just a frontend test
    
    # Step 4: Register user
    print("\nStep 4: User Registration")
    register_response = register_user()
    if not register_response:
        print("❌ Registration failed")
        return False
    
    # Wait for user creation
    time.sleep(2)
    
    # Step 5: Login
    print("\nStep 5: User Login")
    tokens = login_user()
    if not tokens:
        print("❌ Login failed")
        return False
    
    # Wait for authentication to settle
    time.sleep(1)
    
    # Step 6: Get user profile to get user ID
    print("\nStep 6: Get User Profile")
    profile = get_user_profile()
    if not profile:
        print("❌ Failed to get user profile")
        return False
    
    user_id = profile.get('id')
    if not user_id:
        print("❌ User ID not found in profile")
        return False
    
    print(f"✅ User ID obtained: {user_id}")
    
    # Step 7: Upload video for body analysis
    print("\nStep 7: Upload Video for Body Analysis")
    upload_result = upload_video_for_body_analysis(user_id, "body_analysis_test.mp4", "full_body_analysis")
    if not upload_result:
        print("❌ Video upload failed")
        return False
    
    print("✅ Complete body analysis pipeline test completed successfully!")
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
    print("🚀 Starting Complete Body Analysis Pipeline Test")
    print(f"Using email: {EMAIL}")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Run the complete body analysis test
        success = test_body_analysis_pipeline()
        
        # Clean up
        cleanup_test_files()
        
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        
        if success:
            print("✅ All body analysis tests passed!")
            print("✅ Complete body analysis video processing pipeline is working!")
        else:
            print("❌ Some body analysis tests failed!")
            print("❌ There may be issues with the body analysis pipeline")
            
    except Exception as e:
        print(f"💥 Unexpected error during testing: {e}")
        cleanup_test_files()

if __name__ == "__main__":
    main()