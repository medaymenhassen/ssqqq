from django.contrib import admin
from .models import UserProfile, UserType, TrainingDomain, Course, CourseModule, CourseLesson, CourseTest, TestQuestion, TestAnswer, Document, Data, Registration, Location, CalendarEventType, CompanyCalendar, MeetingRequest, ServiceRequest, RefreshToken, PasswordResetToken, TokenBlacklist, UserCourseCompletion, UserModuleCompletion, UserLessonCompletion, UserTestResult, UserDomainCompletion, ChatConversation, ChatMessage, MovementRecord, PoseData, FaceData, HandData, SpringBootUser, Offer, UserOffer

# Register your models here
@admin.register(SpringBootUser)
class SpringBootUserAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email', 'role', 'enabled', 'created_at')
    list_filter = ('role', 'enabled', 'created_at')
    search_fields = ('firstname', 'lastname', 'email')
    readonly_fields = ('created_at', 'updated_at')



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'firstname', 'lastname', 'role', 'enabled', 'created_at')
    list_filter = ('role', 'enabled', 'created_at')
    search_fields = ('firstname', 'lastname', 'user__username', 'user__email')

@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name_fr', 'name_en', 'bigger', 'created_at')
    list_filter = ('bigger', 'created_at')
    search_fields = ('name_fr', 'name_en')

@admin.register(TrainingDomain)
class TrainingDomainAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'student_count', 'display_order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'slug')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')

@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'display_order', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('title', 'user__username')

@admin.register(CourseTest)
class CourseTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'passing_score', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')

@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'course_test', 'question_type', 'points')
    list_filter = ('question_type', 'course_test')
    search_fields = ('question_text',)

@admin.register(TestAnswer)
class TestAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'user')
    search_fields = ('question__question_text', 'user__username')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'user', 'file_type', 'approved', 'uploaded_at')
    list_filter = ('file_type', 'approved', 'uploaded_at')
    search_fields = ('file_name', 'user__username')

@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'movement_detected', 'created_at')
    list_filter = ('movement_detected', 'timestamp')
    search_fields = ('user__username',)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed', 'registered_at')
    list_filter = ('completed', 'registered_at')
    search_fields = ('user__username', 'course__title')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'is_active', 'display_order')
    list_filter = ('is_active', 'location_type')
    search_fields = ('name', 'city', 'country')

@admin.register(CalendarEventType)
class CalendarEventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    search_fields = ('name',)

@admin.register(CompanyCalendar)
class CompanyCalendarAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'event_type', 'start_time', 'end_time')
    list_filter = ('event_type', 'start_time')
    search_fields = ('title', 'company__username')

@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = ('company', 'requester', 'status', 'requested_start_time')
    list_filter = ('status', 'requested_start_time')
    search_fields = ('company__username', 'requester__username')

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'recipient', 'service_type', 'status')
    list_filter = ('service_type', 'status')
    search_fields = ('title', 'provider__username')

@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'expiry_date', 'revoked')
    list_filter = ('revoked', 'expiry_date')
    search_fields = ('user__username',)

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'expires_at', 'is_used', 'created_at')
    list_filter = ('is_used', 'expires_at')
    search_fields = ('user__username',)

@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'blacklisted_at', 'reason')
    list_filter = ('blacklisted_at',)
    search_fields = ('user__username', 'reason')

@admin.register(UserCourseCompletion)
class UserCourseCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('user__username', 'course__title')

@admin.register(UserModuleCompletion)
class UserModuleCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('user__username', 'module__title')

@admin.register(UserLessonCompletion)
class UserLessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('user__username', 'lesson__title')

@admin.register(UserTestResult)
class UserTestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'passed', 'completed_at')
    list_filter = ('passed', 'completed_at')
    search_fields = ('user__username', 'test__title')

@admin.register(UserDomainCompletion)
class UserDomainCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'domain', 'completed_at', 'is_free_access')
    list_filter = ('is_free_access', 'completed_at')
    search_fields = ('user__username', 'domain__title')

@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_group_chat', 'created_at')
    list_filter = ('is_group_chat', 'created_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'content')

@admin.register(MovementRecord)
class MovementRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'timestamp', 'movement_detected', 'created_at')
    list_filter = ('movement_detected', 'created_at', 'timestamp')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'timestamp'

@admin.register(PoseData)
class PoseDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'movement_record', 'body_part', 'x_position', 'y_position', 'created_at')
    list_filter = ('body_part', 'created_at')
    search_fields = ('body_part', 'movement_record__user__username')

@admin.register(FaceData)
class FaceDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'movement_record', 'eye_openness_left', 'eye_openness_right', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('movement_record__user__username',)

@admin.register(HandData)
class HandDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'movement_record', 'hand', 'gesture', 'created_at')
    list_filter = ('hand', 'gesture', 'created_at')
    search_fields = ('hand', 'gesture', 'movement_record__user__username')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'duration_hours', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')



@admin.register(UserOffer)
class UserOfferAdmin(admin.ModelAdmin):
    list_display = ('get_user_info', 'get_offer_info', 'approval_status', 'purchase_date', 'expiration_date', 'is_active')
    list_filter = ('approval_status', 'is_active', 'purchase_date')
    search_fields = ('user_id', 'offer_id', 'offer__title')
    readonly_fields = ('created_at', 'updated_at', 'purchase_date')
    
    def get_user_info(self, obj):
        try:
            user = SpringBootUser.objects.get(id=obj.user_id)
            return f"{user.firstname} {user.lastname} ({user.email})"
        except SpringBootUser.DoesNotExist:
            return f"User ID {obj.user_id} (Not Found)"
    get_user_info.short_description = 'User'
    
    def get_offer_info(self, obj):
        try:
            offer = Offer.objects.get(id=obj.offer_id)
            return f"{offer.title} (€{offer.price})"
        except Offer.DoesNotExist:
            return f"Offer ID {obj.offer_id} (Not Found)"
    get_offer_info.short_description = 'Offer'
    
    actions = ['approve_offers', 'reject_offers']
    
    def approve_offers(self, request, queryset):
        queryset.update(approval_status='APPROVED', is_active=True)
        self.message_user(request, f'{queryset.count()} offers were successfully approved.')
    approve_offers.short_description = "Approve selected offers"
    
    def reject_offers(self, request, queryset):
        queryset.update(approval_status='REJECTED', is_active=False)
        self.message_user(request, f'{queryset.count()} offers were successfully rejected.')
    reject_offers.short_description = "Reject selected offers"
