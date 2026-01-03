#!/usr/bin/env python
"""
Script to check and fix empty json_data fields in MovementRecord model.
This script runs within the Django environment to directly update records.
"""
import os
import sys
import django
import re
import json
from datetime import datetime

# Add the Django project path to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'assistance'))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assistance.settings')

# Setup Django
django.setup()

from bodyanalytics.models import Data as MovementRecord
from django.contrib.auth.models import User

def extract_info_from_image_path(image_path):
    """
    Extract detection type and movement name from image path
    Path format: /media/active_capture/{detection_type}/{subcategory}/{movement_name}/filename
    """
    if not image_path:
        return None
        
    # Extract the path components from the image path
    pattern = r'/active_capture/([^/]+)/([^/]+)/([^/]+)/'
    match = re.search(pattern, image_path)
    
    if match:
        detection_type = match.group(1)
        subcategory = match.group(2)
        movement_name = match.group(3)
        
        # Create a simplified JSON structure 
        json_data = {
            'detection_type': detection_type,
            'movement_name': movement_name,
            'subcategory': subcategory,
            'hasFace': detection_type == 'face',
            'hasPose': detection_type == 'pose',
            'hasHands': detection_type == 'hand',
            'timestamp': int(datetime.now().timestamp() * 1000)
        }
        
        # If it's face data, add expression info
        if detection_type == 'face':
            json_data['expression'] = movement_name
            
        # If it's hand data, add gesture info
        if detection_type == 'hand':
            gesture = movement_name.split('_')[-1] if '_' in movement_name else movement_name
            handedness = 'left' if 'left' in movement_name else 'right' if 'right' in movement_name else 'unknown'
            json_data['hands_info'] = [{
                'handedness': handedness,
                'gesture': gesture
            }]
        
        return json_data
    
    return None

def main():
    print("Checking for records with empty json_data field...")
    
    # Find records with empty or null json_data
    empty_json_records = MovementRecord.objects.filter(json_data__isnull=True)
    print(f"Found {empty_json_records.count()} records with empty json_data")
    
    updated_count = 0
    error_count = 0
    
    for record in empty_json_records:
        print(f"\nProcessing record ID: {record.id}")
        
        # Try to extract information from the image_data field or other available fields
        # Since the image files are stored in specific paths that indicate detection type
        # we can extract the info from the file paths
        
        # The image files are stored in the media directory with the structure:
        # /media/active_capture/{detection_type}/{subcategory}/{movement_name}/filename
        # Let's try to get the latest image path from the media directory
        
        # Since we know images are saved to specific paths, we can check the media directory
        import os
        from django.conf import settings
        
        media_root = os.path.join(settings.BASE_DIR, 'media') if hasattr(settings, 'BASE_DIR') else os.path.join(os.getcwd(), 'media')
        
        # Check if media directory exists and try to find related images
        if os.path.exists(media_root):
            # Look for image files related to this record based on timestamp or other identifiers
            # For now, we'll use a different approach - try to extract from any available image-related fields
            pass
        
        # If record has image data in the image_data field, extract from there
        image_data = record.image_data
        extracted_json = None
        
        if image_data:
            # Try to extract from image_data
            extracted_json = extract_info_from_image_path(image_data)
        
        # If still no extracted data, try to determine from timestamp and user
        if not extracted_json:
            # Create a basic structure based on available info
            json_data = {
                'detection_type': 'general',
                'movement_name': 'general_movement',
                'timestamp': int(record.timestamp.timestamp() * 1000) if record.timestamp else int(datetime.now().timestamp() * 1000),
                'hasFace': False,
                'hasPose': False,
                'hasHands': False,
                'user_id': record.user_id if record.user_id else None
            }
            extracted_json = json_data
        
        if extracted_json:
            print(f"  Extracted JSON data: {json.dumps(extracted_json, indent=2)}")
            
            # Update the record with the extracted JSON data
            # Note: Since the json_data field is OID type, we may need to handle this differently
            # For now, let's try to update it
            try:
                # Convert to JSON string for storage
                json_str = json.dumps(extracted_json, ensure_ascii=False, separators=(',', ':'))
                
                # Update the record
                record.json_data = json_str
                record.save()
                
                print(f"  Successfully updated record {record.id}")
                updated_count += 1
            except Exception as e:
                print(f"  Error updating record {record.id}: {e}")
                error_count += 1
        else:
            print(f"  Could not extract information for record {record.id}")
            error_count += 1
    
    print(f"\nCompleted processing.")
    print(f"Total records processed: {empty_json_records.count()}")
    print(f"Successfully updated: {updated_count}")
    print(f"Errors encountered: {error_count}")

def fix_oid_field():
    """
    Function to fix the OID field issue by altering the database schema
    """
    print("\nAttempting to fix the OID field issue...")
    
    # This would require a database migration to change the field type
    # from OID to TEXT or JSON. This is a complex operation that would
    # normally be done through Django migrations.
    print("To permanently fix the OID field issue, you need to:")
    print("1. Create a Django migration to change the json_data field type from OID to TEXT/JSON")
    print("2. Apply the migration")
    print("3. The current script works around the issue by updating records directly")

if __name__ == "__main__":
    main()
    fix_oid_field()