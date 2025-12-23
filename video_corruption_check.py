"""
Video Corruption Detection Script
This script captures video from the webcam and analyzes it to detect potential corruption issues.
"""
import cv2
import numpy as np
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoCorruptionDetector:
    def __init__(self):
        self.cap = None
        self.frame_count = 0
        self.corruption_detected = False
        self.previous_frame = None
        
    def initialize_camera(self):
        """Initialize the webcam"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logger.error("Cannot open camera")
            return False
        return True
    
    def check_frame_corruption(self, frame):
        """Check if a frame shows signs of corruption"""
        if frame is None:
            logger.warning("Empty frame detected - possible corruption")
            return True
            
        # Check for common corruption signs
        # 1. Check if frame is completely black or white
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_intensity = np.mean(gray)
        
        if mean_intensity < 5 or mean_intensity > 250:
            logger.warning(f"Frame with unusual mean intensity ({mean_intensity}) detected - possible corruption")
            return True
            
        # 2. Check for extreme pixel value variations
        std_dev = np.std(gray)
        if std_dev > 150:  # High variation might indicate corruption
            logger.warning(f"Frame with high standard deviation ({std_dev}) detected - possible corruption")
            return True
            
        # 3. Check for repeated patterns that might indicate corruption
        if self.previous_frame is not None:
            diff = cv2.absdiff(gray, cv2.cvtColor(self.previous_frame, cv2.COLOR_BGR2GRAY))
            diff_mean = np.mean(diff)
            
            # If difference is too low, frames might be identical/repeated (could indicate issues)
            if diff_mean < 1.0:
                logger.warning(f"Frame appears identical to previous frame (diff_mean: {diff_mean}) - possible issue")
                return True
                
        self.previous_frame = frame.copy()
        return False
    
    def capture_and_analyze(self, duration=10, save_path=None):
        """Capture video for a specified duration and analyze for corruption"""
        if not self.initialize_camera():
            return False
            
        # Define the codec and create VideoWriter if save_path is provided
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = None
        if save_path:
            fps = 20.0  # Adjust based on your needs
            frame_size = (int(self.cap.get(3)), int(self.cap.get(4)))
            out = cv2.VideoWriter(save_path, fourcc, fps, frame_size)
        
        start_time = datetime.now()
        logger.info(f"Starting video capture and analysis for {duration} seconds...")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                logger.error("Failed to capture frame")
                break
                
            # Check for corruption
            if self.check_frame_corruption(frame):
                logger.warning(f"Corruption detected at frame {self.frame_count}")
                self.corruption_detected = True
                break
                
            # Write the frame if output is specified
            if out:
                out.write(frame)
                
            # Display the frame
            cv2.imshow('Video Analysis - Press Q to quit', frame)
            
            self.frame_count += 1
            
            # Check if duration has passed
            elapsed_time = (datetime.now() - start_time).total_seconds()
            if elapsed_time >= duration:
                logger.info(f"Captured for {duration} seconds successfully")
                break
                
            # Break on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Manual interruption by user")
                break
        
        # Release everything
        if self.cap:
            self.cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
        
        return not self.corruption_detected
    
    def analyze_existing_video(self, video_path):
        """Analyze an existing video file for corruption"""
        if not os.path.exists(video_path):
            logger.error(f"Video file does not exist: {video_path}")
            return False
            
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        corruption_count = 0
        
        logger.info(f"Analyzing existing video: {video_path}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if self.check_frame_corruption(frame):
                corruption_count += 1
                logger.warning(f"Corruption detected at frame {frame_count}")
                
            frame_count += 1
            
            # Show progress every 100 frames
            if frame_count % 100 == 0:
                logger.info(f"Processed {frame_count} frames...")
        
        cap.release()
        cv2.destroyAllWindows()
        
        corruption_rate = (corruption_count / frame_count) * 100 if frame_count > 0 else 0
        logger.info(f"Analysis complete: {corruption_count}/{frame_count} frames corrupted ({corruption_rate:.2f}%)")
        
        return corruption_count == 0

def main():
    print("Video Corruption Detection Tool")
    print("1. Capture new video and analyze")
    print("2. Analyze existing video file")
    
    choice = input("Select option (1 or 2): ")
    
    detector = VideoCorruptionDetector()
    
    if choice == "1":
        duration = int(input("Enter capture duration in seconds (default 10): ") or "10")
        save_option = input("Save captured video? (y/n): ").lower() == 'y'
        
        if save_option:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"captured_video_{timestamp}.avi"
            success = detector.capture_and_analyze(duration=duration, save_path=save_path)
            if success:
                print(f"Video captured successfully: {save_path}")
            else:
                print("Issues detected during capture")
        else:
            success = detector.capture_and_analyze(duration=duration)
            if success:
                print("Video captured successfully (not saved)")
            else:
                print("Issues detected during capture")
                
    elif choice == "2":
        video_path = input("Enter path to video file: ")
        success = detector.analyze_existing_video(video_path)
        if success:
            print("Video appears to be clean of corruption")
        else:
            print("Corruption detected in the video")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()