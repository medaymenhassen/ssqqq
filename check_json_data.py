#!/usr/bin/env python
"""
Script to connect to Django admin and check/update json_data field for records.
This script verifies if json_data is empty and updates it based on the image file paths.
"""
import os
import sys
import django
import requests
from urllib.parse import urljoin
import json
import re

# Add the Django project path to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'assistance'))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assistance.settings')

# Setup Django
django.setup()

from bodyanalytics.models import Data as MovementRecord
from django.contrib.auth.models import User

def get_django_admin_token(username, password):
    """
    Get authentication token for Django admin access
    """
    login_url = 'http://localhost:8000/api-token-auth/'
    data = {
        'username': username,
        'password': password
    }
    
    try:
        response = requests.post(login_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('token')
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def get_csrf_token(session):
    """
    Get CSRF token from Django admin
    """
    try:
        response = session.get('http://localhost:8000/ai/admin/login/')
        csrf_token = None
        if 'csrftoken' in response.cookies:
            csrf_token = response.cookies['csrftoken']
        return csrf_token
    except Exception as e:
        print(f"Error getting CSRF token: {e}")
        return None

def extract_info_from_image_path(image_path):
    """
    Extract detection type and movement name from image path
    Path format: /media/active_capture/{detection_type}/{subcategory}/{movement_name}/filename
    """
    if not image_path:
        return None
        
    # Extract the path components from the image path
    # Example: /media/active_capture/face/face/disgust/image.jpg
    pattern = r'/active_capture/([^/]+)/([^/]+)/([^/]+)/'
    match = re.search(pattern, image_path)
    
    if match:
        detection_type = match.group(1)
        subcategory = match.group(2)
        movement_name = match.group(3)
        
        # Create a simplified JSON structure similar to what should be stored
        json_data = {
            'detection_type': detection_type,
            'movement_name': movement_name,
            'subcategory': subcategory,
            'hasFace': detection_type == 'face',
            'hasPose': detection_type == 'pose',
            'hasHands': detection_type == 'hand',
            'timestamp': int(django.utils.timezone.now().timestamp() * 1000)
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

def update_record_via_admin(record_id, json_data, session, csrf_token):
    """
    Update a record via Django admin interface
    """
    update_url = f'http://localhost:8000/ai/admin/bodyanalytics/data/{record_id}/change/'
    
    # Get the current form data
    try:
        response = session.get(update_url)
        if response.status_code != 200:
            print(f"Failed to access admin page for record {record_id}: {response.status_code}")
            return False
            
        # This is a simplified approach - in a real scenario, you'd need to parse the form
        # and include all required fields to avoid validation errors
        print(f"Would update record {record_id} with JSON data: {json.dumps(json_data, indent=2)}")
        return True
        
    except Exception as e:
        print(f"Error updating record {record_id}: {e}")
        return False

def main():
    print("Connecting to Django admin to check/update json_data field...")
    
    # Get Django admin credentials
    username = input("Enter Django admin username: ")
    password = input("Enter Django admin password: ")
    
    # Get authentication token
    token = get_django_admin_token(username, password)
    if not token:
        print("Failed to authenticate with Django admin")
        return
    
    print(f"Authenticated successfully with token: {token[:8]}...")
    
    # Create a session with authentication
    session = requests.Session()
    session.headers.update({
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    })
    
    # Get CSRF token
    csrf_token = get_csrf_token(session)
    if csrf_token:
        session.headers.update({'X-CSRFToken': csrf_token})
    
    # Find records with empty json_data
    empty_json_records = MovementRecord.objects.filter(json_data__isnull=True)
    print(f"Found {empty_json_records.count()} records with empty json_data")
    
    updated_count = 0
    
    for record in empty_json_records:
        print(f"\nProcessing record ID: {record.id}")
        
        # Try to extract information from the image_data field
        image_data = record.image_data
        if image_data:
            # If image_data is a JSON string, parse it to get image paths
            try:
                image_paths = json.loads(image_data) if isinstance(image_data, str) and image_data.startswith('[') else [image_data]
                if isinstance(image_paths, str):
                    image_paths = [image_paths]
            except json.JSONDecodeError:
                image_paths = [image_data]
                
            # Extract info from the first image path
            extracted_json = None
            for img_path in image_paths:
                extracted_json = extract_info_from_image_path(img_path)
                if extracted_json:
                    break
                    
            if extracted_json:
                print(f"  Extracted JSON data: {json.dumps(extracted_json, indent=2)}")
                
                # Update the record in the database directly (bypassing the OID field issue)
                try:
                    # Since the json_data field is OID type, we need to update it differently
                    # For now, let's just print what would be updated
                    print(f"  Would update record {record.id} with extracted data")
                    
                    # In a real scenario, you'd need to handle the OID field differently
                    # or potentially alter the database schema to use a proper JSON/TEXT field
                    updated_count += 1
                except Exception as e:
                    print(f"  Error updating record {record.id}: {e}")
            else:
                print(f"  Could not extract information from image path: {image_data}")
        else:
            print(f"  No image data available for record {record.id}")
    
    print(f"\nCompleted check. Found {empty_json_records.count()} records with empty json_data, processed {updated_count} records")

if __name__ == "__main__":
    main()