from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import MovementRecord, PoseData, FaceData, HandData
from .serializers import MovementRecordSerializer, MovementRecordCreateSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


class MovementRecordListCreateView(generics.ListCreateAPIView):
    queryset = MovementRecord.objects.all()
    serializer_class = MovementRecordSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return MovementRecord.objects.filter(user_id=user_id)
        return MovementRecord.objects.all()


class MovementRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MovementRecord.objects.all()
    serializer_class = MovementRecordSerializer


@method_decorator(csrf_exempt, name='dispatch')
class CreateMovementRecordView(APIView):
    def post(self, request):
        try:
            # Parse JSON data
            data = request.data
            
            # Create the main movement record
            movement_record_data = {
                'user': data.get('userId'),
                'image_data': data.get('imageData'),
                'video_url': data.get('videoUrl'),
                'json_data': data.get('jsonData'),
                'movement_detected': data.get('movementDetected', False)
            }
            
            serializer = MovementRecordCreateSerializer(data=movement_record_data)
            if serializer.is_valid():
                movement_record = serializer.save()
                
                # If we have detailed JSON data, parse and save it
                json_data = data.get('jsonData')
                if json_data and isinstance(json_data, dict):
                    # Save pose data
                    if 'poseData' in json_data:
                        self.save_pose_data(movement_record, json_data['poseData'])
                    
                    # Save face data
                    if 'faceData' in json_data:
                        self.save_face_data(movement_record, json_data['faceData'])
                    
                    # Save hand data
                    if 'handsData' in json_data:
                        self.save_hand_data(movement_record, json_data['handsData'])
                
                return Response(
                    {'message': 'Movement record created successfully', 'id': movement_record.id},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def save_pose_data(self, movement_record, pose_data):
        if not pose_data:
            return
            
        for body_part, data in pose_data.items():
            if data and 'position' in data:
                position = data['position']
                PoseData.objects.create(
                    movement_record=movement_record,
                    body_part=body_part,
                    x_position=position.get('x', 0),
                    y_position=position.get('y', 0),
                    z_position=position.get('z'),
                    confidence=data.get('confidence')
                )
    
    def save_face_data(self, movement_record, face_data):
        if not face_data:
            return
            
        FaceData.objects.create(
            movement_record=movement_record,
            eye_openness_left=face_data.get('eyeOpenness', {}).get('left'),
            eye_openness_right=face_data.get('eyeOpenness', {}).get('right'),
            mouth_openness=face_data.get('mouthOpenness'),
            head_position_x=face_data.get('headPosition', {}).get('position', {}).get('x'),
            head_position_y=face_data.get('headPosition', {}).get('position', {}).get('y'),
            head_position_z=face_data.get('headPosition', {}).get('position', {}).get('z')
        )
    
    def save_hand_data(self, movement_record, hands_data):
        if not hands_data:
            return
            
        for hand_side, data in hands_data.items():
            if data:
                HandData.objects.create(
                    movement_record=movement_record,
                    hand=hand_side.upper(),
                    gesture=data.get('gesture'),
                    confidence=data.get('confidence'),
                    landmarks=data.get('landmarks')
                )


class UserMovementRecordsView(APIView):
    def get(self, request, user_id):
        try:
            records = MovementRecord.objects.filter(user_id=user_id).order_by('-timestamp')
            serializer = MovementRecordSerializer(records, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
