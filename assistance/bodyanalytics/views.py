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
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import Data as MovementRecord, Offers as Offer, UserOffers as UserOffer, CourseLessons as CourseLesson, TestQuestions as TestQuestion, Users as SpringBootUser
from .serializers import MovementRecordSerializer, MovementRecordCreateSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
import json
import time
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
            
            # Get user from either userId field or user field
            user_id = data.get('userId') or data.get('user')
            
            # Create the main movement record
            movement_record_data = {
                'user_id': user_id,
                'image_data': data.get('imageData'),
                'video_url': data.get('videoUrl'),
                'json_data': data.get('jsonData'),
                'movement_detected': data.get('movementDetected', False)
            }
            
            # Remove None values to avoid validation errors
            movement_record_data = {k: v for k, v in movement_record_data.items() if v is not None}
            
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
        # Backend does not analyze pose data
        # All analysis is done in frontend and sent to backend
        # This method does nothing as per requirements
        pass
    
    def save_face_data(self, movement_record, face_data):
        # Face detection and detailed face data processing happens in frontend
        # Backend only receives and stores the processed data
        # No FaceData model exists, so this functionality is handled differently
        pass
    
    def save_hand_data(self, movement_record, hands_data):
        # Backend does not analyze hand data
        # All analysis is done in frontend and sent to backend
        # This method does nothing as per requirements
        pass


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
            # Check if user_id is provided in request data
            if user_id is None:
                # Try to get user ID from headers if not in request data
                user_id = request.META.get('HTTP_X_USER_ID')
                if user_id is None:
                    # Try to get user ID from a different field name that might be used
                    user_id = request.data.get('userId') or request.data.get('user_id')
            
            label = request.data.get('label', 'Movement Capture')
            movement_type = request.data.get('movementType', 'general')
            timestamp_str = request.data.get('timestamp')
            json_data_str = request.data.get('jsonData')
            
            # ========== 2. VALIDER L'UTILISATEUR ==========
            if user_id is None:
                return Response(
                    {'error': 'User ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = SpringBootUser.objects.get(id=user_id)
            except SpringBootUser.DoesNotExist:
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
            
            # ========== 4. CRÉER LE MOUVEMENT RECORD (SIMPLIFIED) ==========
            # Create with minimal data to avoid database column type issues
            # Note: json_data field is OID type, so we won't store JSON in it to avoid errors
            # However, we'll extract essential information for image organization
            essential_json_data = {}
            if json_data:
                # Extract only the key information needed for movement classification
                essential_json_data['detection_type'] = json_data.get('detection_type', 'general')
                essential_json_data['movement_name'] = json_data.get('movement_name', 'general_movement')
                essential_json_data['timestamp'] = json_data.get('timestamp')
                essential_json_data['hasFace'] = 'faceData' in json_data and json_data['faceData'] is not None
                essential_json_data['hasPose'] = 'poseData' in json_data and json_data['poseData'] is not None
                essential_json_data['hasHands'] = 'handsData' in json_data and json_data['handsData'] is not None
                
                # Add expression or gesture info if available
                if json_data.get('faceData') and 'expression' in json_data['faceData']:
                    essential_json_data['expression'] = json_data['faceData']['expression']
                
                if json_data.get('handsData'):
                    # Extract hand gesture info
                    hands_info = []
                    for hand in json_data['handsData']:
                        hands_info.append({
                            'handedness': hand.get('handedness'),
                            'gesture': hand.get('gesture')
                        })
                    essential_json_data['hands_info'] = hands_info
            
            # Create the json_data_dict first
            json_data_dict = {
                'label': label,
                'movement_type': movement_type,
                'original_timestamp': timestamp_str,
                'image_urls': [],  # Will be populated after image saving
                'image_order': 0,  # Will be set during image processing
                'detected_movements': {
                    'detection_type': json_data.get('detection_type', 'general'),
                    'movement_name': json_data.get('movement_name', 'general_movement'),
                    'hasFace': 'faceData' in json_data and json_data['faceData'] is not None,
                    'hasPose': 'poseData' in json_data and json_data['poseData'] is not None,
                    'hasHands': 'handsData' in json_data and json_data['handsData'] is not None,
                    'confidence': json_data.get('confidence'),
                    'body_metrics': json_data.get('bodyMetrics'),
                }
            }
            
            # ========== 5. TRAITER LES IMAGES (Before creating record) ==========
            images = request.FILES.getlist('images')
            image_urls = []
            
            # Extract movement type and name from the JSON data for the entire batch
            # This ensures all images in the batch use the same detection type
            detection_type = 'general'
            movement_name = 'general_movement'
            
            print(f"RECEIVED: Raw json_data keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
            
            # Log basic information about the received data
            if isinstance(json_data, dict):
                print(f"RECEIVED: faceData present: {'faceData' in json_data}")
                print(f"RECEIVED: handsData present: {'handsData' in json_data}")
                print(f"RECEIVED: poseData present: {'poseData' in json_data}")
                print(f"RECEIVED: detection_type: {json_data.get('detection_type', 'None')}")
                print(f"RECEIVED: movement_name: {json_data.get('movement_name', 'None')}")
            
            if json_data and isinstance(json_data, dict):
                # Try various possible field names that Angular might send
                # Prioritize explicit detection fields over generic ones
                # Get initial values from the main data fields
                initial_detection_type = (
                    json_data.get('detection_type') or
                    json_data.get('detectionType') or
                    json_data.get('type') or
                    json_data.get('movementType') or
                    json_data.get('movement_type') or
                    json_data.get('gesture') or  # This might be the actual gesture name
                    'general'
                )
                
                initial_movement_name = (
                    json_data.get('detectedGesture') or      # Most specific - actual detected gesture
                    json_data.get('detectedExpression') or   # Most specific - actual detected expression
                    json_data.get('detected_movement') or    # Most specific - actual detected movement
                    json_data.get('handGesture') or          # Hand-specific gesture name
                    json_data.get('faceExpression') or       # Face-specific expression name
                    json_data.get('hand_gesture') or         # Hand-specific gesture name
                    json_data.get('face_expression') or      # Face-specific expression name
                    json_data.get('movement_name') or
                    json_data.get('movementName') or
                    json_data.get('expression') or
                    json_data.get('gesture') or
                    json_data.get('action') or
                    json_data.get('movement') or
                    json_data.get('pose') or
                    'general_movement'
                )
                
                # Initialize with initial values but allow refinement
                detection_type = initial_detection_type
                movement_name = initial_movement_name
                
                print(f"DEBUG: Initial values - detection_type: {detection_type}, movement_name: {movement_name}")
                
                print(f"DEBUG: Initial detection_type: {detection_type}, movement_name: {movement_name}")
                
                # Only allow refinement if initial values are generic
                should_refine_detection_type = detection_type in ['general', 'active_capture']
                should_refine_movement_name = movement_name in ['general_movement', 'active_capture', 'unknown', 'neutral', 'surprised']
                
                # Preserve any specific movement name that comes from Angular, regardless of language
                # If it's not a generic name, keep it as is
                if movement_name not in ['general_movement', 'active_capture', 'unknown', 'neutral', 'general']:
                    should_refine_movement_name = False
                    print(f"RECEIVED: Preserving specific movement from Angular: {movement_name}")
                
                # Always check for specific data presence regardless of initial detection_type
                print(f"DEBUG: Checking for specific data in json_data keys: {list(json_data.keys())}")
                
                # Check for face data presence and extract specific expression
                face_data = json_data.get('faceData')
                if face_data and face_data is not None:
                    print(f"DEBUG: Face data detected: {type(face_data)}, keys: {list(face_data.keys()) if isinstance(face_data, dict) else 'N/A'}")
                    # Extract facial expression from face data
                    if isinstance(face_data, dict):
                        # Check for emotion/expressions in face data
                        expression = face_data.get('expression') or face_data.get('emotion') or face_data.get('gesture')
                        # Check if expression is nested inside face_data
                        if expression is None and 'expression' in face_data:
                            expression = face_data['expression']
                        elif expression is None and 'emotion' in face_data:
                            expression = face_data['emotion']
                        elif expression is None and 'gesture' in face_data:
                            expression = face_data['gesture']
                        print(f"DEBUG: Face expression found: {expression}")
                        if expression and should_refine_movement_name:
                            movement_name = str(expression).lower()
                            print(f"DEBUG: Updated movement_name from face data: {movement_name}")
                        # Only update detection_type to face if we should refine and we don't have a more specific detection already
                        if should_refine_detection_type and detection_type in ['general']:
                            detection_type = 'face'
                
                # Check for hands data presence and extract specific gesture
                hands_data = json_data.get('handsData')
                if hands_data and hands_data is not None and len(hands_data) > 0:
                    print(f"DEBUG: Hands data detected: {type(hands_data)}, length: {len(hands_data) if hasattr(hands_data, '__len__') else 'N/A'}")
                    # Only update detection_type to hand if we should refine and we don't have a more specific detection already
                    if should_refine_detection_type and detection_type in ['general']:
                        detection_type = 'hand'
                    # Try to extract specific hand gesture, regardless of current movement_name
                    if isinstance(hands_data, list) and len(hands_data) > 0:
                        first_hand = hands_data[0]
                        if isinstance(first_hand, dict):
                            # Look for gesture, action, or expression in hand data
                            gesture = first_hand.get('gesture') or first_hand.get('action') or first_hand.get('movement')
                            handedness = first_hand.get('handedness', '')
                            print(f"DEBUG: Hand gesture found: {gesture}, handedness: {handedness}")
                            if gesture and should_refine_movement_name:
                                movement_name = str(gesture).lower()
                                print(f"DEBUG: Updated movement_name from hand data: {movement_name}")
                            else:
                                # Try to get handedness and gesture
                                if handedness and should_refine_movement_name:
                                    movement_name = f"{handedness}_gesture"
                                    print(f"DEBUG: Updated movement_name from handedness: {movement_name}")
                                else:
                                    movement_name = 'hand_gesture'
                    elif isinstance(hands_data, dict):
                        # If it's a dict, check for gesture
                        gesture = hands_data.get('gesture') or hands_data.get('action') or hands_data.get('movement')
                        print(f"DEBUG: Hand gesture found: {gesture}")
                        if gesture and should_refine_movement_name:
                            movement_name = str(gesture).lower()
                            print(f"DEBUG: Updated movement_name from hand data: {movement_name}")
                        else:
                            movement_name = 'hand_gesture'
                    else:
                        movement_name = 'hand_gesture'
                
                # Check for pose data presence and extract specific pose
                pose_data = json_data.get('poseData')
                if pose_data and pose_data is not None and len(pose_data) > 0:
                    print(f"DEBUG: Pose data detected: {type(pose_data)}, length: {len(pose_data) if hasattr(pose_data, '__len__') else 'N/A'}")
                    # Only update detection_type to pose if we should refine and we don't have a more specific detection already
                    if should_refine_detection_type and detection_type in ['general']:
                        detection_type = 'pose'
                    # Try to extract specific pose from pose data, regardless of current movement_name
                    if isinstance(pose_data, dict):
                        # Look for pose name, action, or movement in pose data
                        pose_name = pose_data.get('pose') or pose_data.get('action') or pose_data.get('movement')
                        print(f"DEBUG: Pose name found: {pose_name}")
                        if pose_name and should_refine_movement_name:
                            movement_name = str(pose_name).lower()
                            print(f"DEBUG: Updated movement_name from pose data: {movement_name}")
                        # Only default to 'body_pose' if we should refine and we don't have a more specific movement_name already
                        elif should_refine_movement_name and movement_name in ['general_movement', 'active_capture', 'unknown', 'neutral']:
                            movement_name = 'body_pose'
                    # If pose_data is not a dict but we have pose data, default to 'body_pose'
                    elif should_refine_movement_name and movement_name in ['general_movement', 'active_capture', 'unknown', 'neutral']:
                        movement_name = 'body_pose'
            
            print(f"DEBUG: Final detection_type: {detection_type}, movement_name: {movement_name}")
            
            # Log the final processed result
            print(f"PROCESSED: Final detection_type: {detection_type}, movement_name: {movement_name}")
            
            # Set subcategory based on detection type
            subcategory = detection_type
            
            # Clean names for use in file paths
            # Replace special characters and spaces
            import re
            detection_type = re.sub(r'[^a-zA-Z0-9_]', '_', detection_type.lower())
            subcategory = re.sub(r'[^a-zA-Z0-9_]', '_', subcategory.lower())
            movement_name = re.sub(r'[^a-zA-Z0-9_]', '_', movement_name.lower())
            
            print(f"DEBUG: After cleaning - detection_type: {detection_type}, subcategory: {subcategory}, movement_name: {movement_name}")
            
            for i, image in enumerate(images):
                # Limiter le nombre d'images traitées par requête
                if i >= 5:  # Maximum 5 images par requête
                    break
                
                try:
                    # Générer un nom de fichier unique
                    timestamp_ms = int(timezone.now().timestamp() * 1000)
                    
                    # Simply use the movement information received from frontend
                    # Backend does not analyze movements, only organizes based on received data
                    
                    # Format: active_capture/detection_type/subcategory/movement_name/images
                    filename = f"active_capture/{detection_type}/{subcategory}/{movement_name}/{i}_{timestamp_ms}_{image.name}"
                    
                    # Sauvegarder l'image
                    path = default_storage.save(filename, ContentFile(image.read()))
                    image_url = default_storage.url(path)
                    image_urls.append(image_url)
                    
                except Exception as e:
                    print(f"Error saving image: {str(e)}")
                    # Continuer avec les autres images même si une échoue
                    continue
            
            # Update json_data_dict with the processed image information
            json_data_dict['image_urls'] = image_urls
            json_data_dict['image_order'] = len(image_urls) - 1 if image_urls else 0
            
            # Check if there's an existing session record for this user with the same label/timestamp
            # This allows grouping multiple captures from the same session
            # Use text-based search instead of JSON operators
            existing_record = MovementRecord.objects.filter(
                user=user,
                json_data__icontains=label  # Look for records containing the same label in the text
            ).order_by('-created_at').first()
            
            # If we find an existing record from the same session, update it instead of creating a new one
            if existing_record:
                # Load existing JSON data
                try:
                    import ast
                    # Try to parse as JSON, fallback to literal_eval if needed
                    try:
                        existing_json_data = json.loads(existing_record.json_data) if existing_record.json_data else {}
                    except (json.JSONDecodeError, TypeError):
                        existing_json_data = ast.literal_eval(existing_record.json_data) if existing_record.json_data else {}
                except:
                    existing_json_data = {}
                
                # Merge the new image data with existing ones
                # Create new image entries with landmarks and movement data for each image
                for i, image_url in enumerate(image_urls):
                    # Create a data entry for each image with its landmarks and movements
                    image_data_entry = {
                        'image_url': image_url,
                        'timestamp': timestamp_str,
                        'detected_movements': json_data_dict.get('detected_movements', {}),
                        # Include landmark data if available in the original json_data
                        'landmarks': {
                            'face': json_data.get('faceData', None),
                            'pose': json_data.get('poseData', None),
                            'hands': json_data.get('handsData', None)
                        } if json_data else {}
                    }
                    
                    # Add this image data to existing entries
                    if 'image_data' not in existing_json_data:
                        existing_json_data['image_data'] = []
                    existing_json_data['image_data'].append(image_data_entry)
                
                # Update the existing record with merged data
                try:
                    existing_record.json_data = json.dumps(existing_json_data, ensure_ascii=False, separators=(',', ':'), default=str)
                    existing_record.save()
                    movement_record = existing_record
                except Exception as e:
                    print(f"Error updating json_data in existing movement record: {e}")
                    # If update fails, still use the existing record
                    movement_record = existing_record
            else:
                # Create movement record with the fully populated json_data_dict
                # The json_data_dict now includes actual image URLs, count, and detected movements
                # Handle field type by converting to JSON string first
                try:
                    # Convert the dictionary to a JSON string for storage
                    json_data_str = json.dumps(json_data_dict, ensure_ascii=False, separators=(',', ':'), default=str)
                    movement_record = MovementRecord.objects.create(
                        user=user,
                        timestamp=timezone.now(),
                        movement_detected=True,
                        created_at=timezone.now(),  # Set required field
                        json_data=json_data_str  # Store as JSON string with actual image URLs
                    )
                except Exception as e:
                    # If json_data field type doesn't accept the JSON, create without it
                    print(f"Error saving json_data to movement record: {e}")
                    movement_record = MovementRecord.objects.create(
                        user=user,
                        timestamp=timezone.now(),
                        movement_detected=True,
                        created_at=timezone.now(),  # Set required field
                        json_data=None  # Fallback to None if can't store the dict
                    )
            
            # ========== 6. RÉPONDRE ==========
            return Response({
                'message': 'Movement data uploaded successfully',
                'movement_record_id': movement_record.id,
                'image_count': len(image_urls),
                'image_urls': image_urls,
                'user_id': user_id,
                'timestamp': movement_record.timestamp.isoformat()
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            import traceback
            print(f"ERROR in upload: {str(e)}")
            print(f"TRACEBACK: {traceback.format_exc()}")
            return Response(
                {'error': str(e), 'detail': 'Internal server error', 'traceback': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # ========== HELPER METHODS ==========
    
    def _save_pose_data(self, movement_record, pose_data):
        # Backend does not analyze pose data
        # All analysis is done in frontend and sent to backend
        # This method does nothing as per requirements
        pass


# ========== DJANGO AUTHENTICATION VIEWS ==========

class DjangoLoginView(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            
            # For now, we'll implement a simplified authentication
            # In a real scenario, you might want to call Spring Boot's authentication API
            # or implement a shared authentication mechanism
            
            # For demonstration purposes, we'll just check if the user exists
            # and set up a Django session
            try:
                user = SpringBootUser.objects.get(email=email, enabled=True)
                # Since we can't verify Spring Boot's password hash, we'll just log the user in
                # if they exist in the database and are enabled
                request.session['user_id'] = user.id
                request.session['user_email'] = user.email
                
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'role': user.role,
                    'is_authenticated': True
                }
                return Response(user_data)
            except SpringBootUser.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoCurrentUserView(APIView):
    def get(self, request):
        # This view will return the current user based on session
        user_id = request.session.get('user_id')
        user_email = request.session.get('user_email')
        
        if user_id and user_email:
            try:
                user = SpringBootUser.objects.get(id=user_id, email=user_email, enabled=True)
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'role': user.role,
                    'is_authenticated': True
                }
                return Response(user_data)
            except SpringBootUser.DoesNotExist:
                # Clear the session if user doesn't exist
                if 'user_id' in request.session:
                    del request.session['user_id']
                if 'user_email' in request.session:
                    del request.session['user_email']
        
        return Response({'is_authenticated': False}, status=status.HTTP_401_UNAUTHORIZED)


# ========== DJANGO AUTONOMOUS VIEWS ==========

class DjangoUserListView(APIView):
    def get(self, request):
        try:
            # Get user info from headers
            user_id = request.META.get('HTTP_X_USER_ID')
            user_email = request.META.get('HTTP_X_USER_EMAIL')
            
            # For now, return all users (later we can filter based on permissions)
            users = SpringBootUser.objects.all()
            result = []
            for user in users:
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'role': user.role,
                    'enabled': user.enabled,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                }
                result.append(user_data)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoUserDetailView(APIView):
    def get(self, request, user_id):
        try:
            # Get requesting user info from headers
            requesting_user_id = request.META.get('HTTP_X_USER_ID')
            requesting_user_email = request.META.get('HTTP_X_USER_EMAIL')
            
            # Check if requesting user has permission to access this user's data
            # For now, allow access to any user data (you can add more sophisticated permission checks)
            user = SpringBootUser.objects.get(id=user_id)
            user_data = {
                'id': user.id,
                'email': user.email,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'role': user.role,
                'enabled': user.enabled,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            }
            return Response(user_data)
        except SpringBootUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoOfferListView(APIView):
    def get(self, request):
        try:
            offers = Offer.objects.all()
            result = []
            for offer in offers:
                offer_data = {
                    'id': offer.id,
                    'title': offer.title,
                    'description': offer.description,
                    'price': offer.price,
                    'duration_hours': offer.duration_hours,
                    'is_active': offer.is_active,
                    'created_at': offer.created_at.isoformat() if offer.created_at else None,
                    'updated_at': offer.updated_at.isoformat() if offer.updated_at else None,
                }
                result.append(offer_data)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoOfferDetailView(APIView):
    def get(self, request, offer_id):
        try:
            offer = Offer.objects.get(id=offer_id)
            offer_data = {
                'id': offer.id,
                'title': offer.title,
                'description': offer.description,
                'price': offer.price,
                'duration_hours': offer.duration_hours,
                'is_active': offer.is_active,
                'created_at': offer.created_at.isoformat() if offer.created_at else None,
                'updated_at': offer.updated_at.isoformat() if offer.updated_at else None,
            }
            return Response(offer_data)
        except Offer.DoesNotExist:
            return Response({'error': 'Offer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoUserOfferListView(APIView):
    def get(self, request):
        try:
            user_offers = UserOffer.objects.all()
            result = []
            for user_offer in user_offers:
                user_offer_data = {
                    'id': user_offer.id,
                    'user_id': user_offer.user_id,
                    'offer_id': user_offer.offer_id,
                    'purchase_date': user_offer.purchase_date.isoformat() if user_offer.purchase_date else None,
                    'expiration_date': user_offer.expiration_date.isoformat() if user_offer.expiration_date else None,
                    'is_active': user_offer.is_active,
                    'approval_status': user_offer.approval_status,
                    'created_at': user_offer.created_at.isoformat() if user_offer.created_at else None,
                    'updated_at': user_offer.updated_at.isoformat() if user_offer.updated_at else None,
                }
                result.append(user_offer_data)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoUserOfferByUserView(APIView):
    def get(self, request, user_id):
        try:
            # Get requesting user info from headers
            requesting_user_id = request.META.get('HTTP_X_USER_ID')
            requesting_user_email = request.META.get('HTTP_X_USER_EMAIL')
            
            # Check if requesting user is trying to access their own data or has admin privileges
            # For now, allow access (you can add more sophisticated permission checks)
            user_offers = UserOffer.objects.filter(user_id=user_id)
            result = []
            for user_offer in user_offers:
                user_offer_data = {
                    'id': user_offer.id,
                    'user_id': user_offer.user_id,
                    'offer_id': user_offer.offer_id,
                    'purchase_date': user_offer.purchase_date.isoformat() if user_offer.purchase_date else None,
                    'expiration_date': user_offer.expiration_date.isoformat() if user_offer.expiration_date else None,
                    'is_active': user_offer.is_active,
                    'approval_status': user_offer.approval_status,
                    'created_at': user_offer.created_at.isoformat() if user_offer.created_at else None,
                    'updated_at': user_offer.updated_at.isoformat() if user_offer.updated_at else None,
                }
                result.append(user_offer_data)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoCourseLessonListView(APIView):
    def get(self, request):
        try:
            lessons = CourseLesson.objects.all()
            result = []
            for lesson in lessons:
                lesson_data = {
                    'id': lesson.id,
                    'title': lesson.title,
                    'description': lesson.description,
                    'video_url': lesson.video_url,
                    'animation_3d_url': lesson.animation_3d_url,
                    'content_title': lesson.content_title,
                    'content_description': lesson.content_description,
                    'display_order': lesson.display_order,
                    'lesson_order': lesson.lesson_order,
                    'is_service': lesson.is_service,
                    'user_id': lesson.user_id,
                    'created_at': lesson.created_at.isoformat() if lesson.created_at else None,
                    'updated_at': lesson.updated_at.isoformat() if lesson.updated_at else None,
                }
                result.append(lesson_data)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoCourseLessonDetailView(APIView):
    def get(self, request, lesson_id):
        try:
            lesson = CourseLesson.objects.get(id=lesson_id)
            lesson_data = {
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'video_url': lesson.video_url,
                'animation_3d_url': lesson.animation_3d_url,
                'content_title': lesson.content_title,
                'content_description': lesson.content_description,
                'display_order': lesson.display_order,
                'lesson_order': lesson.lesson_order,
                'is_service': lesson.is_service,
                'user_id': lesson.user_id,
                'created_at': lesson.created_at.isoformat() if lesson.created_at else None,
                'updated_at': lesson.updated_at.isoformat() if lesson.updated_at else None,
            }
            return Response(lesson_data)
        except CourseLesson.DoesNotExist:
            return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoTestQuestionListView(APIView):
    def get(self, request):
        try:
            questions = TestQuestion.objects.all()
            result = []
            for question in questions:
                question_data = {
                    'id': question.id,
                    'question_text': question.question_text,
                    'course_test_id': question.test.id if question.test else None,
                    'question_order': question.question_order,
                    'points': question.points,
                    'question_type': question.question_type,
                    'expected_answer_type': question.expected_answer_type,
                    'user_id': question.user_id,
                    'created_at': question.created_at.isoformat() if question.created_at else None,
                    'updated_at': question.updated_at.isoformat() if question.updated_at else None,
                }
                result.append(question_data)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DjangoTestQuestionByTestView(APIView):
    def get(self, request, test_id):
        try:
            questions = TestQuestion.objects.filter(test_id=test_id)
            result = []
            for question in questions:
                question_data = {
                    'id': question.id,
                    'question_text': question.question_text,
                    'course_test_id': question.test.id if question.test else None,
                    'question_order': question.question_order,
                    'points': question.points,
                    'question_type': question.question_type,
                    'expected_answer_type': question.expected_answer_type,
                    'user_id': question.user_id,
                    'created_at': question.created_at.isoformat() if question.created_at else None,
                    'updated_at': question.updated_at.isoformat() if question.updated_at else None,
                }
                result.append(question_data)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class ApproveUserOfferView(APIView):
    def put(self, request, user_offer_id):
        try:
            user_offer = UserOffer.objects.get(id=user_offer_id)
            user_offer.approval_status = 'APPROVED'
            user_offer.is_active = True
            user_offer.save()
            user_offer_data = {
                'id': user_offer.id,
                'user_id': user_offer.user_id,
                'offer_id': user_offer.offer_id,
                'purchase_date': user_offer.purchase_date.isoformat() if user_offer.purchase_date else None,
                'expiration_date': user_offer.expiration_date.isoformat() if user_offer.expiration_date else None,
                'is_active': user_offer.is_active,
                'approval_status': user_offer.approval_status,
                'created_at': user_offer.created_at.isoformat() if user_offer.created_at else None,
                'updated_at': user_offer.updated_at.isoformat() if user_offer.updated_at else None,
            }
            return Response(user_offer_data)
        except UserOffer.DoesNotExist:
            return Response({'error': 'UserOffer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RejectUserOfferView(APIView):
    def put(self, request, user_offer_id):
        try:
            user_offer = UserOffer.objects.get(id=user_offer_id)
            user_offer.approval_status = 'REJECTED'
            user_offer.is_active = False
            user_offer.save()
            user_offer_data = {
                'id': user_offer.id,
                'user_id': user_offer.user_id,
                'offer_id': user_offer.offer_id,
                'purchase_date': user_offer.purchase_date.isoformat() if user_offer.purchase_date else None,
                'expiration_date': user_offer.expiration_date.isoformat() if user_offer.expiration_date else None,
                'is_active': user_offer.is_active,
                'approval_status': user_offer.approval_status,
                'created_at': user_offer.created_at.isoformat() if user_offer.created_at else None,
                'updated_at': user_offer.updated_at.isoformat() if user_offer.updated_at else None,
            }
            return Response(user_offer_data)
        except UserOffer.DoesNotExist:
            return Response({'error': 'UserOffer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _save_face_data(self, movement_record, face_data):
        # Backend does not analyze face data
        # All analysis is done in frontend and sent to backend
        # This method does nothing as per requirements
        pass
    
    def _save_hand_data(self, movement_record, hands_data):
        # Backend does not analyze hand data
        # All analysis is done in frontend and sent to backend
        # This method does nothing as per requirements
        pass
