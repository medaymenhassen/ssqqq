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