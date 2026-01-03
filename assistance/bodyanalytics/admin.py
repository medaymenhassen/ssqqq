from django.contrib import admin
from .models import (
    Users, Offers, UserOffers, CourseLessons, TestQuestions, TestAnswers,
    Data, Documents, PasswordResetTokens, RefreshTokens, TokenBlacklist,
    UserCourseCompletions, UserLessonCompletions, UserTestResults
)


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'firstname', 'lastname', 'role', 'enabled', 'created_at')
    list_filter = ('role', 'enabled', 'created_at')
    search_fields = ('email', 'firstname', 'lastname')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('email', 'firstname', 'lastname', 'password', 'role')
        }),
        ('Account Status', {
            'fields': ('enabled', 'account_non_expired', 'account_non_locked', 'credentials_non_expired')
        }),
        ('Additional Info', {
            'fields': ('is_blocked', 'blocked_reason', 'rgpd_accepted', 'rgpd_accepted_at', 'ccpa_accepted', 'ccpa_accepted_at', 'commercial_use_consent', 'commercial_use_consent_at', 'user_type')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Offers)
class OffersAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'duration_hours', 'is_active', 'created_at')
    list_filter = ('is_active', 'duration_hours', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserOffers)
class UserOffersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'offer', 'approval_status', 'is_active', 'purchase_date', 'expiration_date', 'created_at')
    list_filter = ('approval_status', 'is_active', 'purchase_date', 'created_at')
    search_fields = ('user__email', 'offer__title')
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['approve_offers', 'reject_offers']
    
    def approve_offers(self, request, queryset):
        queryset.update(approval_status='APPROVED', is_active=True)
        self.message_user(request, f'{queryset.count()} offers were successfully approved.')
    approve_offers.short_description = "Approve selected offers"
    
    def reject_offers(self, request, queryset):
        queryset.update(approval_status='REJECTED', is_active=False)
        self.message_user(request, f'{queryset.count()} offers were successfully rejected.')
    reject_offers.short_description = "Reject selected offers"


@admin.register(CourseLessons)
class CourseLessonsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'is_service', 'display_order', 'lesson_order', 'created_at')
    list_filter = ('is_service', 'display_order', 'lesson_order', 'created_at')
    search_fields = ('title', 'content_title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TestQuestions)
class TestQuestionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'test', 'lesson', 'question_order', 'points', 'question_type', 'created_at')
    list_filter = ('question_type', 'points', 'created_at')
    search_fields = ('question_text',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TestAnswers)
class TestAnswersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'created_at')
    search_fields = ('user__email', 'question__question_text')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'movement_detected', 'timestamp', 'created_at')
    list_filter = ('movement_detected', 'timestamp', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['download_images_to_desktop', 'delete_images_from_server']
    
    def download_images_to_desktop(self, request, queryset):
        '''Download selected records' images to user's desktop'''
        from django.http import HttpResponse, FileResponse
        import os
        import zipfile
        from django.conf import settings
        import json
        import threading
        import time
        from django.contrib import messages
        
        # Create a temporary directory to store images for the zip file
        temp_dir = os.path.join(settings.BASE_DIR, 'temp_download')
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            zip_filename = f"movement_images_{len(queryset)}_records.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for data_record in queryset:
                    # Check if json_data contains image information
                    if data_record.json_data:
                        json_data = data_record.json_data if isinstance(data_record.json_data, dict) else json.loads(data_record.json_data)
                        
                        # Determine the movement type for folder organization
                        movement_type = 'general'
                        if data_record.movement_detected is not None:
                            if isinstance(data_record.movement_detected, bool):
                                movement_type = 'movement_detected' if data_record.movement_detected else 'no_movement'
                            elif isinstance(data_record.movement_detected, str):
                                movement_type = data_record.movement_detected.lower()
                            else:
                                movement_type = str(data_record.movement_detected).lower()
                        
                        # Look for various possible image-related fields in the JSON
                        possible_image_fields = ['image_urls', 'image_paths', 'images', 'image_path', 'image_url', 'image_data']
                        for field in possible_image_fields:
                            if field in json_data:
                                field_value = json_data[field]
                                if isinstance(field_value, list):
                                    # If it's a list of image paths/URLs
                                    for i, img_ref in enumerate(field_value):
                                        # If it's a URL, convert to local path
                                        if isinstance(img_ref, str) and img_ref.startswith('http'):
                                            # Extract filename from URL and look in media directory
                                            from urllib.parse import urlparse
                                            filename = os.path.basename(urlparse(img_ref).path)
                                            img_path = os.path.join(settings.MEDIA_ROOT, filename)
                                        elif isinstance(img_ref, str):
                                            # Direct path
                                            img_path = img_ref if os.path.isabs(img_ref) else os.path.join(settings.BASE_DIR, img_ref)
                                        else:
                                            continue
                                        
                                        if os.path.exists(img_path):
                                            # Organize by movement type in ZIP file
                                            image_name = f"{movement_type}/{data_record.id}_{data_record.movement_detected}_{field}_{i}.jpg"
                                            zip_file.write(img_path, image_name)
                                            
                                elif isinstance(field_value, str):
                                    # If it's a single image path/URL
                                    if field_value.startswith('http'):
                                        # Extract filename from URL and look in media directory
                                        from urllib.parse import urlparse
                                        filename = os.path.basename(urlparse(field_value).path)
                                        img_path = os.path.join(settings.MEDIA_ROOT, filename)
                                    else:
                                        # Direct path
                                        img_path = field_value if os.path.isabs(field_value) else os.path.join(settings.BASE_DIR, field_value)
                                    
                                    if os.path.exists(img_path):
                                        # Organize by movement type in ZIP file
                                        image_name = f"{movement_type}/{data_record.id}_{data_record.movement_detected}_{field}.jpg"
                                        zip_file.write(img_path, image_name)
                    
                    # Also check the image_data field for image path
                    if data_record.image_data:
                        img_path = data_record.image_data if os.path.isabs(data_record.image_data) else os.path.join(settings.BASE_DIR, data_record.image_data)
                        if os.path.exists(img_path):
                            image_name = f"{movement_type}/{data_record.id}_{data_record.movement_detected}_from_image_data.jpg"
                            zip_file.write(img_path, image_name)
                    
                    # Check if there are images in the media directory related to this record
                    import glob
                    # Look for images in the active_capture directories that might be related to this record
                    search_pattern = os.path.join(settings.MEDIA_ROOT, 'active_capture', '**', f'*{data_record.id}*')
                    related_images = glob.glob(search_pattern, recursive=True)
                    for img_path in related_images:
                        if os.path.isfile(img_path):
                            image_name = f"{movement_type}/{data_record.id}_{os.path.basename(img_path)}"
                            zip_file.write(img_path, image_name)
            
            # Return the zip file as a response
            response = FileResponse(
                open(zip_path, 'rb'),
                content_type='application/zip',
                as_attachment=True,
                filename=zip_filename
            )
            
            # Clean up temporary directory after response
            def cleanup():
                time.sleep(5)  # Wait a bit for the file to be sent
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            
            threading.Thread(target=cleanup).start()
            
            self.message_user(request, f"{len(queryset)} records' images have been downloaded to your desktop.")
            return response
        
        except Exception as e:
            self.message_user(request, f"Error downloading images: {str(e)}", level=messages.ERROR)
            return None
    
    download_images_to_desktop.short_description = "Download selected records' images to desktop"
    
    def delete_images_from_server(self, request, queryset):
        '''Delete selected records' images from server'''
        import json
        import os
        
        deleted_count = 0
        for data_record in queryset:
            # Check json_data for image paths and delete them
            if data_record.json_data:
                json_data = data_record.json_data if isinstance(data_record.json_data, dict) else json.loads(data_record.json_data)
                
                # Delete image files referenced in json_data
                possible_image_fields = ['image_urls', 'image_paths', 'images', 'image_path', 'image_url', 'image_data']
                for field in possible_image_fields:
                    if field in json_data:
                        field_value = json_data[field]
                        if isinstance(field_value, list):
                            # If it's a list of image paths/URLs
                            for img_ref in field_value:
                                if isinstance(img_ref, str) and img_ref.startswith('http'):
                                    # Extract filename from URL and look in media directory
                                    from urllib.parse import urlparse
                                    filename = os.path.basename(urlparse(img_ref).path)
                                    img_path = os.path.join(settings.MEDIA_ROOT, filename)
                                elif isinstance(img_ref, str):
                                    # Direct path
                                    img_path = img_ref if os.path.isabs(img_ref) else os.path.join(settings.BASE_DIR, img_ref)
                                else:
                                    continue
                                
                                if os.path.exists(img_path):
                                    os.remove(img_path)
                                    deleted_count += 1
                        elif isinstance(field_value, str):
                            # If it's a single image path/URL
                            if field_value.startswith('http'):
                                # Extract filename from URL and look in media directory
                                from urllib.parse import urlparse
                                filename = os.path.basename(urlparse(field_value).path)
                                img_path = os.path.join(settings.MEDIA_ROOT, filename)
                            else:
                                # Direct path
                                img_path = field_value if os.path.isabs(field_value) else os.path.join(settings.BASE_DIR, field_value)
                            
                            if os.path.exists(img_path):
                                os.remove(img_path)
                                deleted_count += 1
            
            # Delete image file referenced in image_data field
            if data_record.image_data and os.path.exists(data_record.image_data):
                os.remove(data_record.image_data)
                deleted_count += 1
            
            # Delete the record itself
            data_record.delete()
        
        self.message_user(request, f"{deleted_count} images have been deleted from the server.")
    
    delete_images_from_server.short_description = "Delete selected records' images from server"


@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'file_name', 'file_type', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('file_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PasswordResetTokens)
class PasswordResetTokensAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('token', 'user__email')
    readonly_fields = ('created_at',)


@admin.register(RefreshTokens)
class RefreshTokensAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'created_at', 'expiry_date')
    list_filter = ('created_at', 'expiry_date')
    search_fields = ('token', 'user__email')
    readonly_fields = ('created_at',)


@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'blacklisted_at', 'reason')
    list_filter = ('blacklisted_at', 'reason')
    search_fields = ('token', 'reason')
    readonly_fields = ('blacklisted_at',)


@admin.register(UserCourseCompletions)
class UserCourseCompletionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'completed_at', 'created_at')
    list_filter = ('completed_at', 'created_at')
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserLessonCompletions)
class UserLessonCompletionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lesson', 'completed_at', 'created_at')
    list_filter = ('completed_at', 'created_at')
    search_fields = ('user__email', 'lesson__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserTestResults)
class UserTestResultsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'test', 'score', 'passed', 'created_at')
    list_filter = ('passed', 'created_at')
    search_fields = ('user__email', 'test__title')
    readonly_fields = ('created_at', 'updated_at')