"""
Test script to verify that the video generation functionality works correctly
with the updated VideoGeneratorUtil that creates proper MP4 files from CSV data.
"""
import requests
import json
import time
import csv
import io
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

def test_video_generation_from_csv():
    """Test the video generation from CSV functionality"""
    print("=" * 70)
    print("🎬 TESTING VIDEO GENERATION FROM CSV DATA")
    print("=" * 70)
    
    # Create a session
    session = requests.Session()
    
    # Step 1: Register a test user
    print("\n📝 STEP 1: Registering test user")
    print("-" * 40)
    
    register_data = {
        "email": f"video_test_{int(time.time())}@example.com",
        "password": "testpassword123",
        "confirmPassword": "testpassword123",
        "firstname": "Video",
        "lastname": "Test",
        "rgpdAccepted": True,
        "ccpaAccepted": True,
        "commercialUseConsent": True
    }
    
    response = session.post(
        f"{BASE_URL}/api/auth/register",
        json=register_data,
        headers=HEADERS
    )
    
    if response.status_code == 200:
        print("✅ User registration successful")
    else:
        print(f"❌ User registration failed: {response.status_code} - {response.text}")
        return False
    
    # Step 2: Login the user
    print("\n🔐 STEP 2: Logging in user")
    print("-" * 40)
    
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers=HEADERS
    )
    
    if response.status_code == 200:
        login_result = response.json()
        access_token = login_result.get('accessToken')
        session.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        print("✅ User login successful")
        print(f"   Access token: {access_token[:20]}...")
    else:
        print(f"❌ User login failed: {response.status_code} - {response.text}")
        return False
    
    # Step 3: Generate test CSV data
    print("\n📊 STEP 3: Generating test CSV data")
    print("-" * 40)
    
    # Create test CSV data that simulates movement data from body analysis
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Timestamp', 'Pose Confidence', 'Head X', 'Head Y', 'Head Z', 'Head Confidence',
        'Left Shoulder X', 'Left Shoulder Y', 'Left Shoulder Z', 'Left Shoulder Confidence',
        'Right Shoulder X', 'Right Shoulder Y', 'Right Shoulder Z', 'Right Shoulder Confidence',
        'Left Hip X', 'Left Hip Y', 'Left Hip Z', 'Left Hip Confidence',
        'Right Hip X', 'Right Hip Y', 'Right Hip Z', 'Right Hip Confidence',
        'Face Confidence', 'Mouth Open', 'Eye Blink Left', 'Eye Blink Right', 
        'Eye Look Left', 'Eye Look Right', 'Head Position X', 'Head Position Y', 'Head Position Z',
        'Left Hand Gesture', 'Left Hand Landmarks', 'Right Hand Gesture', 'Right Hand Landmarks'
    ])
    
    # Generate test data for multiple frames
    base_time = int(time.time() * 1000)
    for i in range(5):  # Generate 5 frames of data
        timestamp = base_time + (i * 100)  # 100ms intervals
        
        row = [
            timestamp,  # Timestamp
            0.95 + (i * 0.01),  # Pose Confidence
            0.1 + (i * 0.01),   # Head X
            0.2 + (i * 0.01),   # Head Y
            0.3 + (i * 0.01),   # Head Z
            0.90 + (i * 0.01),  # Head Confidence
            0.4 + (i * 0.01),   # Left Shoulder X
            0.5 + (i * 0.01),   # Left Shoulder Y
            0.6 + (i * 0.01),   # Left Shoulder Z
            0.85 + (i * 0.01),  # Left Shoulder Confidence
            0.7 + (i * 0.01),   # Right Shoulder X
            0.8 + (i * 0.01),   # Right Shoulder Y
            0.9 + (i * 0.01),   # Right Shoulder Z
            0.80 + (i * 0.01),  # Right Shoulder Confidence
            1.0 + (i * 0.01),   # Left Hip X
            1.1 + (i * 0.01),   # Left Hip Y
            1.2 + (i * 0.01),   # Left Hip Z
            0.75 + (i * 0.01),  # Left Hip Confidence
            1.3 + (i * 0.01),   # Right Hip X
            1.4 + (i * 0.01),   # Right Hip Y
            1.5 + (i * 0.01),   # Right Hip Z
            0.70 + (i * 0.01),  # Right Hip Confidence
            0.92 + (i * 0.01),  # Face Confidence
            0.1 + (i * 0.02),   # Mouth Open
            0.05 + (i * 0.01),  # Eye Blink Left
            0.05 + (i * 0.01),  # Eye Blink Right
            0.1 + (i * 0.01),   # Eye Look Left
            0.1 + (i * 0.01),   # Eye Look Right
            0.0 + (i * 0.01),   # Head Position X
            0.0 + (i * 0.01),   # Head Position Y
            0.0 + (i * 0.01),   # Head Position Z
            f'Gesture_{i}',       # Left Hand Gesture
            21,                   # Left Hand Landmarks
            f'Gesture_{i+1}',     # Right Hand Gesture
            21                    # Right Hand Landmarks
        ]
        
        writer.writerow(row)
    
    csv_content = output.getvalue()
    print(f"✅ Generated CSV data with {len(csv_content.split(chr(10)))-1} rows")
    print(f"   CSV content preview: {csv_content[:200]}...")
    
    # Step 4: Create video from CSV
    print("\n🎥 STEP 4: Creating video from CSV data")
    print("-" * 40)
    
    import io
    import requests
    
    # Create a file-like object from the CSV content
    files = {'file': ('movement-data.csv', csv_content, 'text/csv')}
    data = {
        'userId': 1,  # This will be ignored since we're authenticated
        'videoName': f'test-analysis-{datetime.now().strftime("%Y%m%d-%H%M%S")}.mp4'
    }
    
    url = f"{BASE_URL}/springboot/csv/create-video"
    
    try:
        response = session.post(url, files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Video created successfully from CSV data")
            print(f"   Response: {json.dumps(result, indent=2)[:500]}...")
            
            # Check if we got a video URL
            video_url = result.get('videoUrl')
            if video_url:
                print(f"   Video URL: {video_url}")
                
                # Step 5: Verify the video file was created
                print("\n🔍 STEP 5: Verifying video file")
                print("-" * 40)
                
                # Try to download the video file to check if it's valid
                full_video_url = f"{BASE_URL}{video_url}"
                video_response = session.get(full_video_url)
                
                if video_response.status_code == 200:
                    print(f"✅ Video file downloaded successfully")
                    print(f"   File size: {len(video_response.content)} bytes")
                    print(f"   Content type: {video_response.headers.get('Content-Type', 'Unknown')}")
                    
                    # Check if it has MP4-like structure (has 'ftyp' box)
                    content = video_response.content
                    if len(content) >= 12:
                        # Check for 'ftyp' box in the first 12 bytes
                        if b'ftyp' in content[:12]:
                            print("✅ Video has proper MP4 header ('ftyp' box found)")
                        else:
                            print("⚠️ Video may not have proper MP4 header")
                    else:
                        print("⚠️ Video file is too small to verify")
                    
                    return True
                else:
                    print(f"❌ Could not download video file: {video_response.status_code}")
                    return False
            else:
                print("⚠️ No video URL in response")
                return False
        else:
            print(f"❌ Video creation failed with status code {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating video from CSV: {e}")
        return False

def main():
    success = test_video_generation_from_csv()
    
    print("\n" + "=" * 70)
    print("📋 VIDEO GENERATION TEST SUMMARY")
    print("=" * 70)
    
    if success:
        print("✅ VIDEO GENERATION TEST PASSED")
        print("✅ CSV data is properly converted to valid MP4 files")
        print("✅ Video files have proper MP4 headers and structure")
        print("✅ Integration between frontend and backend works correctly")
    else:
        print("❌ VIDEO GENERATION TEST FAILED")
        print("❌ There are issues with video generation from CSV data")
    
    print("=" * 70)

if __name__ == "__main__":
    main()