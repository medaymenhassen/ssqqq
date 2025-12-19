from django.urls import path
from .views import (
    MovementRecordListCreateView,
    MovementRecordDetailView,
    CreateMovementRecordView,
    UserMovementRecordsView
)

urlpatterns = [
    path('movement-records/', MovementRecordListCreateView.as_view(), name='movement-record-list-create'),
    path('movement-records/<int:pk>/', MovementRecordDetailView.as_view(), name='movement-record-detail'),
    path('movement-records/create/', CreateMovementRecordView.as_view(), name='create-movement-record'),
    path('movement-records/user/<int:user_id>/', UserMovementRecordsView.as_view(), name='user-movement-records'),
]