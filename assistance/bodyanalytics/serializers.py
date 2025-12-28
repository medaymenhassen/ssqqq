from rest_framework import serializers
from .models import Data as MovementRecord


class MovementRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovementRecord
        fields = '__all__'


class MovementRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovementRecord
        fields = ['user', 'image_data', 'video_url', 'json_data', 'movement_detected']