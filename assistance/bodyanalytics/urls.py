from django.urls import path
from .views import (
    MovementRecordListCreateView,
    MovementRecordDetailView,
    CreateMovementRecordView,
    UserMovementRecordsView,
    EVFAQView,
    UploadMovementDataView,
    # Django Autonomous Views
    DjangoUserListView,
    DjangoUserDetailView,
    DjangoOfferListView,
    DjangoOfferDetailView,
    DjangoUserOfferListView,
    DjangoUserOfferByUserView,
    DjangoCourseLessonListView,
    DjangoCourseLessonDetailView,
    DjangoTestQuestionListView,
    DjangoTestQuestionByTestView,
    ApproveUserOfferView,
    RejectUserOfferView
)

urlpatterns = [
    path('movement-records/', MovementRecordListCreateView.as_view(), name='movement-record-list-create'),
    path('movement-records/<int:pk>/', MovementRecordDetailView.as_view(), name='movement-record-detail'),
    path('movement-records/create/', CreateMovementRecordView.as_view(), name='create-movement-record'),
    path('movement-records/user/<int:user_id>/', UserMovementRecordsView.as_view(), name='user-movement-records'),
    path('movements/upload/', UploadMovementDataView.as_view(), name='upload-movement-data'),
    path('ev-faq/', EVFAQView.as_view(), name='ev-faq'),
    
    
    # Django Autonomous API Endpoints
    path('users/', DjangoUserListView.as_view(), name='django-users-list'),
    path('users/<int:user_id>/', DjangoUserDetailView.as_view(), name='django-user-detail'),
    path('offers/', DjangoOfferListView.as_view(), name='django-offers-list'),
    path('offers/<int:offer_id>/', DjangoOfferDetailView.as_view(), name='django-offer-detail'),
    path('user-offers/', DjangoUserOfferListView.as_view(), name='django-user-offers-list'),
    path('user-offers/user/<int:user_id>/', DjangoUserOfferByUserView.as_view(), name='django-user-offers-by-user'),
    path('course-lessons/', DjangoCourseLessonListView.as_view(), name='django-course-lessons-list'),
    path('course-lessons/<int:lesson_id>/', DjangoCourseLessonDetailView.as_view(), name='django-course-lesson-detail'),
    path('test-questions/', DjangoTestQuestionListView.as_view(), name='django-test-questions-list'),
    path('test-questions/test/<int:test_id>/', DjangoTestQuestionByTestView.as_view(), name='django-test-questions-by-test'),
    path('user-offers/<int:user_offer_id>/approve/', ApproveUserOfferView.as_view(), name='django-approve-user-offer'),
    path('user-offers/<int:user_offer_id>/reject/', RejectUserOfferView.as_view(), name='django-reject-user-offer'),
]