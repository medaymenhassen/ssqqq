# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ChatConversations(models.Model):
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user_id = models.BigIntegerField(unique=True)
    conversation = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'chat_conversations'


class CompanyCalendars(models.Model):
    is_available = models.BooleanField(blank=True, null=True)
    company = models.ForeignKey('Users', on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    end_time = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    start_time = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    event_type = models.CharField(max_length=255, blank=True, null=True)
    meeting_link = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)

    class Meta:

        db_table = 'company_calendars'


class CourseLessons(models.Model):
    display_order = models.IntegerField(blank=True, null=True)
    is_service = models.BooleanField(blank=True, null=True)
    lesson_order = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    description = models.CharField(max_length=1000, blank=True, null=True)
    content_description = models.CharField(max_length=2000, blank=True, null=True)
    animation_3d_url = models.CharField(max_length=255, blank=True, null=True)
    content_title = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    video_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:

        db_table = 'course_lessons'


class CourseModules(models.Model):
    course = models.ForeignKey('Courses', on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    title = models.CharField(max_length=255)

    class Meta:

        db_table = 'course_modules'


class CourseTests(models.Model):
    passing_score = models.IntegerField(blank=True, null=True)
    time_limit_minutes = models.IntegerField(blank=True, null=True)
    course = models.ForeignKey('Courses', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    title = models.CharField(max_length=255)

    class Meta:

        db_table = 'course_tests'


class Courses(models.Model):
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    title = models.CharField(max_length=255)

    class Meta:

        db_table = 'courses'


class Data(models.Model):
    movement_detected = models.BooleanField()
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    video_url = models.CharField(max_length=255, blank=True, null=True)
    image_data = models.TextField(blank=True, null=True)  # This field type is a guess.
    json_data = models.TextField(blank=True, null=True)

    class Meta:

        db_table = 'data'


class Documents(models.Model):
    approved = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    file_size = models.BigIntegerField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    test_answer = models.ForeignKey('TestAnswers', on_delete=models.CASCADE, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    uploaded_at = models.DateTimeField()
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    user_type = models.ForeignKey('UserTypes', on_delete=models.CASCADE, blank=True, null=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    file_type = models.CharField(max_length=255)

    class Meta:

        db_table = 'documents'


class Locations(models.Model):
    display_order = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    location_type = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=500)
    description = models.CharField(max_length=1000, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)

    class Meta:

        db_table = 'locations'


class MeetingRequests(models.Model):
    calendar_event = models.ForeignKey(CompanyCalendars, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey('Users', on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    proposed_end_time = models.DateTimeField(blank=True, null=True)
    proposed_start_time = models.DateTimeField(blank=True, null=True)
    requested_end_time = models.DateTimeField()
    requested_start_time = models.DateTimeField()
    requester = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='meetingrequests_requester_set')
    updated_at = models.DateTimeField(blank=True, null=True)
    company_notes = models.CharField(max_length=1000, blank=True, null=True)
    notes = models.CharField(max_length=1000, blank=True, null=True)
    meeting_link = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:

        db_table = 'meeting_requests'


class Offers(models.Model):
    duration_hours = models.IntegerField()
    is_active = models.BooleanField()
    price = models.FloatField()
    created_at = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user_type_id = models.BigIntegerField(blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    title = models.CharField(max_length=255)

    class Meta:

        db_table = 'offers'


class PasswordResetTokens(models.Model):
    is_used = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    token = models.CharField(unique=True, max_length=500)

    class Meta:

        db_table = 'password_reset_tokens'


class RefreshTokens(models.Model):
    revoked = models.BooleanField()
    created_at = models.DateTimeField()
    expiry_date = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    token = models.CharField(unique=True, max_length=255)

    class Meta:

        db_table = 'refresh_tokens'


class Registrations(models.Model):
    completed = models.BooleanField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    registered_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:

        db_table = 'registrations'


class ServiceRequests(models.Model):
    is_open_to_all = models.BooleanField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    provider = models.ForeignKey('Users', on_delete=models.CASCADE)
    rated_at = models.DateTimeField(blank=True, null=True)
    recipient = models.ForeignKey('Users', on_delete=models.CASCADE, related_name='servicerequests_recipient_set', blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    comment = models.CharField(max_length=2000, blank=True, null=True)
    service_type = models.CharField(max_length=255)
    status = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)

    class Meta:

        db_table = 'service_requests'


class TestAnswers(models.Model):
    answer_order = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    question = models.ForeignKey('TestQuestions', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=1000, blank=True, null=True)
    is_correct = models.CharField(max_length=255, blank=True, null=True)
    is_logical = models.CharField(max_length=255, blank=True, null=True)

    class Meta:

        db_table = 'test_answers'


class TestQuestions(models.Model):
    points = models.IntegerField(blank=True, null=True)
    question_order = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    lesson = models.ForeignKey(CourseLessons, on_delete=models.CASCADE, blank=True, null=True)
    test = models.ForeignKey(CourseTests, on_delete=models.CASCADE, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=1000)
    expected_answer_type = models.CharField(max_length=255, blank=True, null=True)
    question_type = models.CharField(max_length=255)

    class Meta:

        db_table = 'test_questions'


class TokenBlacklist(models.Model):
    blacklisted_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE, blank=True, null=True)
    reason = models.CharField(max_length=255)
    token = models.CharField(unique=True, max_length=255)

    class Meta:

        db_table = 'token_blacklist'


class TrainingDomains(models.Model):
    display_order = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    student_count = models.BigIntegerField()
    updated_at = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=1000)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(unique=True, max_length=255)
    title = models.CharField(max_length=255)

    class Meta:

        db_table = 'training_domains'


class UserCourseCompletions(models.Model):
    completed_at = models.DateTimeField(blank=True, null=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)

    class Meta:

        db_table = 'user_course_completions'


class UserDomainCompletions(models.Model):
    is_free_access = models.BooleanField(blank=True, null=True)
    completed_at = models.DateTimeField()
    created_at = models.DateTimeField()
    domain = models.ForeignKey(TrainingDomains, on_delete=models.CASCADE)
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    domain_link = models.CharField(max_length=500, blank=True, null=True)

    class Meta:

        db_table = 'user_domain_completions'
        unique_together = (('user', 'domain'),)


class UserLessonCompletions(models.Model):
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    lesson = models.ForeignKey(CourseLessons, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)

    class Meta:

        db_table = 'user_lesson_completions'


class UserModuleCompletions(models.Model):
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    module = models.ForeignKey(CourseModules, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)

    class Meta:

        db_table = 'user_module_completions'


class UserOffers(models.Model):
    is_active = models.BooleanField()
    created_at = models.DateTimeField(blank=True, null=True)
    expiration_date = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    offer = models.ForeignKey(Offers, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)
    approval_status = models.CharField(max_length=255)

    class Meta:

        db_table = 'user_offers'


class UserTestResults(models.Model):
    passed = models.BooleanField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    test = models.ForeignKey(CourseTests, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)

    class Meta:

        db_table = 'user_test_results'


class UserTypeDefinitionBackup(models.Model):
    display_order = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    show_in_selection = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    description_en = models.CharField(max_length=500, blank=True, null=True)
    description_fr = models.CharField(max_length=500, blank=True, null=True)
    bigger = models.CharField(max_length=255)
    company_type = models.CharField(max_length=255, blank=True, null=True)
    label_en = models.CharField(max_length=255)
    label_fr = models.CharField(max_length=255)
    type_code = models.CharField(unique=True, max_length=255)

    class Meta:

        db_table = 'user_type_definition_backup'


class UserTypes(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    desc_en = models.CharField(max_length=500, blank=True, null=True)
    desc_fr = models.CharField(max_length=500, blank=True, null=True)
    bigger = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    name_fr = models.CharField(max_length=255)

    class Meta:

        db_table = 'user_types'


class Users(models.Model):
    account_non_expired = models.BooleanField()
    account_non_locked = models.BooleanField()
    ccpa_accepted = models.BooleanField(blank=True, null=True)
    commercial_use_consent = models.BooleanField(blank=True, null=True)
    credentials_non_expired = models.BooleanField()
    enabled = models.BooleanField()
    is_blocked = models.BooleanField(blank=True, null=True)
    rgpd_accepted = models.BooleanField(blank=True, null=True)
    ccpa_accepted_at = models.DateTimeField(blank=True, null=True)
    commercial_use_consent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    id = models.BigAutoField(primary_key=True)
    rgpd_accepted_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    user_type = models.ForeignKey('UserTypes', on_delete=models.CASCADE, blank=True, null=True)
    blocked_reason = models.CharField(max_length=500, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'users'

