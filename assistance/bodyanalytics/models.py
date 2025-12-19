from django.db import models
from django.contrib.auth.models import User


class MovementRecord(models.Model):
    """Model to store movement tracking records"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    image_data = models.TextField(blank=True, null=True)  # Base64 encoded image
    video_url = models.URLField(blank=True, null=True)  # URL to video segment
    json_data = models.JSONField(blank=True, null=True)  # JSON data with pose, face, hand info
    movement_detected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Movement Record'
        verbose_name_plural = 'Movement Records'

    def __str__(self):
        return f"Movement Record {self.id} - {self.user.username} at {self.timestamp}"


class PoseData(models.Model):
    """Model to store detailed pose data"""
    movement_record = models.ForeignKey(MovementRecord, on_delete=models.CASCADE, related_name='pose_data')
    body_part = models.CharField(max_length=50)  # e.g., 'Head', 'LeftShoulder', 'RightHip'
    x_position = models.FloatField()
    y_position = models.FloatField()
    z_position = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Pose Data'
        verbose_name_plural = 'Pose Data'

    def __str__(self):
        return f"{self.body_part} - ({self.x_position}, {self.y_position}, {self.z_position})"


class FaceData(models.Model):
    """Model to store face tracking data"""
    movement_record = models.ForeignKey(MovementRecord, on_delete=models.CASCADE, related_name='face_data')
    eye_openness_left = models.FloatField(null=True, blank=True)
    eye_openness_right = models.FloatField(null=True, blank=True)
    mouth_openness = models.FloatField(null=True, blank=True)
    head_position_x = models.FloatField(null=True, blank=True)
    head_position_y = models.FloatField(null=True, blank=True)
    head_position_z = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Face Data'
        verbose_name_plural = 'Face Data'

    def __str__(self):
        return f"Face Data - Movement {self.movement_record.id}"


class HandData(models.Model):
    """Model to store hand tracking data"""
    HAND_CHOICES = [
        ('LEFT', 'Left'),
        ('RIGHT', 'Right'),
    ]
    
    movement_record = models.ForeignKey(MovementRecord, on_delete=models.CASCADE, related_name='hand_data')
    hand = models.CharField(max_length=10, choices=HAND_CHOICES)
    gesture = models.CharField(max_length=50, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    landmarks = models.JSONField(blank=True, null=True)  # Store hand landmarks as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Hand Data'
        verbose_name_plural = 'Hand Data'

    def __str__(self):
        return f"{self.hand} Hand - {self.gesture} - Movement {self.movement_record.id}"
