import { Component, OnInit, AfterViewInit, OnDestroy, OnChanges, SimpleChanges, ViewChild, ElementRef, Input, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideoService, BodyAnalysis } from '../video.service';
import { AuthService, User } from '../auth.service';
import { DataService } from '../services/data.service';
import { AiService } from '../services/ai.service';
import { DocumentService } from '../services/document.service';
import { VideoUploadService } from '../services/video-upload.service';
import { DjDataService, DjangoUser, DjangoOffer, DjangoUserOffer, DjangoCourseLesson, DjangoTestQuestion } from '../services/dj-data.service';
import { DjAuthService, DjUser } from '../services/dj-auth.service';

// MediaPipe holistic import
import { FACEMESH_TESSELATION, HAND_CONNECTIONS, Holistic, POSE_CONNECTIONS } from '@mediapipe/holistic';

// Modern MediaPipe Tasks API
import {
  PoseLandmarker,
  FaceLandmarker,
  HandLandmarker,
  FilesetResolver,
  HolisticLandmarker,
  DrawingUtils,
  Landmark
} from '@mediapipe/tasks-vision';

// For drawing utilities
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';

import { Camera, Camera as MpCamera } from '@mediapipe/camera_utils';



import {
  VRM,
  VRMLoaderPlugin,
  VRMUtils,
  VRMHumanBoneName,
  VRMExpressionPresetName,
} from '@pixiv/three-vrm';

// Import Three.js types
import * as THREE from 'three';
import { GLTFLoader } from 'three-stdlib';
import { OrbitControls } from 'three-stdlib';
import * as Kalidokit from 'kalidokit';


import { THand } from 'kalidokit';

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
export class VideoComponent implements OnInit, AfterViewInit, OnDestroy, OnChanges {
  @ViewChild('videoElement') videoElement!: ElementRef;
  @ViewChild('canvasElement') canvasElement!: ElementRef;
  @ViewChild('threeDContainer') threeDContainer!: ElementRef;

  // 3D View properties
  showFull3DView = false;
  
  // Three.js related properties
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private renderer!: THREE.WebGLRenderer;
  private controls: OrbitControls | null = null;
  private carModel!: THREE.Group;
  private vision!: any;
  private clock = new THREE.Clock();
  private holistic: Holistic | null = null;
  private mpCamera: MpCamera | null = null;
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
  
  // Video frame capture interval for video files
  private videoFrameCaptureInterval: any = null;
  
  // Landmark tracking for movement detection
  private previousLandmarks: any = null;
  private previousVrmBones: any = null;
  
  // Avatar bones information
  private avatarBonesInfo: string = '';
  
  // VRM properties
  private vrm: VRM | null = null;
  private vrmModel: THREE.Object3D | null = null;

  // Holistic MediaPipe properties
  private lastHolisticResults: any;
  
  // Kalidokit configuration
  private kalidokitConfig: {
    face: {
      runtime: 'mediapipe' | 'tfjs';
      video: HTMLVideoElement;
      imageSize: {
        height: number;
        width: number;
      };
      smoothBlink: boolean;
      blinkSettings: [number, number];
    };
    pose: {
      runtime: 'mediapipe' | 'tfjs';
      video: HTMLVideoElement;
      imageSize: {
        height: number;
        width: number;
      };
      enableLegs: boolean;
    };
    stabilizeBlink: {
      noWink: boolean;
      maxRot: number;
    };
  } | null = null;
  
  // Canvas references for guides
  @ViewChild('guideCanvas', { static: false }) guideCanvasRef!: ElementRef;
  
  // Hand position tracking
  private leftHandWorld = new THREE.Vector3();
  private rightHandWorld = new THREE.Vector3();
  
  // Current VRM reference for easier access
  private currentVrm: VRM | null = null;
  
  // Subscription for body analysis
  private bodyAnalysisSubscription: any = null;

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
    
    // Update renderer size after view is initialized
    setTimeout(() => {
      this.updateRendererSize();
    }, 100);
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
    
    // Unsubscribe from body analysis subscription
    if (this.bodyAnalysisSubscription) {
      this.bodyAnalysisSubscription.unsubscribe();
      this.bodyAnalysisSubscription = null;
    }
  }
}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['videoUrl'] && changes['videoUrl'].currentValue) {
      // When video URL changes, ensure holistic processing is set up
      console.log('Video URL changed, ensuring holistic setup');
      // The video URL change is handled elsewhere in the component
    }
  }

  toggleFull3DView(): void {
    this.showFull3DView = !this.showFull3DView;
    
    // Update renderer size after view changes
    setTimeout(() => {
      this.updateRendererSize();
    }, 100); // Small delay to ensure DOM updates
  }

  private updateRendererSize(): void {
    if (this.threeDContainer && this.renderer && this.camera) {
      const container = this.threeDContainer.nativeElement;
      const width = container.clientWidth;
      const height = container.clientHeight;
      
      this.renderer.setSize(width, height);
      
      // Update camera aspect ratio
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
    }
  }
  
  private showNotification(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    // Create a simple notification element
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '15px 20px';
    notification.style.borderRadius = '8px';
    notification.style.color = 'white';
    notification.style.zIndex = '10000';
    notification.style.fontWeight = 'bold';
      
    // Set color based on type
    if (type === 'success') {
      notification.style.backgroundColor = '#27ae60';
    } else if (type === 'error') {
      notification.style.backgroundColor = '#e74c3c';
    } else {
      notification.style.backgroundColor = '#3498db';
    }
      
    // Add to document
    document.body.appendChild(notification);
      
    // Remove after 5 seconds
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 5000);
  }
    
  private displayAvatarBones(): void {
    if (!this.currentVrm) {
      this.avatarBonesInfo = 'No avatar loaded';
      console.log(this.avatarBonesInfo);
      this.showNotification('No avatar loaded', 'info');
      return;
    }
      
    if (this.currentVrm.humanoid) {
      // VRM model with humanoid rigging
      const humanoid = this.currentVrm.humanoid;
      const boneList = [];
        
      // Get all available bone types
      const boneTypes = Object.keys(VRMHumanBoneName);
        
      for (const boneType of boneTypes) {
        const bone = humanoid.getNormalizedBoneNode(VRMHumanBoneName[boneType as keyof typeof VRMHumanBoneName]);
        if (bone) {
          boneList.push(`${boneType}: [${bone.position.x.toFixed(2)}, ${bone.position.y.toFixed(2)}, ${bone.position.z.toFixed(2)}]`);
        }
      }
        
      this.avatarBonesInfo = `VRM Avatar Bones (${boneList.length} total):\n${boneList.join('\n')}`;
      console.log('VRM AVATAR BONES:', this.avatarBonesInfo);
        
      // Display the bone info in a notification
      this.showNotification(`VRM Bones: ${boneList.length} total`, 'info');
    } else {
      // GLTF model without humanoid rigging - display general information
      this.avatarBonesInfo = 'GLTF model loaded (no humanoid rigging) - Bones tracking not available';
      console.log(this.avatarBonesInfo);
        
      // Display the info in a notification
      this.showNotification('GLTF model (no bones tracking)', 'info');
    }
  }
    
  // Public method to get avatar bones info
  getAvatarBonesInfo(): string {
    return this.avatarBonesInfo;
  }
    
  private calculateLandmarkMovement(prevLandmarks: any, currentLandmarks: any): string {
    if (!prevLandmarks || !currentLandmarks) {
      return 'No previous landmarks to compare';
    }
      
    let movementInfo = 'Landmark Movement Differences:\n';
      
    // Compare pose landmarks if available
    if (prevLandmarks.poseLandmarks && currentLandmarks.poseLandmarks) {
      const prevPose = prevLandmarks.poseLandmarks;
      const currPose = currentLandmarks.poseLandmarks;
        
      for (let i = 0; i < Math.min(prevPose.length, currPose.length); i++) {
        const prev = prevPose[i];
        const curr = currPose[i];
          
        if (prev && curr) {
          const dx = Math.abs(curr.x - prev.x);
          const dy = Math.abs(curr.y - prev.y);
          const dz = Math.abs(curr.z - prev.z);
          const movement = Math.sqrt(dx*dx + dy*dy + dz*dz);
            
          if (movement > 0.01) { // Only show significant movements
            movementInfo += `Pose ${i}: movement ${movement.toFixed(4)} (dx:${dx.toFixed(3)}, dy:${dy.toFixed(3)}, dz:${dz.toFixed(3)})\n`;
          }
        }
      }
    }
      
    // Compare face landmarks if available
    if (prevLandmarks.faceLandmarks && currentLandmarks.faceLandmarks) {
      const prevFace = prevLandmarks.faceLandmarks;
      const currFace = currentLandmarks.faceLandmarks;
        
      for (let i = 0; i < Math.min(prevFace.length, currFace.length, 10); i++) { // Check first 10 for performance
        const prev = prevFace[i];
        const curr = currFace[i];
          
        if (prev && curr) {
          const dx = Math.abs(curr.x - prev.x);
          const dy = Math.abs(curr.y - prev.y);
          const dz = Math.abs(curr.z - prev.z);
          const movement = Math.sqrt(dx*dx + dy*dy + dz*dz);
            
          if (movement > 0.01) {
            movementInfo += `Face ${i}: movement ${movement.toFixed(4)} (dx:${dx.toFixed(3)}, dy:${dy.toFixed(3)}, dz:${dz.toFixed(3)})\n`;
          }
        }
      }
    }
      
    // Compare hand landmarks if available
    if (prevLandmarks.leftHandLandmarks && currentLandmarks.leftHandLandmarks) {
      const prevHand = prevLandmarks.leftHandLandmarks;
      const currHand = currentLandmarks.leftHandLandmarks;
        
      for (let i = 0; i < Math.min(prevHand.length, currHand.length); i++) {
        const prev = prevHand[i];
        const curr = currHand[i];
          
        if (prev && curr) {
          const dx = Math.abs(curr.x - prev.x);
          const dy = Math.abs(curr.y - prev.y);
          const dz = Math.abs(curr.z - prev.z);
          const movement = Math.sqrt(dx*dx + dy*dy + dz*dz);
            
          if (movement > 0.01) {
            movementInfo += `Left Hand ${i}: movement ${movement.toFixed(4)} (dx:${dx.toFixed(3)}, dy:${dy.toFixed(3)}, dz:${dz.toFixed(3)})\n`;
          }
        }
      }
    }
      
    if (prevLandmarks.rightHandLandmarks && currentLandmarks.rightHandLandmarks) {
      const prevHand = prevLandmarks.rightHandLandmarks;
      const currHand = currentLandmarks.rightHandLandmarks;
        
      for (let i = 0; i < Math.min(prevHand.length, currHand.length); i++) {
        const prev = prevHand[i];
        const curr = currHand[i];
          
        if (prev && curr) {
          const dx = Math.abs(curr.x - prev.x);
          const dy = Math.abs(curr.y - prev.y);
          const dz = Math.abs(curr.z - prev.z);
          const movement = Math.sqrt(dx*dx + dy*dy + dz*dz);
            
          if (movement > 0.01) {
            movementInfo += `Right Hand ${i}: movement ${movement.toFixed(4)} (dx:${dx.toFixed(3)}, dy:${dy.toFixed(3)}, dz:${dz.toFixed(3)})\n`;
          }
        }
      }
    }
      
    return movementInfo;
  }
    
  private getVrmBonesState(): any {
    if (!this.currentVrm || !this.currentVrm.humanoid) {
      // If no humanoid, return null or an empty object
      return {};
    }
      
    const humanoid = this.currentVrm.humanoid;
    const boneState: any = {};
      
    // Get all available bone types
    const boneTypes = Object.keys(VRMHumanBoneName);
      
    for (const boneType of boneTypes) {
      const bone = humanoid.getNormalizedBoneNode(VRMHumanBoneName[boneType as keyof typeof VRMHumanBoneName]);
      if (bone) {
        boneState[boneType] = {
          position: { x: bone.position.x, y: bone.position.y, z: bone.position.z },
          rotation: { x: bone.rotation.x, y: bone.rotation.y, z: bone.rotation.z }
        };
      }
    }
      
    return boneState;
  }
    
  private calculateVrmBoneMovement(prevBones: any, currentBones: any): string {
    if (!prevBones || !currentBones || Object.keys(prevBones).length === 0 || Object.keys(currentBones).length === 0) {
      return '';
    }
      
    let movementInfo = 'VRM Bone Movement Differences:\n';
    let hasMovement = false;
      
    for (const boneType in currentBones) {
      if (prevBones[boneType]) {
        const prev = prevBones[boneType];
        const curr = currentBones[boneType];
          
        // Calculate position difference
        const posDx = Math.abs(curr.position.x - prev.position.x);
        const posDy = Math.abs(curr.position.y - prev.position.y);
        const posDz = Math.abs(curr.position.z - prev.position.z);
        const posMovement = Math.sqrt(posDx*posDx + posDy*posDy + posDz*posDz);
          
        // Calculate rotation difference (simplified)
        const rotDx = Math.abs(curr.rotation.x - prev.rotation.x);
        const rotDy = Math.abs(curr.rotation.y - prev.rotation.y);
        const rotDz = Math.abs(curr.rotation.z - prev.rotation.z);
        const rotMovement = Math.sqrt(rotDx*rotDx + rotDy*rotDy + rotDz*rotDz);
          
        // Only report significant movements
        if (posMovement > 0.001 || rotMovement > 0.01) {
          movementInfo += `${boneType}: pos ${posMovement.toFixed(4)}, rot ${rotMovement.toFixed(4)}\n`;
          hasMovement = true;
        }
      }
    }
      
    return hasMovement ? movementInfo : '';
  }
    
  /**
   * ✅ MÉTHODE CORRIGÉE : onHolisticResults
   * - Gère les cas avec et sans VRM
   * - Utilise Kalidokit pour l'animation
   * - Logs réduits et pertinents
   */
  private onHolisticResults(results: any): void {
    console.log('onHolisticResults called');
    this.lastHolisticResults = results;

    // Dessiner les landmarks sur le canvas guide
    this.drawGuides(results);

    // Si pas de VRM, on continue quand même le traitement pour l'analyse backend
    if (!this.currentVrm) {
      console.warn('No VRM avatar loaded - processing data for backend analysis only');
      console.log('VRM Loading Status:', {
        currentVrm: !!this.currentVrm,
        vrmModel: !!this.vrmModel,
        hasScene: !!this.scene,
        hasRenderer: !!this.renderer,
        isModelLoaded: this.isModelLoaded,
      });

      // Les données sont toujours capturées pour analyse backend
      if (results.faceLandmarks?.length > 0) {
        console.log('Face landmarks captured for analysis');
      }
      if (results.poseLandmarks?.length > 0) {
        console.log('Pose landmarks captured for analysis');
      }
      if (results.leftHandLandmarks?.length > 0) {
        console.log('Left hand captured for analysis');
      }
      if (results.rightHandLandmarks?.length > 0) {
        console.log('Right hand captured for analysis');
      }

      // Envoyer les résultats au service pour analyse
      this.videoService.processHolisticResults(results);
      return; // Skip VRM animation
    }

    console.log('VRM avatar is loaded - animating');

    // ==========================================
    // ANIMATION VRM AVEC KALIDOKIT
    // ==========================================

    try {
      // --- VISAGE ---
      if (results.faceLandmarks && results.faceLandmarks.length > 0) {
        try {
          console.log('Processing face landmarks...');
          const riggedFace = Kalidokit.Face.solve(
            results.faceLandmarks,
            this.kalidokitConfig!.face
          );
          if (riggedFace) {
            this.rigFace(riggedFace);
            console.log('Face animation applied');
          }
        } catch (error) {
          console.error('Error in Kalidokit.Face.solve:', error);
        }
      }

      // --- CORPS ---
      if (
        results.poseLandmarks &&
        Array.isArray((results as any).za) &&
        (results as any).za.length > 0 &&
        results.poseLandmarks.length > 0
      ) {
        try {
          console.log('Processing pose landmarks...');
          const riggedPose = Kalidokit.Pose.solve(
            (results as any).za, // landmarks 3D
            results.poseLandmarks, // landmarks 2D
            this.kalidokitConfig!.pose
          );
          if (riggedPose) {
            this.rigPose(riggedPose);
            console.log('Pose animation applied');
          }
        } catch (error) {
          console.error('Error in Kalidokit.Pose.solve:', error);
        }
      }

      // --- MAIN GAUCHE ---
      if (results.leftHandLandmarks && results.leftHandLandmarks.length > 0) {
        try {
          console.log('Processing left hand...');
          const riggedLeft = Kalidokit.Hand.solve(
            results.leftHandLandmarks,
            'Left'
          );
          if (riggedLeft) {
            this.applyHand('Left', riggedLeft);
            console.log('Left hand animation applied');
          }
        } catch (error) {
          console.error('Error in Kalidokit.Hand.solve for left hand:', error);
        }
      }

      // --- MAIN DROITE ---
      if (results.rightHandLandmarks && results.rightHandLandmarks.length > 0) {
        try {
          console.log('Processing right hand...');
          const riggedRight = Kalidokit.Hand.solve(
            results.rightHandLandmarks,
            'Right'
          );
          if (riggedRight) {
            this.applyHand('Right', riggedRight);
            console.log('Right hand animation applied');
          }
        } catch (error) {
          console.error('Error in Kalidokit.Hand.solve for right hand:', error);
        }
      }

      // Mettre à jour le VRM
      if (this.currentVrm && typeof (this.currentVrm as any).update === 'function') {
        (this.currentVrm as any).update(0.016); // 60fps
        console.log('VRM model updated');
      }

      // Envoyer les résultats au service pour analyse
      this.videoService.processHolisticResults(results);
    
    } catch (error) {
      console.error('Error in onHolisticResults animation:', error);
    }
  }

  /**
   * ✅ MÉTHODE OPTIMISÉE : setupHolistic
   * - Logs minimalistes et pertinents
   * - Structure claire en 4 étapes
   * - Gestion d'erreur robuste
   */
  private async setupHolistic(): Promise<void> {
    try {
      console.log('Setting up Holistic MediaPipe...');

      // ÉTAPE 1 : Initialiser Holistic
      this.holistic = new Holistic({
        locateFile: (file: string) =>
          `https://cdn.jsdelivr.net/npm/@mediapipe/holistic@0.5/${file}`,
      });

      // ÉTAPE 2 : Configurer les options
      this.holistic.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: false,
        refineFaceLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      // ÉTAPE 3 : Attacher le callback
      this.holistic.onResults((results: any) => {
        if (results) {
          this.onHolisticResults(results);
        }
      });

      // ÉTAPE 4 : Setup de la caméra
      if (!this.videoElement?.nativeElement) {
        console.warn('Video element not available');
        return;
      }

      this.mpCamera = new MpCamera(this.videoElement.nativeElement, {
        onFrame: async () => {
          if (this.holistic && this.videoElement?.nativeElement) {
            try {
              await this.holistic!.send({ image: this.videoElement!.nativeElement });
            } catch (e) {
              console.error('Error sending frame to Holistic:', e);
            }
          }
        },
        width: 640,
        height: 480,
      });

      this.mpCamera.start();
      console.log('Holistic setup complete');

    } catch (error) {
      console.error('Error setting up Holistic:', error);
      throw error;
    }
  }

  private convertPoseToLandmarks(pose: any): any[] {
    if (!pose) return [];
    
    // Convert our pose data to MediaPipe landmarks format
    const landmarks: any[] = [];
    
    // Map pose keys to MediaPipe landmark indices
    const poseKeys = Object.keys(pose);
    
    for (const key of poseKeys) {
      const poseData = pose[key];
      if (poseData && poseData.position) {
        landmarks.push({
          x: poseData.position.x || 0,
          y: poseData.position.y || 0,
          z: poseData.position.z || 0,
          visibility: poseData.confidence || 0.8
        });
      }
    }
    
    return landmarks;
  }

  private calculate3DLandmarks(landmarks2D: any[]): any[] {
    // Simple conversion: use 2D landmarks as 3D with a default z value
    // In a real implementation, you would use depth estimation
    return landmarks2D.map(landmark => ({
      ...landmark,
      z: landmark.z || 0
    }));
  }

  private extractFaceLandmarks(face: any): any[] {
    // Convert our face data to MediaPipe face landmarks format
    // This is a simplified version - you may need to adjust based on your actual face data structure
    if (!face) return [];
    
    // Return a dummy array since we don't have the exact structure
    // In a real implementation, you would map the face data properly
    return [];
  }

  private drawGuides(results: any): void {
    const video = this.videoElement?.nativeElement as HTMLVideoElement;
    const canvas = this.guideCanvasRef?.nativeElement as HTMLCanvasElement;

    if (!video || !canvas) {
      return;
    }

    try {
      // Adapter le canvas à la taille de la vidéo
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const ctx = canvas.getContext('2d');
      if (!ctx) {
        return;
      }

      // Nettoyer le canvas
      ctx.save();
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      ctx.restore();

      // Commencer à dessiner les overlays
      ctx.save();

      // ==========================================
      // 1️⃣ DESSINER LE CORPS (POSE)
      // ==========================================
      if (results.poseLandmarks && results.poseLandmarks.length > 0) {
        console.log('Drawing pose landmarks:', results.poseLandmarks.length);

        // Dessiner les connexions (lignes entre les articulations)
        drawConnectors(
          ctx,
          results.poseLandmarks,
          POSE_CONNECTIONS,
          { color: '#00FF00', lineWidth: 4 } // Vert pour le squelette
        );

        // Dessiner les points (cercles aux articulations)
        drawLandmarks(
          ctx,
          results.poseLandmarks,
          { color: '#FF0000', lineWidth: 2 } // Rouge pour les points
        );
      }

      // ==========================================
      // 2️⃣ DESSINER LE VISAGE
      // ==========================================
      if (results.faceLandmarks && results.faceLandmarks.length > 0) {
        console.log('Drawing face landmarks:', results.faceLandmarks.length);

        // Dessiner le maillage du visage (tesselation)
        drawConnectors(
          ctx,
          results.faceLandmarks,
          FACEMESH_TESSELATION,
          {
            color: '#C0C0C070', // Gris semi-transparent
            lineWidth: 1
          }
        );
      }

      // ==========================================
      // 3️⃣ DESSINER LA MAIN GAUCHE
      // ==========================================
      if (results.leftHandLandmarks && results.leftHandLandmarks.length > 0) {
        console.log('Drawing left hand landmarks:', results.leftHandLandmarks.length);

        // Dessiner les connexions (lignes entre les phalanges)
        drawConnectors(
          ctx,
          results.leftHandLandmarks,
          HAND_CONNECTIONS,
          {
            color: '#CC0000', // Rouge foncé pour la main gauche
            lineWidth: 5
          }
        );

        // Dessiner les points des doigts
        drawLandmarks(
          ctx,
          results.leftHandLandmarks,
          {
            color: '#00FF00', // Vert pour les joints
            lineWidth: 2
          }
        );
      }

      // ==========================================
      // 4️⃣ DESSINER LA MAIN DROITE
      // ==========================================
      if (results.rightHandLandmarks && results.rightHandLandmarks.length > 0) {
        console.log('Drawing right hand landmarks:', results.rightHandLandmarks.length);

        // Dessiner les connexions
        drawConnectors(
          ctx,
          results.rightHandLandmarks,
          HAND_CONNECTIONS,
          {
            color: '#00CC00', // Vert pour la main droite
            lineWidth: 5
          }
        );

        // Dessiner les points
        drawLandmarks(
          ctx,
          results.rightHandLandmarks,
          {
            color: '#FF0000', // Rouge pour les joints
            lineWidth: 2
          }
        );
      }

      // Afficher les infos de débogage
      this.drawDebugInfo(ctx, results);

      ctx.restore();
    } catch (error) {
      console.warn('Error drawing guides:', error);
    }
  }

  /**
   * ✅ NOUVELLE MÉTHODE : Affiche les informations de débogage sur le canvas
   */
  private drawDebugInfo(ctx: CanvasRenderingContext2D, results: any): void {
    const padding = 15;
    const lineHeight = 22;
    let yPos = padding;

    // Style du texte
    ctx.font = '14px Arial';
    ctx.fillStyle = '#FFFFFF';
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 3;

    // Fonction pour dessiner du texte avec contour
    const drawText = (text: string) => {
      ctx.strokeText(text, padding, yPos);
      ctx.fillText(text, padding, yPos);
      yPos += lineHeight;
    };

    // Afficher les statistiques
    drawText(`Pose: ${results.poseLandmarks ? results.poseLandmarks.length : 0} points`);
    drawText(`Visage: ${results.faceLandmarks ? results.faceLandmarks.length : 0} points`);
    drawText(`Main gauche: ${results.leftHandLandmarks ? results.leftHandLandmarks.length : 0} points`);
    drawText(`Main droite: ${results.rightHandLandmarks ? results.rightHandLandmarks.length : 0} points`);
    drawText(`Temps: ${new Date().toLocaleTimeString()}`);
  }

  private landmarkToWorld(
    landmark: { x: number; y: number; z: number },
    refObj: THREE.Object3D
  ): THREE.Vector3 {
    const scale = refObj.scale.x; // Prend le scale de l'avatar/objet de référence
    return new THREE.Vector3(
      landmark.x * scale + refObj.position.x,
      landmark.y * scale + refObj.position.y,
      landmark.z * scale + refObj.position.z
    );
  }

  private animateVrm(results: any) {
    if (!this.currentVrm) return;

    // --- VISAGE ---
    if (results.faceLandmarks) {
      const riggedFace = Kalidokit.Face.solve(
        results.faceLandmarks,
        this.kalidokitConfig!.face
      );
      if (riggedFace) {
        this.rigFace(riggedFace);
      }
    }

    if (
      results.poseLandmarks &&
      Array.isArray((results as any).za) &&
      (results as any).za.length === results.poseLandmarks.length
    ) {
      const riggedPose = Kalidokit.Pose.solve(
        (results as any).za,            // les landmarks 3D
        results.poseLandmarks,          // les landmarks 2D
        this.kalidokitConfig!.pose
      );
      if (riggedPose) {
        this.rigPose(riggedPose);
      }
    }

    // --- MAINS (pas d'options de configuration) ---
    if (results.leftHandLandmarks) {
      const riggedLeft = Kalidokit.Hand.solve(
        results.leftHandLandmarks, 'Left'
      );
      if (riggedLeft) this.applyHand('Left', riggedLeft);

    }

    if (results.rightHandLandmarks) {
      const riggedRight = Kalidokit.Hand.solve(
        results.rightHandLandmarks, 'Right'
      );
      if (riggedRight) this.applyHand('Right', riggedRight);

    }
  }

  private rigFace(riggedFace: Kalidokit.TFace) {
    const vrm = this.currentVrm!;
    // 2. Animation de la tête
    this.rigRotation('Neck', riggedFace.head, 0.7);

    // 3. Clin d’œil
    const eyeBlinks = Kalidokit.Face.stabilizeBlink(
      { l: 1 - riggedFace.eye.l, r: 1 - riggedFace.eye.r },
      riggedFace.head.y
    );
    vrm.expressionManager?.setValue(VRMExpressionPresetName.Blink, eyeBlinks.l);

    // 4. Bouche (morph targets)
    // Mapping des clés source → clés de l'énumération VRMExpressionPresetName
    const shapeMap = {
      A: 'Aa',          // Viseme pour le son "A"
      I: 'Ih',          // Viseme pour le son "I"
      E: 'Ee',          // Viseme pour le son "E"
      O: 'Ou',          // Viseme pour le son "O"
      U: 'Uu',          // Viseme pour le son "U"

      SMILE: 'Smile',           // Sourire
      ANGRY: 'Angry',           // Bouche crispée (souvent associée à la colère)
      FUN: 'Fun',               // Rire ou sourire plus marqué
      SORROW: 'Sorrow',         // Tristesse (bouche tombante)
      SURPRISED: 'Surprised'    // Bouche ouverte en "O"
    } as const;


    type SourceKey = keyof typeof riggedFace.mouth.shape;         // "A"|"E"|"I"|"O"|"U"
    type PresetKey = typeof shapeMap[SourceKey];                   // "Aa"|"Ih"|"Ee"|"Ou"|"Uu"

    (Object.keys(riggedFace.mouth.shape) as SourceKey[]).forEach(sourceKey => {
      const target = riggedFace.mouth.shape[sourceKey];
      const presetKey = shapeMap[sourceKey];
      // cast presetKey en clé valide de VRMExpressionPresetName
      const preset = VRMExpressionPresetName[presetKey as keyof typeof VRMExpressionPresetName];
      const current = vrm.expressionManager?.getValue(preset) ?? 0;

      vrm.expressionManager?.setValue(
        preset,
        THREE.MathUtils.lerp(current, target, 0.5)
      );
    });

    if (vrm.expressionManager) {
      vrm.expressionManager.update();
    }

  }

  private rigPose(riggedPose: Kalidokit.TPose) {
    const vrm = this.currentVrm!;

    // Hips
    if (riggedPose.Hips.rotation) {
      this.rigRotation('Hips', riggedPose.Hips.rotation, 1, 0.3);
    }

    this.rigPosition('Hips', {
      x: riggedPose.Hips.position.x,
      y: riggedPose.Hips.position.y + 1,
      z: -riggedPose.Hips.position.z
    }, 1, 0.3);

    if (riggedPose.Spine) {
      this.rigRotation('Chest', riggedPose.Spine, 0.7, 0.3);
      this.rigRotation('Spine', riggedPose.Spine, 0.5, 0.3);
    }

    // Bras
    const arms: Array<keyof Kalidokit.TPose> = [
      'LeftUpperArm', 'LeftLowerArm', 'RightUpperArm', 'RightLowerArm'
    ];
    for (const bone of arms) {
      const vec = (riggedPose as any)[bone] as { x: number; y: number; z: number } | undefined;
      if (vec) {
        this.rigRotation(bone as any, vec, 1, 0.3);
      } else {
        console.warn(`⚠️ Aucune donnée de rotation pour ${bone}`);
      }
    }

    // Jambes avec détection d'angle à 90 degrés
    const legs: Array<keyof Kalidokit.TPose> = [
      'LeftUpperLeg', 'LeftLowerLeg', 'RightUpperLeg', 'RightLowerLeg'
    ];

    // Calculer l'angle du genou droit
    // Appliquer les rotations aux os des jambes (comportement normal)
    for (const bone of legs) {
      const vec = (riggedPose as any)[bone] as { x: number; y: number; z: number } | undefined;
      if (vec) {
        this.rigRotation(bone as any, vec, 1, 0.3);
      } else {
        console.warn(`⚠️ Aucune donnée de rotation pour ${bone}`);
      }
    }
  }

  // Dans applyHand(), assurez-vous que leftHandWorld est correctement mis à jour :
  private applyHand(
    side: 'Left' | 'Right',
    riggedHand: Record<string, any>,
  ): void {
    if (!this.currentVrm) return;

    const dampener = 1;
    const lerpAmt = 0.6;

    // ✅ CORRECTION: Calculer la position centrale de la main plus précisément
    if (side === 'Left') {
      const leftWrist = this.currentVrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.LeftHand);
      if (leftWrist) {
        leftWrist.getWorldPosition(this.leftHandWorld);
        console.log(`👋 Main gauche mise à jour: (${this.leftHandWorld.x.toFixed(2)}, ${this.leftHandWorld.y.toFixed(2)}, ${this.leftHandWorld.z.toFixed(2)})`);
      } else {
        // Fallback: utiliser une position relative au VRM
        if (this.currentVrm.scene) {
          this.leftHandWorld.copy(this.currentVrm.scene.position);
          this.leftHandWorld.x -= 0.5; // Main gauche
          this.leftHandWorld.y += 1.2; // Hauteur d'épaule
          console.log(`👋 Position de main fallback: (${this.leftHandWorld.x.toFixed(2)}, ${this.leftHandWorld.y.toFixed(2)}, ${this.leftHandWorld.z.toFixed(2)})`);
        }
      }
    }

    // Reste du code existant pour l'animation des doigts...
    for (const [mpKey, rot] of Object.entries(riggedHand)) {
      if (!rot) continue;
      const base = mpKey.slice(side.length);
      const swap = (side === 'Left' ? 'Right' : 'Left') + base;
      const key = swap as keyof typeof VRMHumanBoneName;
      const boneName = VRMHumanBoneName[key];
      const node = this.currentVrm.humanoid.getNormalizedBoneNode(boneName);
      if (!node) continue;

      const quat = new THREE.Quaternion().setFromEuler(
        new THREE.Euler(-rot.x * dampener, -rot.y * dampener, -rot.z * dampener, 'XYZ')
      );
      node.quaternion.slerp(quat, lerpAmt);
    }
  }

  private setupKalidokit(): void {
    // Configuration par défaut pour Kalidokit
    this.kalidokitConfig = {
      face: {
        runtime: 'mediapipe' as const,
        video: this.videoElement.nativeElement,
        imageSize: {
          height: 480,
          width: 640
        },
        smoothBlink: true,
        blinkSettings: [0.25, 0.75] // [seuil bas, seuil haut] pour la sensibilité du clignement
      },
      pose: {
        runtime: 'mediapipe' as const,
        video: this.videoElement.nativeElement,
        imageSize: {
          height: 480,
          width: 640
        },
        enableLegs: true // Active le calcul des jambes
      },
      stabilizeBlink: {
        noWink: false,   // Permet les clins d'œil
        maxRot: 0.5      // Rotation maximale de la tête en radians avant interpolation
      }
    };
  }

  private rigRotation(
    name: keyof typeof VRMHumanBoneName,
    rotation: { x: number; y: number; z: number },
    dampener = 1,
    lerpAmt = 0.3
  ) {
    if (!this.currentVrm) return;

    // Récupérer la node normalisée, qui absorbe les différences d'axes
    const node = this.currentVrm.humanoid.getNormalizedBoneNode(
      VRMHumanBoneName[name]
    );
    if (!node) return;

    const euler = new THREE.Euler(
      rotation.x * dampener,
      rotation.y * dampener,
      rotation.z * dampener,
      'XYZ'
    );
    const quat = new THREE.Quaternion().setFromEuler(euler);
    node.quaternion.slerp(quat, lerpAmt);
  }

  private rigPosition(
    name: keyof typeof VRMHumanBoneName,
    position: { x: number; y: number; z: number },
    dampener = 1,
    lerpAmt = 0.3
  ) {
    if (!this.currentVrm) return;

    // Récupération du nœud osseux via le nouvel enum VRMHumanBoneName
    const node = this.currentVrm.humanoid.getNormalizedBoneNode(
      VRMHumanBoneName[name]
    );
    if (!node) return;

    // Calcul du vecteur position avec atténuation
    const vec = new THREE.Vector3(
      position.x * dampener,
      position.y * dampener,
      position.z * dampener
    );

    // Interpolation linéaire de la position
    node.position.lerp(vec, lerpAmt);
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
        
        // Initialize and setup the new holistic system for VRM animation
        this.setupKalidokit();
        await this.setupHolistic();
        
        // Ensure the holistic camera is properly initialized
        if (this.mpCamera) {
          console.log('Holistic camera already initialized');
        } else {
          console.warn('Holistic camera not initialized, initializing now...');
          if (this.holistic && this.videoElement && this.videoElement.nativeElement) {
            this.mpCamera = new MpCamera(this.videoElement.nativeElement, {
              onFrame: async () => {
                if (this.holistic && this.videoElement?.nativeElement) {
                  try {
                    await this.holistic.send({ image: this.videoElement.nativeElement });
                  } catch (e) {
                    console.error('Erreur dans onFrame:', e);
                  }
                }
              },
              width: 640,
              height: 480,
            });
            
            try {
              this.mpCamera.start();
              console.log('Holistic camera started successfully');
            } catch (error) {
              console.error('Error starting holistic camera:', error);
            }
          }
        }

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
    
    // Stop the new holistic system
    if (this.mpCamera) {
      this.mpCamera.stop();
      this.mpCamera = null;
    }
    
    if (this.holistic) {
      this.holistic.close();
      this.holistic = null;
    }
    
    // Unsubscribe from body analysis subscription
    if (this.bodyAnalysisSubscription) {
      this.bodyAnalysisSubscription.unsubscribe();
      this.bodyAnalysisSubscription = null;
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
        this.sendMovementData().catch(error => {
          console.error('Error in periodic sendMovementData:', error);
        });
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
  private async sendMovementData(): Promise<void> {
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Movement data sending skipped - not in browser environment');
      return;
    }
      
    // Ensure user is loaded before sending data
    if (!this.userId) {
      console.log('User ID not available, attempting to load user...');
      await this.loadCurrentUser();
        
      // Check again after loading user
      if (!this.userId) {
        console.error('❌ User ID still not available, skipping data send');
        this.showNotification('❌ User ID not available, please log in', 'error');
        return;
      }
    }
      
    // Debug logging to understand what's happening
    console.log('🔍 sendMovementData called - images:', this.capturedImagesForSend.length, 'userId:', this.userId);
      
    // Vérifier que nous avons des images et des données
    if (this.capturedImagesForSend.length === 0) {
      console.log('⚠️ Skipping data send - no images to send');
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
        // Show success message
        this.showNotification('📸 Une image a été prise et envoyée au backend - SUCCESS', 'success');
        // Clear the captured images after successful sending
        this.capturedImagesForSend = [];
      },
      error: (error) => {
        console.error('❌ Erreur lors de l\'envoi des images:', error);
        // Show failure message
        this.showNotification('📸 Une image a été prise mais échec de l\'envoi au backend - FAILED', 'error');
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
      
    // Start capturing images every 5 seconds (constant interval for both webcam and video files)
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
          this.captureImageFromVideo(video);
        } else {
          console.log('Video not ready for capture, readyState:', video.readyState, 'width:', video.videoWidth);
        }
      }
    }, 5000); // Capture every 5 seconds for consistent timing
  }
    
  private captureImageFromVideo(video: HTMLVideoElement): void {
    const canvas = document.createElement('canvas');
    canvas.width = Math.min(video.videoWidth, 320); // Reduce size to optimize
    canvas.height = Math.min(video.videoHeight, 240);
      
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
      // Convert to data URL with JPEG format for smaller size
      const imageData = canvas.toDataURL('image/jpeg', 0.7); // JPEG with 70% quality
        
      console.log('📸 Image captured from video - length:', imageData.length);
        
      // Show notification about image capture
      this.showNotification('📸 Une image a été prise', 'info');
        
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
        
      // For video files, the captured images are added to capturedImagesForSend array
      // which should be sent by the periodic sendMovementData call
      // However, we'll ensure that sending is triggered after capturing
      console.log('📊 Video frame added, total for sending:', this.capturedImagesForSend.length);
      
      // Check if we should trigger sending immediately for video captures
      if (this.userId && this.capturedImagesForSend.length > 0) {
        // Try to trigger the sending mechanism
        console.log('Attempting to trigger send for video frame...');
        
        // Since we know frames are being captured but not sent, 
        // let's call sendMovementData directly after a short delay
        setTimeout(async () => {
          if (this.capturedImagesForSend.length > 0) {
            console.log('Directly triggering sendMovementData for video frames');
            await this.sendMovementData();
          }
        }, 100); // Small delay to ensure everything is set up
      } else {
        console.log('⚠️ Cannot trigger send - userId:', this.userId, 'capturedImages:', this.capturedImagesForSend.length);
      }
    }
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
    
    if (this.videoFrameCaptureInterval) {
      clearInterval(this.videoFrameCaptureInterval);
      this.videoFrameCaptureInterval = null;
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
            
            // Initialize and setup the new holistic system for VRM animation
            this.setupKalidokit();
            await this.setupHolistic();
            
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
        
        // Set up regular frame capture and holistic processing during video playback
        let lastCaptureTime = -1; // Track last capture time
        
        // Ensure holistic is properly set up for video processing
        if (!this.holistic) {
          console.log('Holistic not initialized, setting up now for video...');
          await this.setupHolistic();
        } else {
          console.log('Holistic already initialized, using existing instance');
        }
        
        let lastHolisticTime = 0; // Track last holistic processing time
        
        this.videoElement.nativeElement.ontimeupdate = () => {
          const currentTime = Math.floor(this.videoElement.nativeElement.currentTime);
          
          // Capture frame every 5 seconds based on video time
          // Only capture if we're at a 5-second interval and haven't captured this second yet
          if (currentTime % 5 === 0 && currentTime !== lastCaptureTime && currentTime > 0) {
            lastCaptureTime = currentTime;
            this.captureImageFromVideo(this.videoElement.nativeElement);
          }
          
          // Process holistic tracking for avatar animation (throttled to avoid performance issues)
          const now = Date.now();
          if (this.holistic && this.videoElement && this.videoElement.nativeElement && (now - lastHolisticTime) > 66) { // Process ~15fps (every 66ms) for smoother animation
            lastHolisticTime = now;
            
            // Run holistic detection on the current video frame
            if (this.holistic && this.videoElement?.nativeElement) {
              this.holistic.send({ image: this.videoElement.nativeElement }).catch((err: any) => {
                console.warn('Holistic processing error:', err);
              });
            }
          }
        };
        
        // Handle video end to stop analysis
        this.videoElement.nativeElement.onended = () => {
          this.stopVideoAnalysisLoop();
          this.stopImageCapture();
          this.stopDataSending();
          this.isTracking = false;
          
          // Clear the video frame capture interval if it exists
          if (this.videoFrameCaptureInterval) {
            clearInterval(this.videoFrameCaptureInterval);
            this.videoFrameCaptureInterval = null;
          }
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

    // Create renderer with transparent background
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.setClearColor(0x000000, 0); // Transparent background
    
    // Add renderer to container
    const container = this.threeDContainer.nativeElement;
    container.appendChild(this.renderer.domElement);
    
    // Set initial size based on container
    this.updateRendererSize();
    
    // Create camera with proper aspect ratio
    this.camera = new THREE.PerspectiveCamera(75, this.renderer.domElement.clientWidth / this.renderer.domElement.clientHeight, 0.1, 1000);
    this.camera.position.set(0, 0, 5); // Position camera in front of the VRM model

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
      
      // First try to get VRM from the VRM component in the scene
      // Look for VRM objects in the scene hierarchy
      for (const child of gltf.scene.children) {
        if ((child as any).constructor.name === 'VRM' || (child as any).hasOwnProperty('humanoid')) {
          vrm = child as any;
          break;
        }
      }
      
      // If not found in scene children, try to get from userData
      if (!vrm && gltf.userData && gltf.userData['vrm']) {
        vrm = gltf.userData['vrm'];
      }
      
      // If not found in userData, try to get from gltfExtensions (where VRM data is typically stored)
      if (!vrm) {
        const gltfAny = gltf as any;
        if (gltfAny.gltfExtensions && gltfAny.gltfExtensions['VRM']) {
          vrm = gltfAny.gltfExtensions['VRM'];
        }
      }
      
      // If still not found, try to access from scene children via userData
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
        } else {
          console.log('VRM has humanoid rigging - ready for pose animation');
        }
                
        // Set up the VRM model
        vrm.scene.rotation.y = Math.PI; // Rotate 180 degrees to face the camera
        this.scene.add(vrm.scene);
                
        this.vrm = vrm;
        this.currentVrm = vrm; // Set currentVrm for holistic processing
        this.vrmModel = vrm.scene;
        this.isModelLoaded = true;
                
        console.log('VRM model loaded successfully');
                
        // Log the humanoid bones that are available
        if (vrm.humanoid) {
          console.log('Available humanoid bones:', Object.keys(vrm.humanoid.humanBones || {}));
                  
          // Verify that essential bones for animation are present
          const essentialBones = ['hips', 'spine', 'chest', 'head', 'leftUpperArm', 'rightUpperArm', 'leftLowerArm', 'rightLowerArm'];
          const availableBones = Object.keys(vrm.humanoid.humanBones || {});
          const missingEssentialBones = essentialBones.filter(bone => !availableBones.includes(bone));
                  
          if (missingEssentialBones.length > 0) {
            console.warn('Missing essential bones for full animation:', missingEssentialBones);
          } else {
            console.log('All essential bones for animation are available');
          }
        }
                
        // Display avatar bones info when VRM is successfully loaded
        setTimeout(() => {
          this.displayAvatarBones();
        }, 1000); // Delay to ensure model is fully loaded
                
        // Ensure the VRM is properly initialized for animation
        if (this.currentVrm && typeof this.currentVrm.update === 'function') {
          // Trigger an initial update to ensure the model is ready
          this.currentVrm.update(0);
        }
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
        this.currentVrm = null; // Also set currentVrm to null
                
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
    if (this.vrm) {
      this.vrm.update(Math.min(deltaTime, 0.016)); // Cap at 60fps
      
      // Use holistic results if available, otherwise fall back to body analysis pose
      if (this.lastHolisticResults) {
        this.updateVRMBones(null); // Pass null since we'll use holistic results inside
      } else if (this.bodyAnalysis?.pose) {
        this.updateVRMBones(this.bodyAnalysis.pose);
      }
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
    if (typeof window === 'undefined' || !this.vrm) {
      return;
    }
    
    // Set the current VRM for use in the new methods
    this.currentVrm = this.vrm;
    
    // Check if we have holistic results to animate with
    if (this.lastHolisticResults) {
      this.animateVrm(this.lastHolisticResults);
    } else if (pose) {
      // Fallback to the existing logic if no holistic results but pose is provided
      if (!this.vrm?.humanoid) {
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
    
    // Make sure to update the VRM if it exists
    if (this.currentVrm) {
      // Only update if it has the update method (VRM models have it, GLTF models don't)
      if (typeof this.currentVrm.update === 'function') {
        this.currentVrm.update(0.016); // Update with fixed delta time
      }
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
        
    this.updateRendererSize();
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
        
      // The body analysis subscription should automatically trigger holistic processing
      // but we'll also capture frame for sending
      this.captureVideoFrameImage(video);
        
      // Send data immediately for video processing
      if (this.userId && this.capturedImagesForSend.length > 0) {
        this.sendMovementData().catch(error => {
          console.error('Error sending video frame data:', error);
        });
      }
    } catch (error) {
      console.error('Erreur lors de l\'analyse de la frame vidéo:', error);
    }
  }
  
  private captureVideoFrameImage(video: HTMLVideoElement): void {
    console.log('📷 Starting captureVideoFrameImage...');
    // Check if we're in browser environment
    if (typeof window === 'undefined') {
      console.warn('Frame capture skipped - not in browser environment');
      return;
    }
    
    console.log('✅ Browser environment confirmed');
    
    // Ensure video is ready and has valid dimensions
    if (video.readyState !== video.HAVE_ENOUGH_DATA || 
        video.videoWidth === 0 || 
        video.videoHeight === 0) {
      console.warn('⚠️ Video not ready or invalid dimensions');
      console.log('Video readyState:', video.readyState);
      console.log('Video width:', video.videoWidth);
      console.log('Video height:', video.videoHeight);
      return;
    }
    
    console.log('✅ Video is ready for capture');
    
    const canvas = document.createElement('canvas');
    canvas.width = Math.min(video.videoWidth, 320); // Reduce size to optimize
    canvas.height = Math.min(video.videoHeight, 240);
    
    const ctx = canvas.getContext('2d');
    if (ctx) {
      console.log('🎨 Drawing video frame to canvas...');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert to data URL with JPEG format for smaller size
      const imageData = canvas.toDataURL('image/jpeg', 0.7); // JPEG with 70% quality
      
      console.log('📸 Frame captured - image length:', imageData.length);
      
      // Show notification about frame capture
      this.showNotification('📸 Une image a été prise', 'info');
      
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
      
      // Immediately trigger sending if we have user ID
      if (this.userId) {
        console.log('🔄 User ID available, preparing to send image...');
        this.sendMovementData().catch(error => {
          console.error('❌ Error sending captured image:', error);
        });
      } else {
        console.warn('⚠️ No user ID available, image will be sent when user is loaded');
        // Try to load user and then send
        this.loadCurrentUser();
        if (this.userId) {
          console.log('🔄 User loaded, preparing to send image...');
          this.sendMovementData().catch(error => {
            console.error('❌ Error sending captured image after user load:', error);
          });
        }
      }
    } else {
      console.error('❌ Could not get canvas context');
    }
  }
}
