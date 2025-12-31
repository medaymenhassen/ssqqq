#!/usr/bin/env python3
"""
Script to check if a VRM file has a humanoid skeleton structure.
This script analyzes the VRM file to determine if it contains proper humanoid bone rigging.
"""

import json
import sys
import struct
from pathlib import Path


def check_vrm_skeleton(vrm_path):
    """
    Check if a VRM file contains proper humanoid skeleton structure.
    """
    vrm_path = Path(vrm_path)
    
    if not vrm_path.exists():
        print(f"❌ File not found: {vrm_path}")
        return False
    
    try:
        # Read the VRM file (it's a GLB format - GL Binary)
        with open(vrm_path, 'rb') as f:
            # Check if it's a GLB file by looking for the magic number
            magic = f.read(4)
            if magic != b'glTF':
                print(f"❌ Not a valid GLB/GLTF file: {vrm_path}")
                return False
            
            # Read version (next 4 bytes)
            version = struct.unpack('<I', f.read(4))[0]
            print(f"📊 GLTF Version: {version}")
            
            # Skip length (next 4 bytes)
            length = struct.unpack('<I', f.read(4))[0]
            print(f"📊 File length: {length}")
        
        # Load as JSON to check VRM extensions
        with open(vrm_path, 'rb') as f:
            content = f.read()
        
        # VRM files are stored as GLB (binary GLTF) with JSON metadata
        # Find the JSON portion within the GLB file
        if content[:4] == b'glTF':
            # Parse GLB format
            version = struct.unpack('<I', content[4:8])[0]
            length = struct.unpack('<I', content[8:12])[0]
            
            # GLB has a JSON chunk header (chunk length + type)
            json_chunk_length = struct.unpack('<I', content[12:16])[0]
            json_chunk_type = content[16:20]  # Should be b'JSON'
            
            if json_chunk_type != b'JSON':
                print("❌ No JSON chunk found in GLB file")
                return False
            
            # Extract JSON data
            json_data = content[20:20+json_chunk_length].decode('utf-8')
            gltf_data = json.loads(json_data)
        else:
            print("❌ Invalid GLB format")
            return False
        
        # Check for VRM extension
        extensions = gltf_data.get('extensions', {})
        vrm_ext = extensions.get('VRM', {})
        
        if not vrm_ext:
            print("❌ This file is not a VRM file (no VRM extension found)")
            # Check if it's a regular GLTF/GLB file
            if 'scenes' in gltf_data and 'nodes' in gltf_data:
                print("ℹ️  This appears to be a regular GLTF/GLB file, not a VRM with humanoid rigging")
            return False
        
        print("✅ This is a valid VRM file!")
        
        # Check for humanoid structure
        humanoid = vrm_ext.get('humanoid', {})
        if not humanoid:
            print("❌ No humanoid data found in VRM extension")
            return False
        
        human_bones = humanoid.get('humanBones', [])
        print(f"📊 Found {len(human_bones)} humanoid bones:")
        
        required_bones = [
            'hips', 'leftUpperLeg', 'rightUpperLeg', 'leftLowerLeg', 'rightLowerLeg',
            'leftFoot', 'rightFoot', 'spine', 'chest', 'neck', 'head',
            'leftShoulder', 'rightShoulder', 'leftUpperArm', 'rightUpperArm',
            'leftLowerArm', 'rightLowerArm', 'leftHand', 'rightHand'
        ]
        
        found_bones = []
        missing_bones = []
        
        for bone in human_bones:
            bone_name = bone.get('bone', '').lower()
            node_index = bone.get('node', -1)
            found_bones.append(bone_name)
            print(f"  - {bone_name} (node index: {node_index})")
        
        for required in required_bones:
            if required not in found_bones:
                missing_bones.append(required)
        
        if missing_bones:
            print(f"⚠️  Missing required bones: {missing_bones}")
            print("ℹ️  This VRM may have limited humanoid functionality")
        else:
            print("✅ All required humanoid bones are present!")
        
        # Check for blend shapes (facial expressions)
        blend_shape_groups = vrm_ext.get('blendShapeMaster', {}).get('blendShapeGroups', [])
        print(f"📊 Found {len(blend_shape_groups)} blend shape groups (facial expressions)")
        
        # Check for materials
        materials = gltf_data.get('materials', [])
        print(f"📊 Found {len(materials)} materials")
        
        # Check for meshes
        meshes = gltf_data.get('meshes', [])
        print(f"📊 Found {len(meshes)} meshes")
        
        return len(missing_bones) == 0  # Return True if all required bones are present
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in GLB file")
        return False
    except struct.error:
        print("❌ Invalid binary format")
        return False
    except Exception as e:
        print(f"❌ Error reading VRM file: {str(e)}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_vrm_skeleton.py <path_to_vrm_file>")
        print("Example: python check_vrm_skeleton.py /path/to/avatar.vrm")
        return
    
    vrm_file = sys.argv[1]
    print(f"🔍 Checking VRM file: {vrm_file}")
    print("-" * 50)
    
    has_skeleton = check_vrm_skeleton(vrm_file)
    
    print("-" * 50)
    if has_skeleton:
        print("✅ The VRM file has a complete humanoid skeleton!")
    else:
        print("❌ The VRM file may not have a complete humanoid skeleton for full animation.")


if __name__ == "__main__":
    main()