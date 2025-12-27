from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils import timezone


class UserProfile(models.Model):
    """User profile model that mirrors the Spring Boot User model fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    role = models.CharField(max_length=50, default='USER')
    enabled = models.BooleanField(default=True)
    account_non_expired = models.BooleanField(default=True)
    account_non_locked = models.BooleanField(default=True)
    credentials_non_expired = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.CharField(max_length=500, blank=True, null=True)
    rgpd_accepted = models.BooleanField(default=False)
    rgpd_accepted_at = models.DateTimeField(blank=True, null=True)
    ccpa_accepted = models.BooleanField(default=False)
    ccpa_accepted_at = models.DateTimeField(blank=True, null=True)
    user_type_id = models.BigIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.user.email})"


class UserType(models.Model):
    """Model representing user types"""
    name_fr = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    desc_fr = models.CharField(max_length=500, blank=True, null=True)
    desc_en = models.CharField(max_length=500, blank=True, null=True)
    bigger = models.CharField(max_length=255, default='individual')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name_fr} / {self.name_en}"


class TrainingDomain(models.Model):
    """Model representing training domains"""
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    student_count = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Course(models.Model):
    """Model representing courses"""
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CourseModule(models.Model):
    """Model representing course modules"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (Course: {self.course.title})"


class CourseLesson(models.Model):
    """Model representing course lessons"""
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, blank=True, null=True)
    video_url = models.CharField(max_length=255, blank=True, null=True)
    animation_3d_url = models.CharField(max_length=255, blank=True, null=True)
    content_title = models.CharField(max_length=255, blank=True, null=True)
    content_description = models.CharField(max_length=2000, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    lesson_order = models.IntegerField(default=0)
    is_service = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class CourseTest(models.Model):
    """Model representing course tests"""
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, blank=True, null=True)
    passing_score = models.IntegerField(default=70)
    time_limit_minutes = models.IntegerField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TestQuestion(models.Model):
    """Model representing test questions"""
    QUESTION_TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice Question'),
        ('OPEN_ENDED', 'Open Ended Question'),
    ]
    
    EXPECTED_ANSWER_TYPE_CHOICES = [
        ('OPEN_TEXT', 'Open Text'),
        ('MULTIPLE_CHOICE', 'Multiple Choice'),
    ]
    
    course_test = models.ForeignKey(CourseTest, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=1000)
    question_order = models.IntegerField(blank=True, null=True)
    points = models.IntegerField(default=1)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='OPEN_ENDED')
    expected_answer_type = models.CharField(max_length=20, choices=EXPECTED_ANSWER_TYPE_CHOICES, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question_text[:50] + '...' if len(self.question_text) > 50 else self.question_text


class TestAnswer(models.Model):
    """Model representing test answers"""
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=1000, blank=True, null=True)
    is_logical = models.CharField(max_length=255, blank=True, null=True)
    is_correct = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer_order = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer to: {self.question.question_text[:30]}..."


class Document(models.Model):
    """Model representing documents"""
    FILE_TYPE_CHOICES = [
        ('PDF', 'PDF'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    ]
    
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    file_path = models.CharField(max_length=255)
    file_size = models.BigIntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, blank=True, null=True)
    test_answer = models.ForeignKey(TestAnswer, on_delete=models.CASCADE, blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file_name


class Data(models.Model):
    """Model representing data records (movement tracking data)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_data = models.TextField(blank=True, null=True)  # Base64 encoded image
    video_url = models.CharField(max_length=255, blank=True, null=True)
    json_data = models.TextField(blank=True, null=True)  # JSON data
    timestamp = models.DateTimeField()
    movement_detected = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        if self.timestamp is None:
            self.timestamp = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Data record {self.id} for {self.user.username}"


class Registration(models.Model):
    """Model representing course registrations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True)
    registered_at = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} registered for {self.course.title}"


class Location(models.Model):
    """Model representing locations"""
    LOCATION_TYPE_CHOICES = [
        ('OFFICE', 'Office'),
        ('CLASSROOM', 'Classroom'),
        ('LAB', 'Lab'),
    ]
    
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    location_type = models.CharField(max_length=50, choices=LOCATION_TYPE_CHOICES, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CalendarEventType(models.Model):
    """Model representing calendar event types"""
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7)  # Hex color code
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CompanyCalendar(models.Model):
    """Model representing company calendars"""
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, blank=True, null=True)
    event_type = models.ForeignKey(CalendarEventType, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.company.username}"


class MeetingRequest(models.Model):
    """Model representing meeting requests"""
    MEETING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('RESCHEDULED', 'Rescheduled'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_requests_as_company')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meeting_requests_as_requester')
    calendar_event = models.ForeignKey(CompanyCalendar, on_delete=models.CASCADE, blank=True, null=True)
    requested_start_time = models.DateTimeField()
    requested_end_time = models.DateTimeField()
    proposed_start_time = models.DateTimeField(blank=True, null=True)
    proposed_end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=MEETING_STATUS_CHOICES, default='PENDING')
    notes = models.CharField(max_length=1000, blank=True, null=True)
    company_notes = models.CharField(max_length=1000, blank=True, null=True)
    meeting_link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Meeting request from {self.requester.username} to {self.company.username}"


class ServiceRequest(models.Model):
    """Model representing service requests"""
    SERVICE_TYPE_CHOICES = [
        ('COURSE_CREATED', 'Course Created'),
        ('FREELANCE_MISSION', 'Freelance Mission'),
        ('TUTORING', 'Tutoring'),
        ('CONSULTING', 'Consulting'),
        ('OTHER', 'Other'),
    ]
    
    SERVICE_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests_as_provider')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests_as_recipient', blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=SERVICE_STATUS_CHOICES, default='PENDING')
    is_open_to_all = models.BooleanField(default=False)
    rating = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=2000, blank=True, null=True)
    rated_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.provider.username}"


class RefreshToken(models.Model):
    """Model representing refresh tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    expiry_date = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update created_at field"""
        if not self.id:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Refresh token for {self.user.username}"


class PasswordResetToken(models.Model):
    """Model representing password reset tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, unique=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update created_at field"""
        if not self.id:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Password reset token for {self.user.username}"


class TokenBlacklist(models.Model):
    """Model representing blacklisted tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    token = models.CharField(max_length=255, unique=True)
    blacklisted_at = models.DateTimeField(default=timezone.now)
    reason = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """Override save to update blacklisted_at field"""
        if not self.id:
            self.blacklisted_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Blacklisted token for {self.user.username if self.user else 'unknown'}"


class UserCourseCompletion(models.Model):
    """Model representing user course completions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} completed {self.course.title}"


class UserModuleCompletion(models.Model):
    """Model representing user module completions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE)
    completed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} completed {self.module.title}"


class UserLessonCompletion(models.Model):
    """Model representing user lesson completions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(CourseLesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} completed {self.lesson.title}"


class UserTestResult(models.Model):
    """Model representing user test results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(CourseTest, on_delete=models.CASCADE)
    score = models.IntegerField()
    passed = models.BooleanField()
    completed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.test.title}: {self.score}%"


class UserDomainCompletion(models.Model):
    """Model representing user domain completions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.ForeignKey(TrainingDomain, on_delete=models.CASCADE)
    completed_at = models.DateTimeField()
    is_free_access = models.BooleanField(default=False)
    domain_link = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'domain')

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} completed {self.domain.title}"


class ChatConversation(models.Model):
    """Model representing chat conversations"""
    participants = models.ManyToManyField(User, related_name='chat_conversations')
    title = models.CharField(max_length=255, blank=True, null=True)
    is_group_chat = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.is_group_chat and self.title:
            return self.title
        elif self.participants.count() == 2:
            participants = list(self.participants.all())
            return f"Chat between {participants[0].username} and {participants[1].username}"
        else:
            return f"Chat {self.id}"


class ChatMessage(models.Model):
    """Model representing chat messages"""
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Override save to update timestamp field"""
        if not self.id:
            self.timestamp = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation.id}"


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


class Offer(models.Model):
    """Model representing offers for courses/lessons - matches Spring Boot entity"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=1000, null=True)  # Matches Spring Boot length
    price = models.FloatField(null=False)  # Matches Spring Boot Double type
    duration_hours = models.IntegerField(null=False)  # Matches Spring Boot Integer type
    user_type_id = models.BigIntegerField(null=True)  # Matches Spring Boot Long type
    is_active = models.BooleanField(null=False, default=True)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        if not self.id:  # If new record
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'offers'  # Match Spring Boot table name
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'


class UserOffer(models.Model):
    """Model representing user's offer purchases - matches Spring Boot entity"""
    APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
    ]
    
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField(null=False)  # Direct field to match Spring Boot foreign key
    offer_id = models.BigIntegerField(null=False)  # Direct field to match Spring Boot foreign key
    purchase_date = models.DateTimeField(null=False)
    expiration_date = models.DateTimeField(null=False)
    is_active = models.BooleanField(null=False, default=True)
    approval_status = models.CharField(max_length=255, null=False, choices=APPROVAL_STATUS_CHOICES, default='PENDING')  # Matches Spring Boot enum as string
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        """Override save to update updated_at field"""
        if not self.id:  # If new record
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"UserOffer {self.id} - User ID {self.user_id} - Offer ID {self.offer_id} ({self.approval_status})"

    class Meta:
        db_table = 'user_offers'  # Match Spring Boot table name
        verbose_name = 'User Offer'
        verbose_name_plural = 'User Offers'


class SpringBootUser(models.Model):
    """Model representing users from Spring Boot application"""
    ROLE_CHOICES = [
        ('USER', 'User'),
        ('ADMIN', 'Admin'),
    ]
    
    # Core user fields
    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Hashed password
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    
    # Account status fields
    enabled = models.BooleanField(default=True)
    account_non_expired = models.BooleanField(default=True)
    account_non_locked = models.BooleanField(default=True)
    credentials_non_expired = models.BooleanField(default=True)
    
    # Additional fields
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.CharField(max_length=500, blank=True, null=True)
    rgpd_accepted = models.BooleanField(default=False)
    rgpd_accepted_at = models.DateTimeField(blank=True, null=True)
    ccpa_accepted = models.BooleanField(default=False)
    ccpa_accepted_at = models.DateTimeField(blank=True, null=True)
    commercial_use_consent = models.BooleanField(default=False)
    commercial_use_consent_at = models.DateTimeField(blank=True, null=True)
    user_type_id = models.BigIntegerField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
    class Meta:
        db_table = 'users'  # Use the same table name as Spring Boot
        verbose_name = 'Spring Boot User'
        verbose_name_plural = 'Spring Boot Users'
    
    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.email})"
    
    @property
    def username(self):
        return self.email
    
    @property
    def is_active(self):
        return self.enabled

