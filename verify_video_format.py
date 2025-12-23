"""
Video Format Verification Script
This script checks if video files have proper MP4 format headers
"""
import os
import struct

def check_mp4_header(file_path):
    """Check if a file has proper MP4 headers"""
    if not os.path.exists(file_path):
        print(f"❌ File does not exist: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            # Read the first 32 bytes to check for MP4 signature
            header = f.read(32)
            
            # Check for common MP4 signatures
            # MP4 files typically start with size and 'ftyp' atom
            if len(header) < 12:
                print(f"❌ File too small to be a valid MP4: {file_path}")
                return False
            
            # Unpack the first 8 bytes to check for size and type
            size_bytes = header[:4]
            atom_type = header[4:8]
            
            # Convert size from big-endian
            size = struct.unpack('>I', size_bytes)[0]
            
            # Check if it starts with a valid atom type
            if atom_type == b'ftyp':  # 'ftyp' is the typical first atom in MP4
                print(f"✅ {file_path} has valid MP4 header with 'ftyp' atom")
                print(f"   Size: {size} bytes, Type: {atom_type.decode('ascii', errors='ignore')}")
                return True
            else:
                print(f"❌ {file_path} does not have proper MP4 header")
                print(f"   Expected 'ftyp', got: {atom_type.decode('ascii', errors='ignore')}")
                return False
                
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {e}")
        return False

def check_all_videos_in_directory(directory_path):
    """Check all video files in a directory"""
    if not os.path.exists(directory_path):
        print(f"❌ Directory does not exist: {directory_path}")
        return
    
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    video_files = []
    
    for file in os.listdir(directory_path):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(file)
    
    if not video_files:
        print(f"No video files found in {directory_path}")
        return
    
    print(f"🔍 Found {len(video_files)} video files to check:")
    for video_file in video_files:
        file_path = os.path.join(directory_path, video_file)
        print(f"\nChecking: {video_file}")
        check_mp4_header(file_path)

def main():
    print("Video Format Verification Tool")
    print("=" * 40)
    
    # Get file path from user
    file_path = input("Enter full path to video file to check (or press Enter for default): ").strip()
    
    if not file_path:
        # Default to a specific video file in the project
        file_path = "D:\\final\\3Dproject\\School\\src\\main\\resources\\static\\uploads\\analysis-2025-12-23T07-28-18.mp4"
    
    print(f"Checking video file: {file_path}")
    print("-" * 40)
    
    check_mp4_header(file_path)

if __name__ == "__main__":
    main()