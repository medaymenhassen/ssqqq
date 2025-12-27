from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import json
import os
from pathlib import Path
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse
from .models import MovementRecord, PoseData, FaceData, HandData
from .serializers import MovementRecordSerializer, MovementRecordCreateSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class MovementRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = MovementRecordSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            return MovementRecord.objects.filter(user_id=user_id)
        return MovementRecord.objects.all()

    def perform_create(self, serializer):
        user_id = self.request.data.get('user')
        if user_id:
            user = User.objects.get(id=user_id)
            serializer.save(user=user)
        else:
            serializer.save()


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


class EVFAQView(APIView):
    def get(self, request):
        """
        Serve the electric vehicle FAQ JSON file
        """
        try:
            # Construct the path to the static JSON file
            base_dir = Path(__file__).resolve().parent.parent
            json_file_path = base_dir / 'static' / 'electric-vehicle-faq.json'
            
            # Check if the file exists
            if not json_file_path.exists():
                return JsonResponse(
                    {'error': 'FAQ file not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Read the JSON file
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            return JsonResponse(data, safe=False)
        
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid JSON in FAQ file'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return JsonResponse(
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


@method_decorator(csrf_exempt, name='dispatch')
class UploadMovementDataView(APIView):
    """
    Endpoint pour télécharger les données de mouvement avec images
    """
    
    def post(self, request):
        try:
            # ========== 1. EXTRAIRE LES MÉTADONNÉES ==========
            user_id = request.data.get('user')
            label = request.data.get('label', 'Movement Capture')
            movement_type = request.data.get('movementType', 'general')
            timestamp_str = request.data.get('timestamp')
            json_data_str = request.data.get('jsonData')
            
            # ========== 2. VALIDER L'UTILISATEUR ==========
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': f'User with ID {user_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid user ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ========== 3. PARSER LES DONNÉES JSON ==========
            json_data = {}
            if json_data_str:
                try:
                    json_data = json.loads(json_data_str)
                except json.JSONDecodeError as e:
                    json_data = {}
            
            # ========== 4. CRÉER LE MOUVEMENT RECORD ==========
            movement_record = MovementRecord.objects.create(
                user=user,
                timestamp=timezone.now(),
                movement_detected=True,
                json_data={
                    'label': label,
                    'movement_type': movement_type,
                    'original_timestamp': timestamp_str,
                    # Inclure les données de pose/face/mains
                    'pose_data': json_data.get('poseData'),
                    'face_data': json_data.get('faceData'),
                    'hands_data': json_data.get('handsData'),
                    'confidence': json_data.get('confidence'),
                    'body_metrics': json_data.get('bodyMetrics')
                }
            )
            
            # ========== 5. TRAITER LES IMAGES ==========
            images = request.FILES.getlist('images')
            image_urls = []
            
            for i, image in enumerate(images):
                # Limiter le nombre d'images traitées par requête
                if i >= 5:  # Maximum 5 images par requête
                    break
                
                try:
                    # Générer un nom de fichier unique
                    timestamp_ms = int(timezone.now().timestamp() * 1000)
                    
                    # Format: date/userid/movement_type/images
                    date_str = timezone.now().strftime('%Y-%m-%d')  # Format: 2025-12-27
                    user_id = movement_record.user.id
                    movement_type = movement_record.json_data.get('movement_type', 'general')
                    
                    filename = f"movement_images/{date_str}/{user_id}/{movement_type}/{i}_{timestamp_ms}_{image.name}"
                    
                    # Sauvegarder l'image
                    path = default_storage.save(filename, ContentFile(image.read()))
                    image_url = default_storage.url(path)
                    image_urls.append(image_url)
                    

                    
                except Exception as e:
                    continue
            
            # ========== 6. SAUVEGARDER LES DONNÉES DÉTAILLÉES ==========
            if json_data:
                # Sauvegarder les données de pose
                if 'poseData' in json_data and json_data['poseData']:
                    self._save_pose_data(movement_record, json_data['poseData'])
                
                # Sauvegarder les données de face
                if 'faceData' in json_data and json_data['faceData']:
                    self._save_face_data(movement_record, json_data['faceData'])
                
                # Sauvegarder les données de mains
                if 'handsData' in json_data and json_data['handsData']:
                    self._save_hand_data(movement_record, json_data['handsData'])
            
            # ========== 7. RÉPONDRE ==========
            return Response({
                'message': 'Movement data uploaded successfully',
                'movement_record_id': movement_record.id,
                'image_count': len(image_urls),
                'image_urls': image_urls,
                'user_id': user_id,
                'timestamp': movement_record.timestamp.isoformat()
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e), 'detail': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ========== HELPER METHODS ==========
    
    def _save_pose_data(self, movement_record, pose_data):
        """Sauvegarder les données de pose détaillées"""
        if not pose_data or not isinstance(pose_data, dict):
            return
        
        for body_part, data in pose_data.items():
            try:
                if data and isinstance(data, dict) and 'position' in data:
                    position = data.get('position', {})
                    
                    PoseData.objects.create(
                        movement_record=movement_record,
                        body_part=str(body_part),
                        x_position=float(position.get('x', 0)),
                        y_position=float(position.get('y', 0)),
                        z_position=float(position.get('z')) if position.get('z') is not None else None,
                        confidence=float(data.get('confidence', 0)) if data.get('confidence') else None
                    )
            except Exception as e:
                continue

    def _save_face_data(self, movement_record, face_data):
        """Sauvegarder les données de face détaillées"""
        if not face_data or not isinstance(face_data, dict):
            return
        
        try:
            eye_openness = face_data.get('eyeOpenness', {})
            head_position = face_data.get('headPosition', {}).get('position', {})
            
            FaceData.objects.create(
                movement_record=movement_record,
                eye_openness_left=float(eye_openness.get('left')) if eye_openness.get('left') is not None else None,
                eye_openness_right=float(eye_openness.get('right')) if eye_openness.get('right') is not None else None,
                mouth_openness=float(face_data.get('mouthOpenness')) if face_data.get('mouthOpenness') is not None else None,
                head_position_x=float(head_position.get('x')) if head_position.get('x') is not None else None,
                head_position_y=float(head_position.get('y')) if head_position.get('y') is not None else None,
                head_position_z=float(head_position.get('z')) if head_position.get('z') is not None else None
            )
        except Exception as e:
            pass
    
    def _save_hand_data(self, movement_record, hands_data):
        """Sauvegarder les données de mains détaillées"""
        if not hands_data or not isinstance(hands_data, dict):
            return
        
        for hand_side, data in hands_data.items():
            try:
                if data and isinstance(data, dict):
                    HandData.objects.create(
                        movement_record=movement_record,
                        hand=str(hand_side).upper(),
                        gesture=str(data.get('gesture')) if data.get('gesture') else None,
                        confidence=float(data.get('confidence')) if data.get('confidence') else None,
                    )
            except Exception as e:
                continue
