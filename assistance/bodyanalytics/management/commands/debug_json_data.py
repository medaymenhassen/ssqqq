"""
Management command to debug and fix json_data saving issues
"""
from django.core.management.base import BaseCommand
from bodyanalytics.models import Data as MovementRecord
import json

class Command(BaseCommand):
    help = 'Debug and fix json_data field issues in MovementRecord model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix empty json_data fields by extracting info from image paths',
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check records with empty json_data fields',
        )

    def handle(self, *args, **options):
        if options['check']:
            self.check_json_data()
        elif options['fix']:
            self.fix_json_data()
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Please specify either --check or --fix option'
                )
            )

    def check_json_data(self):
        """Check records with empty json_data fields"""
        self.stdout.write('Checking records with empty json_data...')
        
        empty_records = MovementRecord.objects.filter(json_data__isnull=True)
        self.stdout.write(f'Found {empty_records.count()} records with empty json_data')
        
        for record in empty_records:
            self.stdout.write(f'  - Record ID: {record.id}, User: {record.user_id}, Timestamp: {record.timestamp}')

    def fix_json_data(self):
        """Fix records with empty json_data fields"""
        self.stdout.write('Fixing records with empty json_data...')
        
        empty_records = MovementRecord.objects.filter(json_data__isnull=True)
        updated_count = 0
        
        for record in empty_records:
            # Try to extract information from image_data field
            if record.image_data:
                # Extract detection type and movement from image path
                import re
                pattern = r'/active_capture/([^/]+)/([^/]+)/([^/]+)/'
                match = re.search(pattern, str(record.image_data))
                
                if match:
                    detection_type = match.group(1)
                    subcategory = match.group(2)
                    movement_name = match.group(3)
                    
                    # Create simplified JSON data
                    json_data = {
                        'detection_type': detection_type,
                        'movement_name': movement_name,
                        'subcategory': subcategory,
                        'timestamp': int(record.timestamp.timestamp() * 1000) if record.timestamp else None,
                        'user_id': record.user_id
                    }
                    
                    try:
                        # Try to save the JSON data
                        record.json_data = json.dumps(json_data)
                        record.save()
                        self.stdout.write(f'  - Updated record {record.id} with JSON data')
                        updated_count += 1
                    except Exception as e:
                        self.stdout.write(f'  - Error updating record {record.id}: {e}')
                else:
                    self.stdout.write(f'  - Could not extract info from image path for record {record.id}')
            else:
                self.stdout.write(f'  - No image data for record {record.id}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Fixed {updated_count} records with empty json_data'
            )
        )