from rest_framework import serializers
from .models import MovementRecord, PoseData, FaceData, HandData


class PoseDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoseData
        fields = '__all__'


class FaceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceData
        fields = '__all__'


class HandDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HandData
        fields = '__all__'


class MovementRecordSerializer(serializers.ModelSerializer):
    pose_data = PoseDataSerializer(many=True, read_only=True)
    face_data = FaceDataSerializer(many=True, read_only=True)
    hand_data = HandDataSerializer(many=True, read_only=True)

    class Meta:
        model = MovementRecord
        fields = '__all__'


class MovementRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovementRecord
        fields = ['user', 'image_data', 'video_url', 'json_data', 'movement_detected']