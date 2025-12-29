import { Component, OnInit, AfterViewInit, OnDestroy, ViewChild, ElementRef, Input, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideoService, BodyAnalysis } from '../video.service';
import { AuthService, User } from '../auth.service';
import { DataService } from '../services/data.service';
import { AiService } from '../services/ai.service';
import { DocumentService } from '../services/document.service';
import { VideoUploadService } from '../services/video-upload.service';
import { DjDataService, DjangoUser, DjangoOffer, DjangoUserOffer, DjangoCourseLesson, DjangoTestQuestion } from '../services/dj-data.service';
import { DjAuthService, DjUser } from '../services/dj-auth.service';

// Import Three.js types
import * as THREE from 'three';
import { GLTFLoader } from 'three-stdlib';
import { OrbitControls } from 'three-stdlib';
import { VRM, VRMUtils } from '@pixiv/three-vrm';

interface PoseDataHistory {
  timestamp: number;
  data: any;
}

interface FaceDataHistory {
  timestamp: number;
  data: any;
}

interface HandsDataHistory {
  timestamp: number;
  data: any;
}

interface CapturedVideo {
  blob: Blob;
  metadata: any;
}

@Component({
  selector: 'app-video',
  standalone: true,
  templateUrl: './video.component.html',
  styleUrls: ['./video.component.scss'],
  imports: [CommonModule]
})
export class VideoComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('videoElement') videoElement!: ElementRef;
  @ViewChild('canvasElement') canvasElement!: ElementRef;
  @ViewChild('threeDContainer') threeDContainer!: ElementRef;

  // Three.js related properties
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private renderer!: THREE.WebGLRenderer;
  private controls: OrbitControls | null = null;
  private carModel!: THREE.Group;
  private isModelLoaded = false;
  showModelInfo = false;
  modelPosition = { x: 0, y: 0, z: 0 };

  // State variables
  isTracking = false;
  isVideoInitialized = false;
  stream: MediaStream | null = null;
  bodyAnalysis: BodyAnalysis | null = null;
  userId: number = 0;
  confidenceTrend: 'increasing' | 'decreasing' | 'stable' = 'stable';
  previousConfidence = 0;
  lastAnalysisTime = 0;
  analysisInterval = 100;
  isCsvDropdownOpen = false;
  fps = 0;
  errorMessage = '';

  // For capturing videos and movement data
  private mediaRecorder: MediaRecorder | null = null;
  private recordedChunks: Blob[] = [];

  // For movement data history
  public poseDataHistory: PoseDataHistory[] = [];
  public faceDataHistory: FaceDataHistory[] = [];
  public handsDataHistory: HandsDataHistory[] = [];
  
  // For periodic data sending
  private dataSendInterval: any;
  private lastMovementDetection: { timestamp: number, type: string } | null = null;
  private capturedImagesForSend: string[] = [];
  private lastCaptureTime: number = 0;
  
  // For temporary video creation
  public temporaryVideoBlob: Blob | null = null;
  private temporaryVideoUrl: string | null = null;
  private analysisStartTime: number | null = null;
  private analysisEndTime: number | null = null;
  
  // For video file upload
  public selectedVideoFile: File | null = null;
  public isProcessingVideo = false;
  public storedVideoUrl: string | null = null;
  
  @Input() videoUrl: string | null = null;
  @Input() lessonId: number | null | undefined = null;
  
  // For image capture functionality
  capturedImages: string[] = [];
  
  // Django autonomous data
  djangoUsers: DjangoUser[] = [];
  djangoOffers: DjangoOffer[] = [];
  djangoUserOffers: DjangoUserOffer[] = [];
  djangoCourseLessons: DjangoCourseLesson[] = [];
  djangoTestQuestions: DjangoTestQuestion[] = [];
  
  // Loading states
  usersLoading = false;
  offersLoading = false;
  userOffersLoading = false;
  lessonsLoading = false;
  questionsLoading = false;
  
  // Django authentication
  djUser: DjUser | null = null;
  private imageCaptureInterval: any;
  
  // For image file upload
  public selectedImageFile: File | null = null;
  public isProcessingImage = false;
  
  // VRM properties
  private vrm: VRM | null = null;
  private vrmModel: THREE.Object3D | null = null;

  constructor(
    private videoService: VideoService,
    private authService: AuthService,
    private dataService: DataService,
    private aiService: AiService,
    private documentService: DocumentService,
    private videoUploadService: VideoUploadService,
    private djDataService: DjDataService,
    private djAuthService: DjAuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadCurrentUser();
    
    // Initialize 3D scene after view is ready, only in browser environment
    if (typeof window !== 'undefined') {
      setTimeout(() => {
        this.initThreeScene();
      }, 100);
    }
    
    // Load Django autonomous data
    this.loadDjangoData();
    
    // Initialize Django authentication
    this.initDjangoAuth();
  }
  
  ngAfterViewInit(): void {
    // Set up body analysis subscription after view is initialized
    // This ensures we're definitely in the browser environment
    this.setupBodyAnalysisSubscription();
  }

ngOnDestroy(): void {
  // Check if we're in browser environment
  if (typeof window !== 'undefined') {
    this.stopCamera();
    this.stopDataSending();
    
    // Clean up Three.js resources
    if (this.renderer) {
      this.renderer.dispose();
    }
    
    // Dispose of controls if they exist
    if (this.controls) {
      this.controls.dispose();
    }
    
    // Optionnel: appeler dispose() s'il existe
    if (this.videoService && typeof (this.videoService as any).dispose === 'function') {
      (this.videoService as any).dispose();
    }
  }
}

  private loadCurrentUser(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('User loading skipped - not in browser environment');
      return;
    }
    
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.userId = currentUser.id;
      console.log('✅ User ID loaded in video component:', this.userId);
      // Start data sending if camera is already active
      if (this.isTracking) {
        this.startDataSending();
      }
    } else {
      // If user is not available, try to get it from the observable
      this.authService.currentUser.subscribe(user => {
        if (user) {
          this.userId = user.id;
          console.log('✅ User ID loaded from observable:', this.userId);
          // Start data sending if camera is already active
          if (this.isTracking) {
            this.startDataSending();
          }
        }
      });
    }
  }

  private setupBodyAnalysisSubscription(): void {
    this.videoService.bodyAnalysis$.subscribe(analysis => {
      // Use setTimeout to defer the update and avoid ExpressionChangedAfterItHasBeenCheckedError
      setTimeout(() => {
        this.bodyAnalysis = analysis;
        if (analysis.isAnalyzing) {
          this.collectMovementData(Date.now());
          // Also detect movements and capture images when movement is detected
          this.detectMovementAndCapture();
        }
        
        // Trigger change detection to update the view
        if (typeof window !== 'undefined') {
          this.cdr.detectChanges();
        }
      });
    });
  }

  async startCamera(): Promise<void> {
    // Check if we're in browser environment
    if (typeof window === 'undefined' || typeof navigator === 'undefined' || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn('Camera access skipped - not in browser environment or media devices not available');
      this.errorMessage = 'Camera not available in server environment';
      return Promise.resolve();
    }
    
    if (this.isTracking) {
      return Promise.resolve();
    }

    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 },
        audio: false
      });

      if (this.videoElement) {
        this.videoElement.nativeElement.srcObject = this.stream;
        this.videoElement.nativeElement.play();

        await this.videoService.initializeMediaPipe();
        await this.videoService.setupHolistic(this.videoElement.nativeElement);

        this.isTracking = true;
        this.isVideoInitialized = true;
        this.analysisStartTime = Date.now();
        this.lastAnalysisTime = 0;

        // Start recording the video stream
        this.startRecording();
        
        // Start image capture
        this.startImageCapture();
        
        // Load current user and start periodic data sending
        this.loadCurrentUser();
        
        // Start periodic data sending
        this.startDataSending();
      }
    } catch (error) {
      this.errorMessage = 'Failed to start camera: ' + (error as Error).message;
      this.isTracking = false;
    }
  }
  
  // Override stopCamera to also stop data sending
  stopCamera(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Camera stop skipped - not in browser environment');
      return;
    }
    
    this.isTracking = false;

    this.analysisEndTime = Date.now();

    // Stop recording
    this.stopRecording();

    // Stop image capture interval
    this.stopImageCapture();

    // Stop data sending
    this.stopDataSending();

    // Stop video analysis loop
    this.stopVideoAnalysisLoop();

    // Create video from CSV data
    this.createVideoFromPoseCSV();

    // Upload all CSV data to backend
    this.uploadAllCSV();

    this.sendCapturedDataToBackends();

    // Store the analyzed video
    this.storeAnalyzedVideo();

    // Stop all tracks
    if (this.stream) {
      this.stream.getTracks().forEach(track => {
        track.stop();
      });
      this.stream = null;
    }

    // Also stop the MediaPipe camera
    if (this.videoService) {
      this.videoService.dispose();
    }
  }
  
  private startDataSending(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Data sending skipped - not in browser environment');
      return;
    }
    
    // Clear any existing interval
    this.stopDataSending();
    
    // Start sending detailed data every 5 seconds as requested
    this.dataSendInterval = setInterval(() => {
      // Check authentication status
      const currentUser = this.authService.getCurrentUser();
      
      // Only send data if user ID is available
      if (this.userId) {

        // Send movement data which includes captured images
        this.sendMovementData();
      } else {
        console.warn('❌ User ID not available, skipping data send');
        // Try to reload user if not available
        this.loadCurrentUser();
      }
    }, 5000); // Every 5 seconds
  }
  
  private stopDataSending(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Data sending stop skipped - not in browser environment');
      return;
    }
    
    if (this.dataSendInterval) {
      clearInterval(this.dataSendInterval);
      this.dataSendInterval = null;
    }
  }
  
  private sendMovementDataToBackend(): void {
    if (!this.userId) {
      console.error('No user ID available for data sending');
      return;
    }
    
    // Check if there has been any movement detection in the last period
    if (this.lastMovementDetection) {
      // Format the data as "date-userid-movement_type"
      const dateStr = new Date().toLocaleDateString('fr-FR'); // Format: 26/12/2026
      const dataLabel = `${dateStr}-${this.userId}-${this.lastMovementDetection.type}`;
      
      // Only send if we have images to send
      if (this.capturedImagesForSend.length > 0) {
        // Prepare the data to send
        const movementData = {
          user: this.userId,
          label: dataLabel,
          movementType: this.lastMovementDetection.type,
          timestamp: this.lastMovementDetection.timestamp,
          images: this.capturedImagesForSend // Send captured images
        };
        
        // Send to Django backend
        this.documentService.uploadMovementData(movementData).subscribe({
          next: (response) => {
            console.log('Movement data sent successfully:', response);
            // Clear the captured images after successful sending
            this.capturedImagesForSend = [];
            this.lastMovementDetection = null;
          },
          error: (error) => {
            console.error('Error sending movement data:', error);
            // Don't clear images on error so they can be retried
            this.lastMovementDetection = null; // But clear detection so it doesn't keep trying
          }
        });
      } else {
        // If there was movement detection but no images, still clear the detection
        this.lastMovementDetection = null;
      }
    }
  }
  private sendMovementData(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Movement data sending skipped - not in browser environment');
      return;
    }
      
    // Debug logging to understand what's happening
    console.log('🔍 sendMovementData called - images:', this.capturedImagesForSend.length, 'userId:', this.userId);
        
    // Vérifier que nous avons des images et des données
    if (this.capturedImagesForSend.length === 0 || !this.userId) {
      console.log('⚠️ Skipping data send - images:', this.capturedImagesForSend.length, 'userId:', this.userId);
      return;
    }
        
    console.log('📤 Attempting to send', this.capturedImagesForSend.length, 'images to Django backend');
        
    
      
    // Format the data as "date-userid-movement_type"
    const dateStr = new Date().toLocaleDateString('fr-FR'); // Format: 26/12/2026
    const dataLabel = `${dateStr}-${this.userId}-active_capture`;
      
    // Prepare the data to send
    const movementDataToSend = {
      user: this.userId,
      label: dataLabel,
      movementType: 'active_capture',
      timestamp: Date.now(),
      images: this.capturedImagesForSend // Send captured images
    };
        
    console.log('📡 Sending movement data:', movementDataToSend);
        
    // Send to Django backend via document service (the only service that handles this)
    console.log('🔌 Calling documentService.uploadMovementData');
    this.documentService.uploadMovementData(movementDataToSend).subscribe({
      next: (response) => {
        console.log('✅ Images envoyées avec succès:', response);
        // Clear the captured images after successful sending
        this.capturedImagesForSend = [];
    
      },
      error: (error) => {
        console.error('❌ Erreur lors de l\'envoi des images:', error);
        // Check if it's a 401 error - this might mean the token is not valid for Django
        if (error.status === 401) {
          console.warn('⚠️ 401 Unauthorized - token may not be valid for Django backend');
          // Don't clear images on 401 error so they can be retried
        } else {
          // Don't clear images on other errors so they can be retried
        }
      }
    });
  }

  
  private detectMovementAndCapture(): void {
    // Check if there's significant movement detected
    // This could be based on pose confidence changes, hand movements, etc.
    
    // Example: Check if hands are in a victory pose
    if (this.bodyAnalysis?.hands?.left?.gesture === 'VICTORY' || 
        this.bodyAnalysis?.hands?.right?.gesture === 'VICTORY') {
      
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'VICTORY' };
      
      // Don't duplicate image capture - use the already captured images
      // The image is already captured by the regular capture interval
    }
    
    // Add other movement detection logic as needed
    // Example: Check for other gestures or pose changes
    if (this.bodyAnalysis?.hands?.left?.gesture === 'THUMBS_UP' || 
        this.bodyAnalysis?.hands?.right?.gesture === 'THUMBS_UP') {
      
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'THUMBS_UP' };
      
      // Don't duplicate image capture - use the already captured images
      // The image is already captured by the regular capture interval
    }
    
    // Additional movement detection: head movement, pose changes, etc.
    if (this.bodyAnalysis?.pose) {
      // Example: detect significant pose changes or head movements
      const pose = this.bodyAnalysis.pose;
      
      // NEW: Detect body movements
      this.detectBodyMovements(pose);
    }
    
    // NEW: Detect facial expressions as movements
    if (this.bodyAnalysis?.face) {
      const expression = this.getFaceExpression();
      
      // Check for specific expressions that should trigger capture
      if (expression === 'Dégoût' || expression === 'Colère' || 
          expression === 'Joie' || expression === 'Surprise' || 
          expression === 'Peur' || expression === 'Tristesse') {
        
        const timestamp = Date.now();
        this.lastMovementDetection = { timestamp, type: `EXPRESSION_${expression.toUpperCase()}` };
        
        // The image is already captured by the regular capture interval
        // But we'll also store facial expression data
        this.storeFacialExpressionData(expression, timestamp);
      }
    }
  }
  
  // Detect body movements like turning, punching, gesturing, etc.
  private detectBodyMovements(pose: any): void {
    // Check for turning movement (head and shoulder rotation)
    if (this.isTurningDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'TOURNER' };
    }
    
    // Check for punching movement (arm extension with specific hand gesture)
    if (this.isPunchingDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'DONNER_PUNCH' };
    }
    
    // Check for gesturing movement (arm movements with open hands)
    if (this.isGesturingDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'GESTICULER' };
    }
    
    // Check for asserting movement (strong posture, hands on hips, etc.)
    if (this.isAssertingDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'S_AFFIRMER' };
    }
    
    // Check for daily movements
    if (this.isWalkingDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'MARCHER' };
    }
    
    if (this.isSittingDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'S_ASSOIR' };
    }
    
    if (this.isStandingDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'SE_DEBOUTER' };
    }
    
    if (this.isReachingDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'ATTEINDRE' };
    }
    
    if (this.isWavingDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'SALUER' };
    }
    
    if (this.isPointingDetected(pose)) {
      const timestamp = Date.now();
      this.lastMovementDetection = { timestamp, type: 'POINTER' };
    }
  }
  
  // Check if turning is detected
  private isTurningDetected(pose: any): boolean {
    try {
      // Turning is detected by head rotation and shoulder position
      const head = pose['Head'];
      const leftShoulder = pose['LeftShoulder'];
      const rightShoulder = pose['RightShoulder'];
      
      if (head && leftShoulder && rightShoulder) {
        // Calculate the angle between shoulders to detect rotation
        const shoulderAngle = Math.abs(leftShoulder.position.y - rightShoulder.position.y);
        
        // If the head is turned significantly from the shoulder line
        const headShoulderOffset = Math.abs(head.position.x - ((leftShoulder.position.x + rightShoulder.position.x) / 2));
        
        return headShoulderOffset > 0.2 || shoulderAngle > 0.1;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting turning:', error);
      return false;
    }
  }
  
  // Check if punching is detected
  private isPunchingDetected(pose: any): boolean {
    try {
      // Punching is detected by arm extension and hand position
      const leftShoulder = pose['LeftShoulder'];
      const leftElbow = pose['LeftElbow'];
      const leftWrist = pose['LeftWrist'];
      const rightShoulder = pose['RightShoulder'];
      const rightElbow = pose['RightElbow'];
      const rightWrist = pose['RightWrist'];
      
      // Check for left arm punch
      if (leftShoulder && leftElbow && leftWrist) {
        // Calculate arm extension - punch typically has extended arm
        const leftArmExtension = this.calculateDistance(leftShoulder.position, leftElbow.position) + 
                              this.calculateDistance(leftElbow.position, leftWrist.position);
        
        // Check if arm is extended forward (punching motion)
        const leftPunching = Math.abs(leftWrist.position.x - leftShoulder.position.x) > 0.3 &&
                         leftWrist.position.x < leftShoulder.position.x; // Moving forward
        
        if (leftPunching) return true;
      }
      
      // Check for right arm punch
      if (rightShoulder && rightElbow && rightWrist) {
        // Calculate arm extension - punch typically has extended arm
        const rightArmExtension = this.calculateDistance(rightShoulder.position, rightElbow.position) + 
                               this.calculateDistance(rightElbow.position, rightWrist.position);
        
        // Check if arm is extended forward (punching motion)
        const rightPunching = Math.abs(rightWrist.position.x - rightShoulder.position.x) > 0.3 &&
                          rightWrist.position.x < rightShoulder.position.x; // Moving forward
        
        if (rightPunching) return true;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting punching:', error);
      return false;
    }
  }
  
  // Check if gesturing is detected
  private isGesturingDetected(pose: any): boolean {
    try {
      // Gesturing is detected by arm movements with open hands
      const leftShoulder = pose['LeftShoulder'];
      const leftElbow = pose['LeftElbow'];
      const leftWrist = pose['LeftWrist'];
      const rightShoulder = pose['RightShoulder'];
      const rightElbow = pose['RightElbow'];
      const rightWrist = pose['RightWrist'];
      
      // Check if hands are moving significantly
      const leftGesture = leftShoulder && leftElbow && leftWrist &&
                         this.calculateDistance(leftShoulder.position, leftWrist.position) > 0.4;
      
      const rightGesture = rightShoulder && rightElbow && rightWrist &&
                          this.calculateDistance(rightShoulder.position, rightWrist.position) > 0.4;
      
      // Also check if hands are open (not fists)
      const handsOpen = (this.bodyAnalysis?.hands?.left?.gesture !== 'FIST' || 
                      this.bodyAnalysis?.hands?.right?.gesture !== 'FIST');
      
      return (leftGesture || rightGesture) && handsOpen;
    } catch (error) {
      console.warn('Error detecting gesturing:', error);
      return false;
    }
  }
  
  // Check if asserting posture is detected
  private isAssertingDetected(pose: any): boolean {
    try {
      // Asserting posture often includes strong stance, hands on hips, etc.
      const leftShoulder = pose['LeftShoulder'];
      const leftHip = pose['LeftHip'];
      const rightShoulder = pose['RightShoulder'];
      const rightHip = pose['RightHip'];
      const leftWrist = pose['LeftWrist'];
      const rightWrist = pose['RightWrist'];
      
      // Check for hands on hips posture (common asserting stance)
      if (leftWrist && leftHip) {
        const leftHandOnHip = this.calculateDistance(leftWrist.position, leftHip.position) < 0.2;
        
        if (leftHandOnHip) return true;
      }
      
      if (rightWrist && rightHip) {
        const rightHandOnHip = this.calculateDistance(rightWrist.position, rightHip.position) < 0.2;
        
        if (rightHandOnHip) return true;
      }
      
      // Check for strong, confident posture (shoulders back, chest out)
      const shoulderHipAlignment = leftShoulder && leftHip && rightShoulder && rightHip &&
                                  Math.abs(leftShoulder.position.x - leftHip.position.x) < 0.1 &&
                                  Math.abs(rightShoulder.position.x - rightHip.position.x) < 0.1;
      
      return shoulderHipAlignment;
    } catch (error) {
      console.warn('Error detecting asserting:', error);
      return false;
    }
  }
  
  // Check if walking is detected
  private isWalkingDetected(pose: any): boolean {
    try {
      // Walking is detected by alternating leg movements and hip motion
      const leftHip = pose['LeftHip'];
      const rightHip = pose['RightHip'];
      const leftKnee = pose['LeftKnee'];
      const rightKnee = pose['RightKnee'];
      const leftAnkle = pose['LeftAnkle'];
      const rightAnkle = pose['RightAnkle'];
      
      // For walking detection, we'd need to track movement over time
      // This is a simplified check based on relative positions
      if (leftHip && rightHip && leftAnkle && rightAnkle) {
        // Check if there's significant difference in leg positions (indicating movement)
        const legDifference = Math.abs(leftAnkle.position.y - rightAnkle.position.y);
        return legDifference > 0.1;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting walking:', error);
      return false;
    }
  }
  
  // Check if sitting is detected
  private isSittingDetected(pose: any): boolean {
    try {
      // Sitting is detected by hip-knee-ankle angle and overall posture
      const leftHip = pose['LeftHip'];
      const leftKnee = pose['LeftKnee'];
      const leftAnkle = pose['LeftAnkle'];
      const rightHip = pose['RightHip'];
      const rightKnee = pose['RightKnee'];
      const rightAnkle = pose['RightAnkle'];
      
      if (leftHip && leftKnee && leftAnkle && rightHip && rightKnee && rightAnkle) {
        // Calculate angles between hip-knee-ankle to detect sitting position
        const leftAngle = this.calculateAngle(leftHip.position, leftKnee.position, leftAnkle.position);
        const rightAngle = this.calculateAngle(rightHip.position, rightKnee.position, rightAnkle.position);
        
        // Sitting typically has more bent knees (smaller angles)
        return leftAngle < 120 || rightAngle < 120; // Angle in degrees
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting sitting:', error);
      return false;
    }
  }
  
  // Check if standing is detected
  private isStandingDetected(pose: any): boolean {
    try {
      // Standing is detected by more straight leg alignment
      const leftHip = pose['LeftHip'];
      const leftKnee = pose['LeftKnee'];
      const leftAnkle = pose['LeftAnkle'];
      const rightHip = pose['RightHip'];
      const rightKnee = pose['RightKnee'];
      const rightAnkle = pose['RightAnkle'];
      
      if (leftHip && leftKnee && leftAnkle && rightHip && rightKnee && rightAnkle) {
        // Calculate angles between hip-knee-ankle to detect standing position
        const leftAngle = this.calculateAngle(leftHip.position, leftKnee.position, leftAnkle.position);
        const rightAngle = this.calculateAngle(rightHip.position, rightKnee.position, rightAnkle.position);
        
        // Standing typically has more straight legs (larger angles)
        return leftAngle > 160 && rightAngle > 160; // Angle in degrees
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting standing:', error);
      return false;
    }
  }
  
  // Check if reaching is detected
  private isReachingDetected(pose: any): boolean {
    try {
      // Reaching is detected by extended arms away from body
      const leftShoulder = pose['LeftShoulder'];
      const leftWrist = pose['LeftWrist'];
      const rightShoulder = pose['RightShoulder'];
      const rightWrist = pose['RightWrist'];
      
      if (leftShoulder && leftWrist) {
        // Check if arm is extended significantly from body
        const leftArmExtension = this.calculateDistance(leftShoulder.position, leftWrist.position);
        
        // If the distance is large, it might be reaching
        if (leftArmExtension > 0.6) return true;
      }
      
      if (rightShoulder && rightWrist) {
        // Check if arm is extended significantly from body
        const rightArmExtension = this.calculateDistance(rightShoulder.position, rightWrist.position);
        
        // If the distance is large, it might be reaching
        if (rightArmExtension > 0.6) return true;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting reaching:', error);
      return false;
    }
  }
  
  // Check if waving is detected
  private isWavingDetected(pose: any): boolean {
    try {
      // Waving is detected by repetitive hand movements
      const leftShoulder = pose['LeftShoulder'];
      const leftElbow = pose['LeftElbow'];
      const leftWrist = pose['LeftWrist'];
      const rightShoulder = pose['RightShoulder'];
      const rightElbow = pose['RightElbow'];
      const rightWrist = pose['RightWrist'];
      
      // Check for waving motion (repetitive movement)
      if (leftWrist) {
        // Check if hand is moving in a waving pattern
        const leftWaving = Math.abs(leftWrist.position.y - leftElbow.position.y) > 0.2 &&
                        Math.abs(leftWrist.position.x - leftElbow.position.x) > 0.1;
        
        if (leftWaving) return true;
      }
      
      if (rightWrist) {
        // Check if hand is moving in a waving pattern
        const rightWaving = Math.abs(rightWrist.position.y - rightElbow.position.y) > 0.2 &&
                         Math.abs(rightWrist.position.x - rightElbow.position.x) > 0.1;
        
        if (rightWaving) return true;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting waving:', error);
      return false;
    }
  }
  
  // Check if pointing is detected
  private isPointingDetected(pose: any): boolean {
    try {
      // Pointing is detected by extended index finger and specific hand orientation
      const leftWrist = pose['LeftWrist'];
      const rightWrist = pose['RightWrist'];
      
      // Check if hand is in pointing gesture (using hand analysis)
      const leftPointing = this.bodyAnalysis?.hands?.left?.gesture === 'POINT' ||
                        this.bodyAnalysis?.hands?.left?.gesture === 'FINGER_UP';
      
      const rightPointing = this.bodyAnalysis?.hands?.right?.gesture === 'POINT' ||
                         this.bodyAnalysis?.hands?.right?.gesture === 'FINGER_UP';
      
      return leftPointing || rightPointing;
    } catch (error) {
      console.warn('Error detecting pointing:', error);
      return false;
    }
  }
  
  // Helper to calculate distance between two points
  private calculateDistance(point1: any, point2: any): number {
    if (!point1 || !point2) return 0;
    
    const dx = point1.x - point2.x;
    const dy = point1.y - point2.y;
    const dz = point1.z ? (point1.z - point2.z) : 0;
    
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
  
  // Helper to calculate angle between three points
  private calculateAngle(point1: any, point2: any, point3: any): number {
    if (!point1 || !point2 || !point3) return 0;
    
    // Vector from point2 to point1
    const v1 = { x: point1.x - point2.x, y: point1.y - point2.y };
    // Vector from point2 to point3
    const v2 = { x: point3.x - point2.x, y: point3.y - point2.y };
    
    // Calculate angle in radians and convert to degrees
    const dot = v1.x * v2.x + v1.y * v2.y;
    const det = v1.x * v2.y - v1.y * v2.x;
    const angle = Math.atan2(det, dot) * (180 / Math.PI);
    
    return Math.abs(angle);
  }
  
  // Get the detected movement
  getDetectedMovement(): string {
    // Try to get movement from face data history
    if (this.faceDataHistory.length > 0) {
      const latestFaceData = this.faceDataHistory[this.faceDataHistory.length - 1];
      if (latestFaceData.data?.detectedMovement) {
        return latestFaceData.data.detectedMovement;
      }
    }
    
    // Also try to get movement from pose data history
    if (this.poseDataHistory.length > 0) {
      const latestPoseData = this.poseDataHistory[this.poseDataHistory.length - 1];
      if (latestPoseData.data?.detectedMovement) {
        return latestPoseData.data.detectedMovement;
      }
    }
    
    // Also try to get movement from hands data history
    if (this.handsDataHistory.length > 0) {
      const latestHandsData = this.handsDataHistory[this.handsDataHistory.length - 1];
      if (latestHandsData.data?.detectedMovement) {
        return latestHandsData.data.detectedMovement;
      }
    }
    
    // Fallback to last movement detection
    return this.lastMovementDetection?.type || 'AUCUN';
  }
  
  // Store facial expression data
  private storeFacialExpressionData(expression: string, timestamp: number): void {
    // Store the detected expression in face data history
    if (this.bodyAnalysis?.face) {
      this.faceDataHistory.push({
        timestamp,
        data: {
          ...this.bodyAnalysis.face,
          detectedExpression: expression,
          confidence: this.bodyAnalysis.faceConfidence || 0
        }
      });
      
      // Keep only the last 100 entries to prevent memory issues
      if (this.faceDataHistory.length > 100) {
        this.faceDataHistory.shift();
      }
    }
  }
  
  private startRecording(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined' || typeof MediaRecorder === 'undefined') {
      console.warn('Recording skipped - not in browser environment or MediaRecorder not available');
      return;
    }
    
    if (!this.stream) {
      return;
    }

    try {
      // Reset recorded chunks
      this.recordedChunks = [];

      // Create MediaRecorder with a specific MIME type
      const options = { mimeType: 'video/webm; codecs=vp9' };
      this.mediaRecorder = new MediaRecorder(this.stream, options);

      this.mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          this.recordedChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        this.createTemporaryVideo();
      };

      this.mediaRecorder.onerror = (event: Event) => {
        this.errorMessage = 'Error recording video';
      };

      // Start recording with 1 second chunks
      this.mediaRecorder.start(1000);
    } catch (error) {
      this.errorMessage = 'Failed to start recording: ' + (error as Error).message;
    }
  }

  private stopRecording(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Recording stop skipped - not in browser environment');
      return;
    }
    
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }
  }

  private createTemporaryVideo(): void {
    if (this.recordedChunks.length === 0) {
      return;
    }

    try {
      // Create blob from recorded chunks
      const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
      // Revoke previous temporary video URL if it exists to prevent memory leaks
      if (this.temporaryVideoUrl) {
        URL.revokeObjectURL(this.temporaryVideoUrl);
        this.temporaryVideoUrl = null;
      }
      this.temporaryVideoBlob = blob;
      
      // Clean up
      this.recordedChunks = [];
    } catch (error) {
      this.errorMessage = 'Failed to create temporary video: ' + (error as Error).message;
    }
  }

  getBodyConfidence(): number {
    if (!this.bodyAnalysis) return 0;
    const poseConfidence = this.bodyAnalysis.poseConfidence || 0;
    const faceConfidence = this.bodyAnalysis.faceConfidence || 0;
    const handsDetected = this.bodyAnalysis.handsDetected || { left: false, right: false };
    const handsCount = (handsDetected.left ? 1 : 0) + (handsDetected.right ? 1 : 0);

    const confidence = (poseConfidence * 0.5) + (faceConfidence * 0.3) + (handsCount * 50 * 0.2);
    return Math.min(100, Math.round(confidence));
  }

  // ========== MÉTHODES DE TÉLÉCHARGEMENT CSV ==========

  downloadPoseCSV(): void {
    if (this.poseDataHistory.length === 0) {
      return;
    }

    let csvContent = 'Timestamp,Pose Confidence,Head X,Head Y,Head Z,Head Confidence,Left Shoulder X,Left Shoulder Y,Left Shoulder Z,Left Shoulder Confidence,Right Shoulder X,Right Shoulder Y,Right Shoulder Z,Right Shoulder Confidence,Left Hip X,Left Hip Y,Left Hip Z,Left Hip Confidence,Right Hip X,Right Hip Y,Right Hip Z,Right Hip Confidence,Detecte Movement\n';

    this.poseDataHistory.forEach(entry => {
      const data = entry.data;
      const row = [
        entry.timestamp,
        data.confidence || 0,
        data.head?.x || 0,
        data.head?.y || 0,
        data.head?.z || 0,
        data.head?.confidence || 0,
        data.leftShoulder?.x || 0,
        data.leftShoulder?.y || 0,
        data.leftShoulder?.z || 0,
        data.leftShoulder?.confidence || 0,
        data.rightShoulder?.x || 0,
        data.rightShoulder?.y || 0,
        data.rightShoulder?.z || 0,
        data.rightShoulder?.confidence || 0,
        data.leftHip?.x || 0,
        data.leftHip?.y || 0,
        data.leftHip?.z || 0,
        data.leftHip?.confidence || 0,
        data.rightHip?.x || 0,
        data.rightHip?.y || 0,
        data.rightHip?.z || 0,
        data.rightHip?.confidence || 0,
        data.detectedMovement || 'AUCUN'
      ].join(',');
      csvContent += row + '\n';
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pose-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }

  downloadFaceCSV(): void {
    if (this.faceDataHistory.length === 0) {
      return;
    }

    let csvContent = 'Timestamp,Face Confidence,Mouth Open,Eye Blink Left,Eye Blink Right,Eye Look Left,Eye Look Right,Head X,Head Y,Head Z,Detected Expression,Detected Movement\n';

    this.faceDataHistory.forEach(entry => {
      const data = entry.data;
      const row = [
        entry.timestamp,
        data.confidence || 0,
        data.mouth_open || 0,
        data.eye_blink_left || 0,
        data.eye_blink_right || 0,
        data.eye_look_left || 0,
        data.eye_look_right || 0,
        data.headPosition?.x || 0,
        data.headPosition?.y || 0,
        data.headPosition?.z || 0,
        data.detectedExpression || 'Neutre',
        data.detectedMovement || 'AUCUN'
      ].join(',');
      csvContent += row + '\n';
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `face-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }

  downloadHandsCSV(): void {
    if (this.handsDataHistory.length === 0) {
      return;
    }

    let csvContent = 'Timestamp,Hand,Gesture,Confidence,Landmark Count,Detecte Movement\n';

    this.handsDataHistory.forEach(entry => {
      const data = entry.data;
      
      // Left hand data
      if (data.left) {
        const row = [
          entry.timestamp,
          'Left',
          data.left.gesture || '',
          data.left.confidence || 0,
          data.left.landmarks ? data.left.landmarks.length : 0,
          data.left.detectedMovement || 'AUCUN'
        ].join(',');
        csvContent += row + '\n';
      }
      
      // Right hand data
      if (data.right) {
        const row = [
          entry.timestamp,
          'Right',
          data.right.gesture || '',
          data.right.confidence || 0,
          data.right.landmarks ? data.right.landmarks.length : 0,
          data.right.detectedMovement || 'AUCUN'
        ].join(',');
        csvContent += row + '\n';
      }
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hands-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }

  // ========== CRÉER VIDEO DEPUIS CSV ==========

  private createVideoFromPoseCSV(): void {

    if (this.poseDataHistory.length === 0 && this.faceDataHistory.length === 0 && this.handsDataHistory.length === 0) {
      return;
    }

    // Generate comprehensive CSV content combining all data types
    let csvContent = 'Timestamp,Pose Confidence,Head X,Head Y,Head Z,Head Confidence,Left Shoulder X,Left Shoulder Y,Left Shoulder Z,Left Shoulder Confidence,Right Shoulder X,Right Shoulder Y,Right Shoulder Z,Right Shoulder Confidence,Left Hip X,Left Hip Y,Left Hip Z,Left Hip Confidence,Right Hip X,Right Hip Y,Right Hip Z,Right Hip Confidence,Face Confidence,Mouth Open,Eye Blink Left,Eye Blink Right,Eye Look Left,Eye Look Right,Head Position X,Head Position Y,Head Position Z,Detected Expression,Left Hand Gesture,Left Hand Confidence,Left Hand Landmarks,Right Hand Gesture,Right Hand Confidence,Right Hand Landmarks\n';

    // We'll combine all data by timestamp
    const allTimestamps = new Set([
      ...this.poseDataHistory.map(entry => entry.timestamp),
      ...this.faceDataHistory.map(entry => entry.timestamp),
      ...this.handsDataHistory.map(entry => entry.timestamp)
    ]);

    Array.from(allTimestamps).sort().forEach(timestamp => {
      // Find data for this timestamp
      const poseEntry = this.poseDataHistory.find(entry => entry.timestamp === timestamp);
      const faceEntry = this.faceDataHistory.find(entry => entry.timestamp === timestamp);
      const handsEntry = this.handsDataHistory.find(entry => entry.timestamp === timestamp);
      
      const poseData = poseEntry?.data || {};
      const faceData = faceEntry?.data || {};
      const handsData = handsEntry?.data || {};
      
      const row = [
        timestamp,
        // Pose data
        poseData.confidence || 0,
        poseData.head?.x || 0,
        poseData.head?.y || 0,
        poseData.head?.z || 0,
        poseData.head?.confidence || 0,
        poseData.leftShoulder?.x || 0,
        poseData.leftShoulder?.y || 0,
        poseData.leftShoulder?.z || 0,
        poseData.leftShoulder?.confidence || 0,
        poseData.rightShoulder?.x || 0,
        poseData.rightShoulder?.y || 0,
        poseData.rightShoulder?.z || 0,
        poseData.rightShoulder?.confidence || 0,
        poseData.leftHip?.x || 0,
        poseData.leftHip?.y || 0,
        poseData.leftHip?.z || 0,
        poseData.leftHip?.confidence || 0,
        poseData.rightHip?.x || 0,
        poseData.rightHip?.y || 0,
        poseData.rightHip?.z || 0,
        poseData.rightHip?.confidence || 0,
        // Face data
        faceData.confidence || 0,
        faceData.mouthOpen || 0,
        faceData.eyeBlinkLeft || 0,
        faceData.eyeBlinkRight || 0,
        faceData.eyeLookLeft || 0,
        faceData.eyeLookRight || 0,
        faceData.headPosition?.x || 0,
        faceData.headPosition?.y || 0,
        faceData.headPosition?.z || 0,
        faceData.detectedExpression || 'Neutre', // Detected expression
        // Hands data
        handsData.left?.gesture || '',
0, // handsData.left?.confidence || 0  // Not available in HandData interface
        handsData.left?.landmarks ? handsData.left.landmarks.length : 0,
        handsData.right?.gesture || '',
0, // handsData.right?.confidence || 0  // Not available in HandData interface
        handsData.right?.landmarks ? handsData.right.landmarks.length : 0
      ].join(',');
      csvContent += row + '\n';
    });

    // Send CSV to backend to generate MP4
    const videoName = `analysis-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.mp4`;
    
    // Send to Django backend via video upload service
    this.videoUploadService.createVideoFromCSV(
      csvContent,
      this.userId,
      videoName
    ).subscribe({
      next: (response) => {
        // Update the stored video URL with the one from the backend
        if (response.videoUrl) {
          this.storedVideoUrl = response.videoUrl;
              
          // Also revoke any previous temporary video URL to prevent memory leaks
          if (this.temporaryVideoUrl) {
            URL.revokeObjectURL(this.temporaryVideoUrl);
            this.temporaryVideoUrl = null;
          }
        }
        alert('✅ Vidéo créée et stockée avec succès!');
      },
      error: (err) => {
        // Create video locally if backend fails
        this.createVideoLocally(csvContent, videoName);
      }
    });
  }

  // Create video locally when backend is not available
  private createVideoLocally(csvContent: string, videoName: string): void {
    console.log('Le backend n\'est pas disponible. La vidéo sera créée localement.');
    
    // In a real implementation, we would convert the CSV data to a video locally
    // For now, we'll just create a placeholder video
    const placeholderVideo = new Blob([], { type: 'video/mp4' });
    const videoUrl = URL.createObjectURL(placeholderVideo);
    this.storedVideoUrl = videoUrl;
    this.temporaryVideoUrl = videoUrl;
    
    // Don't automatically download CSV file - store for later use if needed
    // Create and store the CSV content for potential manual download
    const csvBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const csvUrl = URL.createObjectURL(csvBlob);
    this.temporaryVideoUrl = csvUrl; // Store for potential manual download
    

  }

  uploadPoseCSV(): void {
    if (this.poseDataHistory.length === 0) {
      return;
    }

    let csvContent = 'Timestamp,Pose Confidence,Head X,Head Y,Head Z,Head Confidence,Left Shoulder X,Left Shoulder Y,Left Shoulder Z,Left Shoulder Confidence,Right Shoulder X,Right Shoulder Y,Right Shoulder Z,Right Shoulder Confidence,Left Hip X,Left Hip Y,Left Hip Z,Left Hip Confidence,Right Hip X,Right Hip Y,Right Hip Z,Right Hip Confidence,Detecte Movement\n';

    this.poseDataHistory.forEach(entry => {
      const data = entry.data;
      const row = [
        entry.timestamp,
        data.confidence || 0,
        data.head?.x || 0,
        data.head?.y || 0,
        data.head?.z || 0,
        data.head?.confidence || 0,
        data.leftShoulder?.x || 0,
        data.leftShoulder?.y || 0,
        data.leftShoulder?.z || 0,
        data.leftShoulder?.confidence || 0,
        data.rightShoulder?.x || 0,
        data.rightShoulder?.y || 0,
        data.rightShoulder?.z || 0,
        data.rightShoulder?.confidence || 0,
        data.leftHip?.x || 0,
        data.leftHip?.y || 0,
        data.leftHip?.z || 0,
        data.leftHip?.confidence || 0,
        data.rightHip?.x || 0,
        data.rightHip?.y || 0,
        data.rightHip?.z || 0,
        data.rightHip?.confidence || 0,
        data.detectedMovement || 'AUCUN'
      ].join(',');
      csvContent += row + '\n';
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const csvFile = new File([blob], `pose-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`, { type: 'text/csv;charset=utf-8;' });

    if (this.userId) {
      this.documentService.uploadDocumentForLessonOrAnalysis(this.userId, 'pose_data', csvFile).subscribe({
        next: (document) => {

        },
        error: (err) => {

        }
      });
    }

  }

  uploadFaceCSV(): void {
    if (this.faceDataHistory.length === 0) {
      return;
    }

    let csvContent = 'Timestamp,Face Confidence,Mouth Open,Eye Blink Left,Eye Blink Right,Eye Look Left,Eye Look Right,Head X,Head Y,Head Z,Detected Expression,Detected Movement\n';

    this.faceDataHistory.forEach(entry => {
      const data = entry.data;
      const row = [
        entry.timestamp,
        data.confidence || 0,
        data.mouth_open || 0,
        data.eye_blink_left || 0,
        data.eye_blink_right || 0,
        data.eye_look_left || 0,
        data.eye_look_right || 0,
        data.headPosition?.x || 0,
        data.headPosition?.y || 0,
        data.headPosition?.z || 0,
        data.detectedExpression || 'Neutre',
        data.detectedMovement || 'AUCUN'
      ].join(',');
      csvContent += row + '\n';
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const csvFile = new File([blob], `face-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`, { type: 'text/csv;charset=utf-8;' });

    if (this.userId) {
      this.documentService.uploadDocumentForLessonOrAnalysis(this.userId, 'face_data', csvFile).subscribe({
        next: (document) => {

        },
        error: (err) => {

        }
      });
    }

  }

  uploadHandsCSV(): void {
    if (this.handsDataHistory.length === 0) {
      return;
    }

    let csvContent = 'Timestamp,Hand,Gesture,Confidence,Landmark Count,Detecte Movement\n';

    this.handsDataHistory.forEach(entry => {
      const data = entry.data;
      
      // Left hand data
      if (data.left) {
        const row = [
          entry.timestamp,
          'Left',
          data.left.gesture || '',
          data.left.confidence || 0,
          data.left.landmarks ? data.left.landmarks.length : 0,
          data.left.detectedMovement || 'AUCUN'
        ].join(',');
        csvContent += row + '\n';
      }
      
      // Right hand data
      if (data.right) {
        const row = [
          entry.timestamp,
          'Right',
          data.right.gesture || '',
          data.right.confidence || 0,
          data.right.landmarks ? data.right.landmarks.length : 0,
          data.right.detectedMovement || 'AUCUN'
        ].join(',');
        csvContent += row + '\n';
      }
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const csvFile = new File([blob], `hands-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`, { type: 'text/csv;charset=utf-8;' });

    if (this.userId) {
      this.documentService.uploadDocumentForLessonOrAnalysis(this.userId, 'hands_data', csvFile).subscribe({
        next: (document) => {

        },
        error: (err) => {

        }
      });
    }

  }

  downloadAllCSV(): void {
    this.downloadPoseCSV();
    this.downloadFaceCSV();
    this.downloadHandsCSV();
  }

  uploadAllCSV(): void {
    this.uploadPoseCSV();
    this.uploadFaceCSV();
    this.uploadHandsCSV();
  }

  // ========== COLLECTE DE DONNÉES ==========

  private collectMovementData(timestamp: number): void {
    // Always collect data even if confidence is low
    const hasPoseData = this.bodyAnalysis?.pose && Object.keys(this.bodyAnalysis.pose).length > 0;
    const hasFaceData = this.bodyAnalysis?.face;
    const hasHandsData = this.bodyAnalysis?.hands && 
      (this.bodyAnalysis.hands.left || this.bodyAnalysis.hands.right);
    
    // Collect pose data
    if (hasPoseData) {
      this.poseDataHistory.push({
        timestamp,
        data: {
          confidence: this.bodyAnalysis!.poseConfidence || 0,
          head: this.bodyAnalysis!.pose!['Head'] ? {
            x: this.bodyAnalysis!.pose!['Head'].position?.x || 0,
            y: this.bodyAnalysis!.pose!['Head'].position?.y || 0,
            z: this.bodyAnalysis!.pose!['Head'].position?.z || 0,
            confidence: this.bodyAnalysis!.pose!['Head'].confidence || 0
          } : null,
          leftShoulder: this.bodyAnalysis!.pose!['LeftShoulder'] ? {
            x: this.bodyAnalysis!.pose!['LeftShoulder'].position?.x || 0,
            y: this.bodyAnalysis!.pose!['LeftShoulder'].position?.y || 0,
            z: this.bodyAnalysis!.pose!['LeftShoulder'].position?.z || 0,
            confidence: this.bodyAnalysis!.pose!['LeftShoulder'].confidence || 0
          } : null,
          rightShoulder: this.bodyAnalysis!.pose!['RightShoulder'] ? {
            x: this.bodyAnalysis!.pose!['RightShoulder'].position?.x || 0,
            y: this.bodyAnalysis!.pose!['RightShoulder'].position?.y || 0,
            z: this.bodyAnalysis!.pose!['RightShoulder'].position?.z || 0,
            confidence: this.bodyAnalysis!.pose!['RightShoulder'].confidence || 0
          } : null,
          leftHip: this.bodyAnalysis!.pose!['LeftHip'] ? {
            x: this.bodyAnalysis!.pose!['LeftHip'].position?.x || 0,
            y: this.bodyAnalysis!.pose!['LeftHip'].position?.y || 0,
            z: this.bodyAnalysis!.pose!['LeftHip'].position?.z || 0,
            confidence: this.bodyAnalysis!.pose!['LeftHip'].confidence || 0
          } : null,
          rightHip: this.bodyAnalysis!.pose!['RightHip'] ? {
            x: this.bodyAnalysis!.pose!['RightHip'].position?.x || 0,
            y: this.bodyAnalysis!.pose!['RightHip'].position?.y || 0,
            z: this.bodyAnalysis!.pose!['RightHip'].position?.z || 0,
            confidence: this.bodyAnalysis!.pose!['RightHip'].confidence || 0
          } : null,
          detectedMovement: this.lastMovementDetection?.type || 'AUCUN'
        }
      });
    }

    // Collect face data
    if (hasFaceData) {
      // Get the detected expression
      const expression = this.getFaceExpression();
      
      this.faceDataHistory.push({
        timestamp,
        data: {
          confidence: this.bodyAnalysis!.faceConfidence || 0,
          mouthOpen: this.bodyAnalysis!.face!.mouth_open || 0,
          eyeBlinkLeft: this.bodyAnalysis!.face!.eye_blink_left || 0,
          eyeBlinkRight: this.bodyAnalysis!.face!.eye_blink_right || 0,
          eyeLookLeft: this.bodyAnalysis!.face!.eye_look_left || 0,
          eyeLookRight: this.bodyAnalysis!.face!.eye_look_right || 0,
          headPosition: this.bodyAnalysis!.face!.Head ? {
            x: this.bodyAnalysis!.face!.Head.position?.x || 0,
            y: this.bodyAnalysis!.face!.Head.position?.y || 0,
            z: this.bodyAnalysis!.face!.Head.position?.z || 0
          } : null,
          detectedExpression: expression,
          detectedMovement: this.lastMovementDetection?.type || 'AUCUN'
        }
      });
    }

    // Collect hands data
    if (hasHandsData) {
      this.handsDataHistory.push({
        timestamp,
        data: {
          left: this.bodyAnalysis!.hands!.left ? {
            gesture: this.bodyAnalysis!.hands!.left.gesture || 'unknown',
            handedness: this.bodyAnalysis!.hands!.left.handedness || 'unknown',
            landmarks: this.bodyAnalysis!.hands!.left.landmarks ? this.bodyAnalysis!.hands!.left.landmarks.map((landmark: any) => ({
              x: landmark.x !== undefined ? landmark.x : 0,
              y: landmark.y !== undefined ? landmark.y : 0,
              z: landmark.z !== undefined ? landmark.z : 0
            })) : [],
            confidence: 0,  // Placeholder since confidence isn't available
            detectedMovement: this.lastMovementDetection?.type || 'AUCUN'
          } : null,
          right: this.bodyAnalysis!.hands!.right ? {
            gesture: this.bodyAnalysis!.hands!.right.gesture || 'unknown',
            handedness: this.bodyAnalysis!.hands!.right.handedness || 'unknown',
            landmarks: this.bodyAnalysis!.hands!.right.landmarks ? this.bodyAnalysis!.hands!.right.landmarks.map((landmark: any) => ({
              x: landmark.x !== undefined ? landmark.x : 0,
              y: landmark.y !== undefined ? landmark.y : 0,
              z: landmark.z !== undefined ? landmark.z : 0
            })) : [],
            confidence: 0,  // Placeholder since confidence isn't available
            detectedMovement: this.lastMovementDetection?.type || 'AUCUN'
          } : null
        }
      });
    }
    
  }

  private sendCapturedDataToBackends(): void {
    
    // Check if backend is available before sending data
    this.sendDataToBackend();
    
    // Define type for movement data
    interface MovementData {
      timestamp: number;
      pose: any;
      face: any;
      hands: any;
    }
    
    // Create movement data from collected history
    const allMovementData: MovementData[] = [];
    
    // Combine all collected data into movement records
    const timestamps = new Set([
      ...this.poseDataHistory.map(entry => entry.timestamp),
      ...this.faceDataHistory.map(entry => entry.timestamp),
      ...this.handsDataHistory.map(entry => entry.timestamp)
    ]);
    
    // Create movement records for each timestamp
    Array.from(timestamps).sort().forEach(timestamp => {
      const poseEntry = this.poseDataHistory.find(entry => entry.timestamp === timestamp);
      const faceEntry = this.faceDataHistory.find(entry => entry.timestamp === timestamp);
      const handsEntry = this.handsDataHistory.find(entry => entry.timestamp === timestamp);
      
      const movementRecord = {
        timestamp,
        pose: poseEntry?.data || null,
        face: {
          ...(faceEntry?.data || {}),
          detectedExpression: faceEntry?.data?.detectedExpression || this.getFaceExpression(),
          detectedMovement: faceEntry?.data?.detectedMovement || this.lastMovementDetection?.type || 'AUCUN'
        },
        hands: handsEntry?.data || null
      };
      
      allMovementData.push(movementRecord);
    });
    

    
    

  }
  
  private sendDataToBackend(): void {
    // Define type for movement data
    interface MovementData {
      timestamp: number;
      pose: any;
      face: any;
      hands: any;
    }
    
    // Create movement data from collected history
    const allMovementData: MovementData[] = [];
    
    // Combine all collected data into movement records
    const timestamps = new Set([
      ...this.poseDataHistory.map(entry => entry.timestamp),
      ...this.faceDataHistory.map(entry => entry.timestamp),
      ...this.handsDataHistory.map(entry => entry.timestamp)
    ]);
    
    // Create movement records for each timestamp
    Array.from(timestamps).sort().forEach(timestamp => {
      const poseEntry = this.poseDataHistory.find(entry => entry.timestamp === timestamp);
      const faceEntry = this.faceDataHistory.find(entry => entry.timestamp === timestamp);
      const handsEntry = this.handsDataHistory.find(entry => entry.timestamp === timestamp);
      
      const movementRecord = {
        timestamp,
        pose: poseEntry?.data || null,
        face: {
          ...(faceEntry?.data || {}),
          detectedExpression: faceEntry?.data?.detectedExpression || this.getFaceExpression(),
          detectedMovement: faceEntry?.data?.detectedMovement || this.lastMovementDetection?.type || 'AUCUN'
        },
        hands: handsEntry?.data || null
      };
      
      allMovementData.push(movementRecord);
    });
    

    
    if (allMovementData.length > 0) {
      allMovementData.forEach((movementData, index) => {
        const aiRecord = {
          user: this.userId,
          json_data: movementData,
          movement_detected: true
        };

        this.aiService.createMovementRecord(aiRecord).subscribe({
          next: (record) => {
          },
          error: (err) => {
          }
        });
      });
    } else {
    }
    

    // Also send captured images to Django
    if (this.capturedImagesForSend.length > 0 && this.userId) {
      this.sendMovementData();
    }
  }
  
  private storeDataLocally(): void {
    // Store the collected data locally as JSON for later upload
    const localData = {
      userId: this.userId,
      timestamp: new Date().toISOString(),
      poseData: this.poseDataHistory,
      faceData: this.faceDataHistory,
      handsData: this.handsDataHistory
    };
    
    // Store in localStorage only if in browser environment
    if (typeof localStorage !== 'undefined') {
      const dataStr = JSON.stringify(localData);
      localStorage.setItem('movementData', dataStr);
    }
    
    // Don't automatically download JSON file - user can manually download if needed
    console.log('Movement data stored locally for later upload');
  }

  // ========== MÉTHODES MANQUANTES POUR LE TEMPLATE ==========

  // Toggle CSV dropdown
  toggleCsvDropdown(): void {
    this.isCsvDropdownOpen = !this.isCsvDropdownOpen;
  }
  
  // Send test image from webcam to Django backend
  sendTestImageToDjango(): void {
    if (!this.videoElement || !this.videoElement.nativeElement) {
      console.error('Video element not available');
      return;
    }
    
    const video = this.videoElement.nativeElement;
    
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
      console.error('Video not ready for capture');
      return;
    }
    
    // Create canvas to capture image
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to data URL
      const imageData = canvas.toDataURL('image/png');
      
      // Convert data URL to Blob
      fetch(imageData)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], `test-image-${Date.now()}.png`, { type: 'image/png' });
          
          // Send to Django backend
          if (this.userId) {
            this.documentService.uploadDocumentForLessonOrAnalysis(this.userId, 'test_image', file).subscribe({
              next: (response) => {
                console.log('Test image sent to Django successfully:', response);
              },
              error: (error) => {
                console.error('Error sending test image to Django:', error);
              }
            });
          } else {
            console.error('User ID not available for sending test image');
          }
        })
        .catch(error => {
          console.error('Error converting image to blob:', error);
        });
    }
  }

  private startImageCapture(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Image capture skipped - not in browser environment');
      return;
    }
      
    // Clear any existing interval
    this.stopImageCapture();
      
    // Start capturing images every 3 seconds (more frequent but optimized)
    this.imageCaptureInterval = setInterval(() => {
      const currentTime = Date.now();
      // Only capture if at least 1 second has passed since last capture to prevent overwhelming
      if (currentTime - this.lastCaptureTime < 1000) {
        return; // Skip capture if too frequent
      }
        
      this.lastCaptureTime = currentTime;
        
      if (this.videoElement && this.videoElement.nativeElement) {
        const video = this.videoElement.nativeElement;
          
        // Ensure video is ready and has valid dimensions
        if (video.readyState === video.HAVE_ENOUGH_DATA && video.videoWidth > 0 && video.videoHeight > 0) {
          const canvas = document.createElement('canvas');
          canvas.width = Math.min(video.videoWidth, 320); // Reduce size to optimize
          canvas.height = Math.min(video.videoHeight, 240);
            
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
              
            // Convert to data URL with JPEG format for smaller size
            const imageData = canvas.toDataURL('image/jpeg', 0.7); // JPEG with 70% quality
            this.capturedImages.push(imageData);
              
            // Keep only the last 5 images to prevent memory issues
            if (this.capturedImages.length > 5) {
              this.capturedImages.shift();
            }
              
            // Also add to the movement-specific capture array
            this.capturedImagesForSend.push(imageData);
              
              
            // Keep only the last 3 images in the send array to prevent memory issues
            if (this.capturedImagesForSend.length > 3) {
              this.capturedImagesForSend.shift();
              
            }
          }
        } else {
          console.log('Video not ready for capture, readyState:', video.readyState, 'width:', video.videoWidth);
        }
      }
    }, 3000); // Capture every 3 seconds
  }

  private stopImageCapture(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Image capture stop skipped - not in browser environment');
      return;
    }
    
    if (this.imageCaptureInterval) {
      clearInterval(this.imageCaptureInterval);
      this.imageCaptureInterval = null;
    }
  }


  // Get pose confidence
  getPoseConfidence(): number {
    if (!this.bodyAnalysis) return 0;
    return this.bodyAnalysis.poseConfidence || 0;
  }

  // Get pose status
  getPoseStatus(): string {
    const confidence = this.getPoseConfidence();
    if (confidence > 80) return 'Excellent';
    if (confidence > 60) return 'Bon';
    if (confidence > 40) return 'Moyen';
    if (confidence > 20) return 'Faible';
    return 'Très faible';
  }

  // Get pose details
  getPoseDetails(): string {
    if (!this.bodyAnalysis?.pose) return 'Aucune donnée de pose';
    const parts = Object.keys(this.bodyAnalysis.pose);
    return `Parties détectées: ${parts.length}`;
  }

  // Get face status
  getFaceStatus(): string {
    const confidence = this.bodyAnalysis?.faceConfidence || 0;
    const movement = this.getDetectedMovement();
    
    if (confidence > 80) return `Visage clair - Mouvement: ${movement}`;
    if (confidence > 60) return `Visage visible - Mouvement: ${movement}`;
    if (confidence > 40) return `Visage partiel - Mouvement: ${movement}`;
    if (confidence > 20) return `Visage flou - Mouvement: ${movement}`;
    return `Visage invisible - Mouvement: ${movement}`;
  }

  // Get face expression
  getFaceExpression(): string {
    if (!this.bodyAnalysis?.face) return 'Aucune expression';
    
    // Analyze facial landmarks to detect expressions
    const faceData = this.bodyAnalysis.face;
    
    // Detect expressions based on facial landmarks
    const expression = this.detectFacialExpression(faceData);
    return expression;
  }
  
  // Detect facial expression based on landmarks
  private detectFacialExpression(faceData: any): string {
    // Check for specific facial expressions based on landmarks
    
    // Check for disgust expression (raised upper lip, wrinkled nose)
    if (this.isDisgustDetected(faceData)) {
      return 'Dégoût';
    }
    
    // Check for anger expression (lowered eyebrows, tight lips)
    if (this.isAngerDetected(faceData)) {
      return 'Colère';
    }
    
    // Check for joy expression (smile, eye wrinkles)
    if (this.isJoyDetected(faceData)) {
      return 'Joie';
    }
    
    // Check for surprise expression (raised eyebrows, open mouth)
    if (this.isSurpriseDetected(faceData)) {
      return 'Surprise';
    }
    
    // Check for fear expression (raised eyebrows, tense mouth)
    if (this.isFearDetected(faceData)) {
      return 'Peur';
    }
    
    // Check for sadness expression (drooping mouth corners)
    if (this.isSadnessDetected(faceData)) {
      return 'Tristesse';
    }
    
    // Default to neutral if no specific expression detected
    return 'Neutre';
  }
  
  // Check if disgust is detected
  private isDisgustDetected(faceData: any): boolean {
    // Disgust is often detected by raised upper lip, wrinkled nose
    try {
      // Check if mouth landmarks suggest raised upper lip
      const upperLip = faceData.mouth?.upper_lip;
      const lowerLip = faceData.mouth?.lower_lip;
      
      // If we have mouth landmarks, check for specific configurations
      if (upperLip && lowerLip) {
        // Calculate distances between key points
        // For disgust: upper lip is raised, nose may be wrinkled
        const mouthOpen = this.calculateMouthOpenness(upperLip, lowerLip);
        
        // Additional checks for nose wrinkles if available
        return mouthOpen < 0.1; // Slightly closed mouth with tension
      }
      
      // If we don't have detailed landmarks, use available face data
      if (faceData.mouth_open !== undefined) {
        // Disgust often has a slightly closed mouth but with tension
        return faceData.mouth_open < 0.2;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting disgust:', error);
      return false;
    }
  }
  
  // Check if anger is detected
  private isAngerDetected(faceData: any): boolean {
    try {
      // Anger is often detected by lowered eyebrows, tight lips, tense jaw
      const leftEyebrow = faceData.left_eyebrow;
      const rightEyebrow = faceData.right_eyebrow;
      
      // Check for lowered eyebrows
      if (leftEyebrow || rightEyebrow) {
        // If eyebrows are lowered compared to neutral position
        // This is a simplified check - in reality, you'd compare to baseline
        const eyebrowPosition = this.getEyebrowPosition(leftEyebrow || rightEyebrow);
        if (eyebrowPosition < 0.3) { // Lowered position
          return true;
        }
      }
      
      // Check for tight lips
      if (faceData.mouth_open !== undefined) {
        // Anger often has tightly pressed lips
        return faceData.mouth_open < 0.1;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting anger:', error);
      return false;
    }
  }
  
  // Check if joy is detected
  private isJoyDetected(faceData: any): boolean {
    try {
      // Joy is often detected by smile, eye wrinkles (crow's feet)
      const mouthOpen = faceData.mouth_open || 0;
      const smileIntensity = faceData.smile_intensity || 0;
      
      // If we have smile intensity data
      if (smileIntensity > 0.6) {
        return true;
      }
      
      // Check for open mouth (smile) and other joy indicators
      if (mouthOpen > 0.4) { // More open than neutral
        // Check for eye wrinkles that indicate genuine smile
        const eyeWrinkles = faceData.eye_wrinkles || 0;
        if (eyeWrinkles > 0.5) {
          return true;
        }
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting joy:', error);
      return false;
    }
  }
  
  // Check if surprise is detected
  private isSurpriseDetected(faceData: any): boolean {
    try {
      // Surprise is often detected by raised eyebrows, open mouth
      const mouthOpen = faceData.mouth_open || 0;
      const eyebrowRaised = faceData.eyebrow_raised || 0;
      
      // High mouth openness and raised eyebrows
      if (mouthOpen > 0.6 && eyebrowRaised > 0.7) {
        return true;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting surprise:', error);
      return false;
    }
  }
  
  // Check if fear is detected
  private isFearDetected(faceData: any): boolean {
    try {
      // Fear is often detected by wide eyes, tense mouth
      const eyeOpenness = faceData.eye_openness || 0;
      const mouthTension = faceData.mouth_tension || 0;
      
      // Wide eyes and tense mouth
      if (eyeOpenness > 0.8 && mouthTension > 0.6) {
        return true;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting fear:', error);
      return false;
    }
  }
  
  // Check if sadness is detected
  private isSadnessDetected(faceData: any): boolean {
    try {
      // Sadness is often detected by drooping mouth corners, lowered eyebrows
      const mouthPosition = faceData.mouth_position || 0; // Negative if corners are drooping
      const eyebrowPosition = faceData.eyebrow_position || 0; // Lowered
      
      // Drooping mouth and lowered eyebrows
      if (mouthPosition < -0.3 || eyebrowPosition < 0.2) {
        return true;
      }
      
      return false;
    } catch (error) {
      console.warn('Error detecting sadness:', error);
      return false;
    }
  }
  
  // Helper to calculate mouth openness
  private calculateMouthOpenness(upperLip: any, lowerLip: any): number {
    // This is a simplified calculation
    // In reality, you'd use actual landmark coordinates
    if (upperLip && lowerLip) {
      // Calculate distance between upper and lower lip
      // For now, return a placeholder value
      return Math.abs(upperLip.y - lowerLip.y) || 0.3;
    }
    return 0.3; // Default neutral value
  }
  
  // Helper to get eyebrow position
  private getEyebrowPosition(eyebrow: any): number {
    // Simplified eyebrow position calculation
    return eyebrow?.y ? Math.max(0, Math.min(1, eyebrow.y)) : 0.5; // Normalize to 0-1
  }

  // Get hands status
  getHandsStatus(): string {
    const hands = this.bodyAnalysis?.hands;
    if (!hands) return 'Mains non détectées';
    
    const leftDetected = hands.left !== null;
    const rightDetected = hands.right !== null;
    
    if (leftDetected && rightDetected) return 'Deux mains détectées';
    if (leftDetected) return 'Main gauche détectée';
    if (rightDetected) return 'Main droite détectée';
    return 'Aucune main détectée';
  }

  // Get hands gestures
  getHandsGestures(): string {
    const hands = this.bodyAnalysis?.hands;
    if (!hands) return 'Aucun geste';
    
    const gestures = [];
    if (hands.left?.gesture) gestures.push(`Gauche: ${hands.left.gesture}`);
    if (hands.right?.gesture) gestures.push(`Droite: ${hands.right.gesture}`);
    
    return gestures.length > 0 ? gestures.join(', ') : 'Aucun geste';
  }

  // Get system status
  getSystemStatus(): any {
    return {
      camera: this.isVideoInitialized ? '🟢 Active' : '🔴 Inactive',
      analysis: this.isTracking ? '🟢 En cours' : '🔴 Arrêtée',
      fps: `${this.fps} FPS`,
      posture: this.getPoseStatus()
    };
  }



  // Download temporary video
  downloadTemporaryVideo(): void {
    if (!this.temporaryVideoBlob) {
      return;
    }

    const url = URL.createObjectURL(this.temporaryVideoBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `temporary-video-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.webm`;
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }

  // Upload temporary video to backend
  uploadTemporaryVideo(): void {
    if (!this.temporaryVideoBlob) {
      this.errorMessage = 'No temporary video available for upload';
      return;
    }

    if (!this.userId) {
      this.errorMessage = 'No user ID available';
      return;
    }

    const filename = `recorded-video-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.webm`;
    
    this.videoUploadService.uploadVideo(this.temporaryVideoBlob, this.userId, filename).subscribe({
      next: (response) => {
        alert('Video uploaded successfully!');
      },
      error: (err) => {
        this.errorMessage = 'Error uploading video: ' + (err.message || 'Unknown error');
        alert('Error uploading video');
      }
    });
  }

  // Get face confidence
  getFaceConfidence(): number {
    if (!this.bodyAnalysis) return 0;
    return this.bodyAnalysis.faceConfidence || 0;
  }

  // ========== MÉTHODES POUR LE TÉLÉCHARGEMENT DE VIDÉO ==========

  onVideoFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file && file.type.startsWith('video/')) {
      this.selectedVideoFile = file;
      this.errorMessage = '';
    } else {
      this.errorMessage = 'Veuillez sélectionner un fichier vidéo valide.';
    }
  }

  async processVideoFile(): Promise<void> {
    if (!this.selectedVideoFile) {
      this.errorMessage = 'Aucun fichier vidéo sélectionné.';
      return;
    }

    this.isProcessingVideo = true;
    this.errorMessage = '';

    try {
      const videoUrl = URL.createObjectURL(this.selectedVideoFile);
      
      // Set the video element source to the selected file
      if (this.videoElement) {
        this.videoElement.nativeElement.src = videoUrl;
        
        // Initialize MediaPipe for the video file
        await this.videoService.initializeMediaPipe();
        
        // For video files, we need to handle analysis differently than webcam
        // We'll manually trigger analysis on video events
        this.videoElement.nativeElement.onloadeddata = async () => {
          // Only proceed if in browser environment
          if (typeof window !== 'undefined') {
            // CRITICAL: Setup Holistic BEFORE starting analysis
            await this.videoService.setupHolistic(this.videoElement.nativeElement);
            
            this.isTracking = true;
            this.isVideoInitialized = true;
            this.analysisStartTime = Date.now();
            
            // Load current user to ensure authentication
            await this.loadCurrentUser();
            
            // Start analysis loop WITH proper setup
            this.startVideoAnalysisLoop();
            this.startImageCapture();
            this.startDataSending();
          }
        };
        
        // Handle video end to stop analysis
        this.videoElement.nativeElement.onended = () => {
          this.stopVideoAnalysisLoop();
          this.stopImageCapture();
          this.stopDataSending();
          this.isTracking = false;
        };
        
        this.videoElement.nativeElement.play();
      }
    } catch (error) {
      this.errorMessage = 'Erreur lors du traitement de la vidéo: ' + (error as Error).message;
    } finally {
      this.isProcessingVideo = false;
    }
  }

  // Method to store video after analysis
  storeAnalyzedVideo(): void {
    
    // The video from CSV is already created by createVideoFromPoseCSV
    // which receives the video URL from the backend
    // If no backend video URL is set, we can use the temporary video as fallback
    if (this.temporaryVideoBlob && !this.storedVideoUrl) {
      // Create a local URL for immediate display
      const storedUrl = URL.createObjectURL(this.temporaryVideoBlob);
      this.storedVideoUrl = storedUrl;
      // Store the URL so we can revoke it later
      this.temporaryVideoUrl = storedUrl;
    }
  }

  downloadStoredVideo(): void {
    if (!this.storedVideoUrl) {
      return;
    }

    // Create a temporary link to download the video
    const a = document.createElement('a');
    a.href = this.storedVideoUrl;
    a.download = `analyzed-video-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.webm`;
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(this.storedVideoUrl!);
    }, 100);
  }

  // ========== MÉTHODES POUR LE TÉLÉCHARGEMENT D'IMAGE ==========

  onImageFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      this.selectedImageFile = file;
      this.errorMessage = '';
    } else {
      this.errorMessage = 'Veuillez sélectionner un fichier image valide.';
    }
  }

  async processImageFile(): Promise<void> {
    if (!this.selectedImageFile) {
      this.errorMessage = 'Aucun fichier image sélectionné.';
      return;
    }

    this.isProcessingImage = true;
    this.errorMessage = '';

    try {
      // In a real implementation, we would process the image file using MediaPipe
      // For now, we'll simulate the processing by creating a URL for the selected file
      const imageUrl = URL.createObjectURL(this.selectedImageFile);
      
      // Set the video element source to the selected image
      if (this.videoElement) {
        this.videoElement.nativeElement.src = imageUrl;
                
        // Initialize MediaPipe for the image file
        await this.videoService.initializeMediaPipe();
                
        // For images, analyze once when loaded
        this.videoElement.nativeElement.onloadeddata = async () => {
          // Only proceed if in browser environment
          if (typeof window !== 'undefined') {
            this.isTracking = true;
            this.isVideoInitialized = true;
            this.analysisStartTime = Date.now();
                    
            // Analyze the image once
            await this.analyzeImageFrame();
          }
        };
                
        this.videoElement.nativeElement.play();
      }
    } catch (error) {
      this.errorMessage = 'Erreur lors du traitement de l' + "'" + 'image: ' + (error as Error).message;
    } finally {
      this.isProcessingImage = false;
    }
  }

  // Initialize Three.js scene
  private initThreeScene(): void {
    // Check if we're in browser environment and container exists
    if (typeof window === 'undefined' || !this.threeDContainer) {
      console.error('3D Container not found or not in browser environment');
      return;
    }

    // Create scene
    this.scene = new THREE.Scene();
    // Remove background color to make it transparent

    // Create camera with fixed aspect ratio
    this.camera = new THREE.PerspectiveCamera(75, 400 / 300, 0.1, 1000);
    this.camera.position.set(0, 0, 5); // Position camera in front of the VRM model

    // Create renderer with transparent background
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(400, 300);
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.setClearColor(0x000000, 0); // Transparent background
    
    // Add renderer to container
    const container = this.threeDContainer.nativeElement;
    container.appendChild(this.renderer.domElement);

    // Initialize OrbitControls for mouse interaction
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true; // Smooth camera movement
    this.controls.dampingFactor = 0.05;
    this.controls.screenSpacePanning = false;
    this.controls.minDistance = 1;
    this.controls.maxDistance = 10;
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    this.scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    this.scene.add(directionalLight);

    // Load the VRM model
    this.loadVRMModel();

    // Add event listener for clicks
    this.renderer.domElement.addEventListener('click', this.onModelClick.bind(this));

    // Start animation loop
    this.animate();
  }

  private async loadVRMModel(): Promise<void> {
    console.log('Starting VRM model loading...');
    
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('VRM model loading skipped - not in browser environment');
      return;
    }
    
    try {
      // Remove any existing model before loading VRM
      if (this.carModel) {
        console.log('Removing existing car model');
        this.scene.remove(this.carModel);
        this.carModel = undefined as any;
      }
      
      if (this.vrmModel) {
        console.log('Removing existing VRM model');
        this.scene.remove(this.vrmModel);
        this.vrmModel = undefined as any;
      }
      
      // Load the VRM model from the specified path
      const loader = new GLTFLoader();
      
      console.log('Loading VRM file from /5749760313079890670.vrm');
      
      // Try loading the VRM file from the public directory
      let gltf;
      try {
        gltf = await loader.loadAsync('/5749760313079890670.vrm');
      } catch (loadError) {
        console.warn('Failed to load VRM from /5749760313079890670.vrm, trying alternative path...');
        // Try alternative path in case of deployment configuration differences
        gltf = await loader.loadAsync('assets/5749760313079890670.vrm');
      }
      
      console.log('VRM file loaded, processing with VRMUtils...');
      
      // Process the VRM properly using VRMUtils to handle the skeleton
      // Use the non-deprecated method
      VRMUtils.combineSkeletons(gltf.scene);
      
      // Try to extract VRM from the loaded GLTF using the proper API
      // The VRM object should be available after processing
      let vrm = null;
      
      // First try to get VRM from userData (common approach)
      if (gltf.userData && gltf.userData['vrm']) {
        vrm = gltf.userData['vrm'];
      }
      
      // If not found in userData, try to get from gltfExtensions (where VRM data is typically stored)
      if (!vrm) {
        const gltfAny = gltf as any;
        if (gltfAny.gltfExtensions && gltfAny.gltfExtensions['VRM']) {
          vrm = gltfAny.gltfExtensions['VRM'];
        }
      }
      
      // If still not found, try to access from scene children
      if (!vrm) {
        for (const child of gltf.scene.children) {
          if (child.userData && child.userData['vrm']) {
            vrm = child.userData['vrm'];
            break;
          }
        }
      }
      
      // If still no VRM found, we'll use the GLTF scene directly
      if (vrm) {
        console.log('VRM model found, setting up...');
        
        // Check if vrm has humanoid property (essential for pose control)
        if (!vrm.humanoid) {
          console.warn('VRM loaded but has no humanoid property - this may be a static model');
        }
        
        // Set up the VRM model
        vrm.scene.rotation.y = Math.PI; // Rotate 180 degrees to face the camera
        this.scene.add(vrm.scene);
        
        this.vrm = vrm;
        this.vrmModel = vrm.scene;
        this.isModelLoaded = true;
        
        console.log('VRM model loaded successfully');
      } else {
        console.warn('VRM data not found, using GLTF scene directly as fallback');
        
        // Use the GLTF scene directly since no VRM data was found
        // This means the file might be a rigged model that's not a proper VRM
        gltf.scene.rotation.y = Math.PI; // Rotate 180 degrees to face the camera
        this.scene.add(gltf.scene);
        
        this.vrmModel = gltf.scene;
        this.isModelLoaded = true;
        
        // Set vrm to null since we're using the scene directly
        this.vrm = null;
        
        console.log('GLTF scene loaded as fallback');
      }
    } catch (error) {
      console.error('Error loading VRM model:', error);
      
      // Don't create any fallback - only VRM should be displayed
      this.isModelLoaded = false;
    }
  }

  private createCarModel(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Car model creation skipped - not in browser environment');
      return;
    }
    
    // Create a simple fallback model
    this.carModel = new THREE.Group();
    
    // Create a simple sphere as fallback
    const geometry = new THREE.SphereGeometry(0.5, 32, 32);
    const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 }); // Green sphere
    const sphere = new THREE.Mesh(geometry, material);
    sphere.position.y = 0;
    this.carModel.add(sphere);
    
    // Position the fallback model at the center of the camera view
    this.carModel.position.set(0, 0, -3);
    this.scene.add(this.carModel);
    
    this.isModelLoaded = true;
  }

  private lastFrameTime = 0;

  private animate = (): void => {
    if (typeof window === 'undefined') return;

    requestAnimationFrame(this.animate);

    // Calculate deltaTime
    const now = performance.now();
    const deltaTime = (now - this.lastFrameTime) / 1000;
    this.lastFrameTime = now;

    // Update model position
    this.updateModelPosition();

    // Update VRM with proper deltaTime
    if (this.vrm && this.bodyAnalysis?.pose) {
      this.vrm.update(Math.min(deltaTime, 0.016)); // Cap at 60fps
      this.updateVRMBones(this.bodyAnalysis.pose);
    }

    // Update controls
    if (this.controls) {
      this.controls.update();
    }

    this.renderer.render(this.scene, this.camera);
  }

  private onModelClick(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Model click handling skipped - not in browser environment');
      return;
    }
    
    this.showModelInfo = !this.showModelInfo;
  }

  // Update model position based on body tracking
  private updateModelPosition(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined' || !this.isModelLoaded || !this.bodyAnalysis) return;
    
    // Get pose data if available
    const pose = this.bodyAnalysis.pose;
    
    if (pose) {
      console.log('Pose data received:', pose);
      
      // This is a simplified example - in reality, you'd map specific body landmarks
      // to control the 3D model position
      
      // For example, use head position to move the model
      const head = pose['Head'];
      if (head && head.position && head.position.x !== undefined && 
          head.position.y !== undefined && head.position.z !== undefined) {
        // Map the head position to 3D space coordinates
        // Invert x to match camera view (mirror effect)
        this.modelPosition.x = -(head.position.x - 0.5) * 3; // Adjust range and invert for mirror effect
        this.modelPosition.y = (head.position.y - 0.5) * 2; // Adjust range
        // Don't change Z position much, keep VRM in front
        this.modelPosition.z = -3; // Keep VRM fixed in front
        
        // Update VRM model position if it exists
        if (this.vrmModel) {
          this.vrmModel.position.x = this.modelPosition.x;
          this.vrmModel.position.y = this.modelPosition.y;
          this.vrmModel.position.z = this.modelPosition.z;
        }
        
        // Update VRM humanoid bones based on body tracking data
        if (this.vrm) {
          this.updateVRMBones(pose);
        }
      } else {
        // If no head data, still try to update with other pose data
        if (this.vrm) {
          this.updateVRMBones(pose);
        }
      }
    }
  }
  
  private updateVRMBones(pose: any): void {
    if (typeof window === 'undefined' || !this.vrm?.humanoid) {
      return;
    }

    try {
      // Helper function to safely get and rotate bone
      const rotateBone = (boneName: string, rotX: number, rotY: number, rotZ: number) => {
        const bone = this.vrm?.humanoid?.getRawBoneNode(boneName as any);
        if (bone) {
          bone.rotation.x = rotX;
          bone.rotation.y = rotY;
          bone.rotation.z = rotZ;
        }
      };

      // Head rotation based on head position
      const head = pose['Head'];
      if (head?.position) {
        const headX = (head.position.y - 0.5) * Math.PI; // Pitch
        const headY = -(head.position.x - 0.5) * Math.PI; // Yaw
        rotateBone('head', headX * 0.5, headY * 0.5, 0);
      }

      // Spine rotation based on shoulder alignment
      const leftShoulder = pose['LeftShoulder'];
      const rightShoulder = pose['RightShoulder'];
      
      if (leftShoulder?.position && rightShoulder?.position) {
        const shoulderDiff = leftShoulder.position.y - rightShoulder.position.y;
        const shoulderAngle = Math.atan2(shoulderDiff, 0.3) * 0.3;
        rotateBone('spine', 0, 0, shoulderAngle);
      }

      // Left arm based on shoulder-elbow-wrist
      const leftShoulder_pos = pose['LeftShoulder']?.position;
      const leftElbow = pose['LeftElbow']?.position;
      const leftWrist = pose['LeftWrist']?.position;

      if (leftShoulder_pos && leftElbow && leftWrist) {
        const elbowAngle = this.calculateBoneAngle(leftShoulder_pos, leftElbow, leftWrist);
        rotateBone('leftUpperArm', -0.2, -0.3, 0);
        rotateBone('leftLowerArm', -elbowAngle * 0.3, 0, 0);
      }

      // Right arm (mirror of left)
      const rightShoulder_pos = pose['RightShoulder']?.position;
      const rightElbow = pose['RightElbow']?.position;
      const rightWrist = pose['RightWrist']?.position;

      if (rightShoulder_pos && rightElbow && rightWrist) {
        const elbowAngle = this.calculateBoneAngle(rightShoulder_pos, rightElbow, rightWrist);
        rotateBone('rightUpperArm', -0.2, 0.3, 0);
        rotateBone('rightLowerArm', -elbowAngle * 0.3, 0, 0);
      }

      // Hip and leg rotations
      const leftHip = pose['LeftHip']?.position;
      const rightHip = pose['RightHip']?.position;
      
      if (leftHip && rightHip) {
        const hipDiff = leftHip.y - rightHip.y;
        rotateBone('hips', 0, 0, hipDiff * 0.2);
      }

      // Update hands based on hand tracking data
      if (this.bodyAnalysis?.hands) {
        this.updateVRMHands(this.bodyAnalysis.hands);
      }
      
      // Update face expressions based on face tracking data
      if (this.bodyAnalysis?.face) {
        this.updateVRMFace(this.bodyAnalysis.face);
      }

    } catch (error) {
      console.warn('Erreur lors de la mise à jour des bones VRM:', error);
    }
  }

  // Helper method for calculating bone angles
  private calculateBoneAngle(point1: any, point2: any, point3: any): number {
    if (!point1 || !point2 || !point3) return 0;
    
    const v1 = { x: point2.x - point1.x, y: point2.y - point1.y };
    const v2 = { x: point3.x - point2.x, y: point3.y - point2.y };
    
    const dot = v1.x * v2.x + v1.y * v2.y;
    const det = v1.x * v2.y - v1.y * v2.x;
    
    return Math.atan2(det, dot);
  }
  
  private updateVRMHands(hands: any): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined' || !this.vrm || !this.vrm.humanoid) return;
    
    console.log('Updating VRM hands with hand data:', hands);
    
    // Update left hand
    if (hands.left && hands.left.confidence > 0.5) {
      const leftHandBone = this.vrm.humanoid.getRawBoneNode('leftHand');
      if (leftHandBone) {
        console.log('Updating left hand bone with gesture:', hands.left.gesture);
        // Apply hand gesture based on detected gesture
        const gesture = hands.left.gesture;
        if (gesture === 'FIST') {
          // Apply fist pose
          leftHandBone.rotation.x = 0.5;
          leftHandBone.rotation.y = 0.2;
          leftHandBone.rotation.z = -0.3;
        } else if (gesture === 'VICTORY') {
          // Apply victory pose
          leftHandBone.rotation.x = -0.2;
          leftHandBone.rotation.y = 0.1;
          leftHandBone.rotation.z = 0.4;
        }
      }
    }
    
    // Update right hand
    if (hands.right && hands.right.confidence > 0.5) {
      const rightHandBone = this.vrm.humanoid.getRawBoneNode('rightHand');
      if (rightHandBone) {
        console.log('Updating right hand bone with gesture:', hands.right.gesture);
        // Apply hand gesture based on detected gesture
        const gesture = hands.right.gesture;
        if (gesture === 'FIST') {
          // Apply fist pose
          rightHandBone.rotation.x = 0.5;
          rightHandBone.rotation.y = -0.2;
          rightHandBone.rotation.z = 0.3;
        } else if (gesture === 'VICTORY') {
          // Apply victory pose
          rightHandBone.rotation.x = -0.2;
          rightHandBone.rotation.y = -0.1;
          rightHandBone.rotation.z = -0.4;
        }
      }
    }
  }
  
  private updateVRMFace(face: any): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined' || !this.vrm) return;
    
    // Update face expressions based on detected expressions
    const expression = this.getFaceExpression();
    
    // VRM face expressions would be implemented here
    // For now, we just log the detected expression
    console.log('Detected expression:', expression);
  }

  
  
  // Handle window resize
  private onWindowResize(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Window resize handling skipped - not in browser environment');
      return;
    }
    
    if (this.camera && this.renderer && this.threeDContainer) {
      const container = this.threeDContainer.nativeElement;
      this.camera.aspect = container.clientWidth / container.clientHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(container.clientWidth, container.clientHeight);
    }
  }
  
  // Load Django autonomous data
  private loadDjangoData(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Django data loading skipped - not in browser environment');
      return;
    }
    
    // Load Django data with error handling for unauthenticated access
    setTimeout(() => this.loadDjangoUsers(), 100);
    setTimeout(() => this.loadDjangoOffers(), 200);
    setTimeout(() => this.loadDjangoUserOffers(), 300);
    setTimeout(() => this.loadDjangoCourseLessons(), 400);
    setTimeout(() => this.loadDjangoTestQuestions(), 500);
  }
  
  private loadDjangoUsers(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Django users loading skipped - not in browser environment');
      return;
    }
    
    this.usersLoading = true;
    this.djDataService.getAllUsers().subscribe({
      next: (users) => {
        this.djangoUsers = users;
        this.usersLoading = false;
      },
      error: (error) => {
        // Handle 404 error specifically - it means user is not authenticated
        if (error.status === 404) {
          console.log('Django users not accessible - user not authenticated (404)');
        } else {
          console.error('Error loading Django users:', error);
        }
        this.usersLoading = false;
      }
    });
  }
  
  private loadDjangoOffers(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Django offers loading skipped - not in browser environment');
      return;
    }
    
    this.offersLoading = true;
    this.djDataService.getAllOffers().subscribe({
      next: (offers) => {
        this.djangoOffers = offers;
        this.offersLoading = false;
      },
      error: (error) => {
        // Handle 404 error specifically - it means user is not authenticated
        if (error.status === 404) {
          console.log('Django offers not accessible - user not authenticated (404)');
        } else {
          console.error('Error loading Django offers:', error);
        }
        this.offersLoading = false;
      }
    });
  }
  
  private loadDjangoUserOffers(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Django user offers loading skipped - not in browser environment');
      return;
    }
    
    this.userOffersLoading = true;
    this.djDataService.getAllUserOffers().subscribe({
      next: (userOffers) => {
        this.djangoUserOffers = userOffers;
        this.userOffersLoading = false;
      },
      error: (error) => {
        // Handle 404 error specifically - it means user is not authenticated
        if (error.status === 404) {
          console.log('Django user offers not accessible - user not authenticated (404)');
        } else {
          console.error('Error loading Django user offers:', error);
        }
        this.userOffersLoading = false;
      }
    });
  }
  
  private loadDjangoCourseLessons(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Django course lessons loading skipped - not in browser environment');
      return;
    }
    
    this.lessonsLoading = true;
    this.djDataService.getAllCourseLessons().subscribe({
      next: (lessons) => {
        this.djangoCourseLessons = lessons;
        this.lessonsLoading = false;
      },
      error: (error) => {
        // Handle 404 error specifically - it means user is not authenticated
        if (error.status === 404) {
          console.log('Django course lessons not accessible - user not authenticated (404)');
        } else {
          console.error('Error loading Django course lessons:', error);
        }
        this.lessonsLoading = false;
      }
    });
  }
  
  private loadDjangoTestQuestions(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Django test questions loading skipped - not in browser environment');
      return;
    }
    
    this.questionsLoading = true;
    this.djDataService.getAllTestQuestions().subscribe({
      next: (questions) => {
        this.djangoTestQuestions = questions;
        this.questionsLoading = false;
      },
      error: (error) => {
        // Handle 404 error specifically - it means user is not authenticated
        if (error.status === 404) {
          console.log('Django test questions not accessible - user not authenticated (404)');
        } else {
          console.error('Error loading Django test questions:', error);
        }
        this.questionsLoading = false;
      }
    });
  }
  
  private initDjangoAuth(): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Django authentication initialization skipped - not in browser environment');
      return;
    }
    
    // Subscribe to Django authentication state
    this.djAuthService.currentUser$.subscribe(user => {
      this.djUser = user;
      console.log('Django user updated:', user);
    });
    
    // Try to get current Django user
    this.djAuthService.getCurrentUser().subscribe({
      next: (user) => {
        if (user) {
          console.log('Successfully authenticated with Django:', user);
        } else {
          console.log('Not authenticated with Django');
        }
      },
      error: (error) => {
        // Handle 404 error specifically - it means user is not authenticated
        if (error.status === 404) {
          console.log('User not authenticated with Django (404)');
        } else {
          console.error('Error getting Django user:', error);
        }
      }
    });
  }

  private async analyzeImageFrame(): Promise<void> {
    // Check if we're in browser environment
    if (typeof window === 'undefined' || !this.videoElement || !this.videoElement.nativeElement) {
      return;
    }
    
    try {
      // Use the new static content analysis method
      await this.videoService.analyzeStaticContent(this.videoElement.nativeElement);
    } catch (error) {
      console.error('Error analyzing image frame:', error);
    }
  }

  private videoAnalysisInterval: any;

  private startVideoAnalysisLoop(): void {
    // Stop any existing analysis loop
    this.stopVideoAnalysisLoop();
    
    // Start a new analysis loop for the video
    this.videoAnalysisInterval = setInterval(() => {
      this.analyzeVideoFrame();
    }, 100); // Analyze every 100ms
  }

  private stopVideoAnalysisLoop(): void {
    if (this.videoAnalysisInterval) {
      clearInterval(this.videoAnalysisInterval);
      this.videoAnalysisInterval = null;
    }
  }

  private async analyzeVideoFrame(): Promise<void> {
    // Check if we're in browser environment
    if (typeof window === 'undefined' || !this.videoElement || !this.videoElement.nativeElement || 
        this.videoElement.nativeElement.paused || this.videoElement.nativeElement.ended) {
      return;
    }
      
    const video = this.videoElement.nativeElement;
      
    // Check that the video is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA || 
        video.videoWidth === 0 || 
        video.videoHeight === 0) {
      return;
    }
      
    try {
      // Use analyzeFrame instead of analyzeStaticContent
      await (this.videoService as any).analyzeFrame(video);
        
      // Capture frame for sending
      this.captureVideoFrameImage(video);
        
      // Send data immediately for video processing
      if (this.userId && this.capturedImagesForSend.length > 0) {
        this.sendMovementData();
      }
    } catch (error) {
      console.error('Erreur lors de l\'analyse de la frame vidéo:', error);
    }
  }
  
  private captureVideoFrameImage(video: HTMLVideoElement): void {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Frame capture skipped - not in browser environment');
      return;
    }
    
    // Ensure video is ready and has valid dimensions
    if (video.readyState !== video.HAVE_ENOUGH_DATA || 
        video.videoWidth === 0 || 
        video.videoHeight === 0) {
      return;
    }
    
    const canvas = document.createElement('canvas');
    canvas.width = Math.min(video.videoWidth, 320); // Reduce size to optimize
    canvas.height = Math.min(video.videoHeight, 240);
    
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to data URL with JPEG format for smaller size
      const imageData = canvas.toDataURL('image/jpeg', 0.7); // JPEG with 70% quality
      
      console.log('📸 Frame captured - image length:', imageData.length);
      
      // Add to the captured images array for processing
      this.capturedImages.push(imageData);
      
      // Keep only the last 5 images to prevent memory issues
      if (this.capturedImages.length > 5) {
        this.capturedImages.shift();
      }
      
      // Also add to the movement-specific capture array for backend sending
      this.capturedImagesForSend.push(imageData);
      
      // Keep only the last 3 images in the send array to prevent memory issues
      if (this.capturedImagesForSend.length > 3) {
        this.capturedImagesForSend.shift();
      }
      
      console.log('📊 Images for send array length:', this.capturedImagesForSend.length);
    }
  }
}
