import {
  Component,
  OnInit,
  OnDestroy,
  ViewChild,
  ElementRef,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  HostListener,
  Inject
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { VideoService } from '../video.service';
import { BodyAnalysis } from '../video.service';
import { DataService } from '../services/data.service';
import { DataRecord } from '../models/data.model';
import { AuthService, User } from '../auth.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-video',
  standalone: true,
  imports: [CommonModule, HttpClientModule, RouterModule],
  templateUrl: './video.component.html',
  styleUrl: './video.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class VideoComponent implements OnInit, OnDestroy {
  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;

  bodyAnalysis: BodyAnalysis | null = null;
  isVideoInitialized = false;
  errorMessage: string | null = null;
  fps = 0;

  isTracking = false;
  private frameCount = 0;
  private lastTime = performance.now();
  private destroy$ = new Subject<void>();
  private animationFrameId: number | null = null;
  private stream: MediaStream | null = null;

  private lastAnalysisTime = 0;
  private analysisInterval = 100;

  // Data capture properties
  private userId = 1; // Default user ID, should be set dynamically
  private lastCaptureTime = 0;
  private captureInterval = 5000; // Capture every 5 seconds when movement is detected
  private movementThreshold = 0.1; // Minimum pose confidence to consider as movement
  private isRecording = false;
  private recordingStartTime = 0;
  private recordingDuration = 30000; // 30 seconds
  private mediaRecorder: MediaRecorder | null = null;
  private recordedChunks: Blob[] = [];

  // Captured data storage
  private capturedVideos: { blob: Blob, metadata: any }[] = [];
  private capturedMovements: any[] = [];

  constructor(
    @Inject(VideoService) private videoService: VideoService,
    private dataService: DataService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  async ngOnInit(): Promise<void> {
    console.log('🎬 VideoComponent initialized');
    
    // Get current user ID
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.userId = currentUser.id;
      console.log('👤 Current user ID:', this.userId);
    } else {
      console.log('👤 No current user, using default ID');
    }
    
    // Subscribe to user changes
    this.authService.currentUser.subscribe((user: User | null) => {
      if (user) {
        this.userId = user.id;
        console.log('👤 User logged in, updated user ID:', this.userId);
        // Reload data records for the new user
        this.loadDataRecords();
      }
    });
    
    console.log('✅ Service vidéo initialisé');
    this.subscribeToAnalysis();
  }

  private subscribeToAnalysis(): void {
    this.videoService.bodyAnalysis$
      .pipe(takeUntil(this.destroy$))
      .subscribe((analysis: BodyAnalysis) => {
        console.log('📊 Receiving analysis data:', analysis);
        this.bodyAnalysis = analysis;
        console.log('📊 Données analysées:', analysis);
        
        // Check for movement when new analysis data arrives
        if (this.isTracking) {
          this.checkForMovement();
        } else {
          console.log('⏸️ Not checking for movement - tracking is paused');
        }
        
        this.cdr.markForCheck();
      });
  }

  async startCamera(): Promise<void> {
    console.log('🎬 Starting camera...');
    
    // Check if we're in a browser environment
    if (typeof window === 'undefined' || !navigator.mediaDevices) {
      console.log('❌ Camera not available in server environment');
      this.errorMessage = '❌ Caméra non disponible dans cet environnement';
      this.cdr.markForCheck();
      return;
    }
    
    try {
      this.errorMessage = null;

      const constraints: MediaStreamConstraints = {
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.videoElement.nativeElement.srcObject = this.stream;

      await new Promise<void>((resolve) => {
        this.videoElement.nativeElement.onloadedmetadata = () => {
          console.log('🎬 Video metadata loaded');
          this.videoElement.nativeElement.play();
          console.log('🎬 Video play initiated');
          console.log('🎬 Video dimensions:', this.videoElement.nativeElement.videoWidth, 'x', this.videoElement.nativeElement.videoHeight);
          this.isVideoInitialized = true;
          this.isTracking = true;
          this.cdr.markForCheck();
          console.log('✅ Caméra démarrée');
          // Start holistic tracking
          console.log('🎬 Calling setupHolistic...');
          this.videoService.setupHolistic(this.videoElement.nativeElement);
          resolve();
        };
      });
    } catch (error) {
      this.errorMessage = '❌ Erreur d\'accès à la caméra. Vérifiez les permissions.';
      console.error('Erreur caméra:', error);
      this.cdr.markForCheck();
    }
  }

  stopCamera(): void {
    this.isTracking = false;

    // Send captured data to Spring Boot before stopping
    this.sendCapturedDataToSpringBoot();

    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }

    // Dispose of MediaPipe resources
    this.videoService.dispose();

    this.isVideoInitialized = false;
    this.cdr.markForCheck();
    console.log('⏹️ Caméra arrêtée');
  }

  private startAnalysisLoop(): void {
    console.log('🎬 Starting analysis loop');
    const analyze = async () => {
      console.log('🎬 Analysis loop iteration');
      if (!this.isTracking || !this.videoElement?.nativeElement) {
        console.log('🎬 Analysis loop stopped - tracking:', this.isTracking, 'video element:', !!this.videoElement?.nativeElement);
        return;
      }

      this.updateFPS();

      this.animationFrameId = requestAnimationFrame(analyze);
    };

    analyze();
  }

  private updateFPS(): void {
    this.frameCount++;
    const now = performance.now();
    const elapsed = now - this.lastTime;

    if (elapsed >= 1000) {
      this.fps = Math.round(this.frameCount * 1000 / elapsed);
      this.frameCount = 0;
      this.lastTime = now;
      this.cdr.markForCheck();
    }
  }

  getPoseStatus(): string {
    const conf = this.bodyAnalysis?.poseConfidence || 0;

    if (conf === 0) {
      return '❌ Pas de pose détectée';
    } else if (conf < 30) {
      return '⚠️ Pose peu claire (' + conf + '%)';
    } else if (conf < 70) {
      return '🟡 Pose détectée (' + conf + '%)';
    } else {
      return '✅ Pose claire (' + conf + '%)';
    }
  }

  getPoseConfidence(): number {
    return this.bodyAnalysis?.poseConfidence || 0;
  }

  getFaceStatus(): string {
    const conf = this.bodyAnalysis?.faceConfidence || 0;

    if (conf === 0) {
      return '❌ Pas de visage détecté';
    } else if (conf < 30) {
      return '⚠️ Visage peu clair (' + conf + '%)';
    } else if (conf < 70) {
      return '🟡 Visage détecté (' + conf + '%)';
    } else {
      return '✅ Visage clair (' + conf + '%)';
    }
  }

  getFaceConfidence(): number {
    return this.bodyAnalysis?.faceConfidence || 0;
  }

  getHandsStatus(): string {
    const { left, right } = this.bodyAnalysis?.handsDetected || { left: false, right: false };

    if (!left && !right) {
      return '❌ Pas détectées';
    } else if (left && right) {
      return '✅ Détectées (2)';
    } else if (left) {
      return '✅ Gauche | ❌ Droite';
    } else {
      return '❌ Gauche | ✅ Droite';
    }
  }

  getHandsGestures(): string {
    const { left, right } = this.bodyAnalysis?.hands || { left: null, right: null };

    let leftGesture = left?.gesture || 'Aucun';
    let rightGesture = right?.gesture || 'Aucun';

    return `${leftGesture} | ${rightGesture}`;
  }

  getPoseDetails(): string {
    const metrics = this.bodyAnalysis?.bodyMetrics;
    if (!metrics) return 'N/A';

    const pose = this.bodyAnalysis?.pose;
    if (!pose) return 'N/A';

    const head = pose['Head'];
    const leftArm = pose['LeftElbow'];
    const rightArm = pose['RightElbow'];

    let details = metrics.posture;

    if (head?.position) {
      details += ` | Tête: (${head.position.x?.toFixed(2)}, ${head.position.y?.toFixed(2)})`;
    }

    return details;
  }

  getFaceExpression(): string {
    return this.bodyAnalysis?.bodyMetrics?.faceExpression || 'Neutre';
  }

  getSystemStatus(): {
    camera: string;
    analysis: string;
    posture: string;
    fps: string;
  } {
    return {
      camera: this.isVideoInitialized ? '🟢 Actif' : '🔴 Inactif',
      analysis: this.bodyAnalysis?.isAnalyzing ? '⏳ En cours' : '✅ Prêt',
      posture: this.bodyAnalysis?.poseConfidence || 0 > 50 ? '✅ Détectée' : '⏳ En attente',
      fps: this.fps + ' FPS'
    };
  }

  @HostListener('window:beforeunload')
  ngOnDestroy(): void {
    this.stopCamera();
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadDataRecords(): void {
    // Load data records for the current user
    this.dataService.getDataRecordsByUserId(this.userId).subscribe({
      next: (records) => {
        console.log('📋 Loaded data records from backend:', records);
      },
      error: (error) => {
        console.error('❌ Error loading data records:', error);
      }
    });
  }

  private captureImage(): void {
    console.log('📸 Attempting to capture image...');
    console.log('📸 Current body analysis:', this.bodyAnalysis);
    console.log('📸 Current user ID:', this.userId);
    
    if (!this.videoElement || !this.videoElement.nativeElement) {
      console.warn('❌ Video element not available for capture');
      return;
    }

    try {
      const video = this.videoElement.nativeElement;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        
        console.log('🖼️ Image captured successfully');
        
        // Create detailed JSON data with comprehensive movement information
        const jsonData: any = {
          type: 'movement_capture',
          poseConfidence: this.bodyAnalysis?.poseConfidence || 0,
          faceConfidence: this.bodyAnalysis?.faceConfidence || 0,
          handsDetected: this.bodyAnalysis?.handsDetected || { left: false, right: false },
          bodyMetrics: this.bodyAnalysis?.bodyMetrics || {},
          timestamp: new Date().toISOString(),
          userId: this.userId,
          movementType: 'detected'
        };
        
        // Add pose data if available
        if (this.bodyAnalysis?.pose) {
          jsonData.poseData = {
            head: this.bodyAnalysis.pose['Head'] ? {
              position: this.bodyAnalysis.pose['Head'].position,
              confidence: this.bodyAnalysis.pose['Head'].confidence
            } : null,
            shoulders: {
              left: this.bodyAnalysis.pose['LeftShoulder'] ? {
                position: this.bodyAnalysis.pose['LeftShoulder'].position,
                confidence: this.bodyAnalysis.pose['LeftShoulder'].confidence
              } : null,
              right: this.bodyAnalysis.pose['RightShoulder'] ? {
                position: this.bodyAnalysis.pose['RightShoulder'].position,
                confidence: this.bodyAnalysis.pose['RightShoulder'].confidence
              } : null
            },
            hips: {
              left: this.bodyAnalysis.pose['LeftHip'] ? {
                position: this.bodyAnalysis.pose['LeftHip'].position,
                confidence: this.bodyAnalysis.pose['LeftHip'].confidence
              } : null,
              right: this.bodyAnalysis.pose['RightHip'] ? {
                position: this.bodyAnalysis.pose['RightHip'].position,
                confidence: this.bodyAnalysis.pose['RightHip'].confidence
              } : null
            }
          };
        }
        
        // Add face data if available
        if (this.bodyAnalysis?.face) {
          jsonData.faceData = {
            eyeOpenness: {
              left: this.bodyAnalysis.face.eye_blink_left,
              right: this.bodyAnalysis.face.eye_blink_right
            },
            mouthOpenness: this.bodyAnalysis.face.mouth_open,
            headPosition: this.bodyAnalysis.face.Head ? {
              position: this.bodyAnalysis.face.Head.position
            } : null
          };
        }
        
        // Add hand data if available
        if (this.bodyAnalysis?.hands) {
          jsonData.handsData = {
            left: this.bodyAnalysis.hands.left ? {
              landmarks: this.bodyAnalysis.hands.left.landmarks,
              gesture: this.bodyAnalysis.hands.left.gesture,
              handedness: this.bodyAnalysis.hands.left.handedness
            } : null,
            right: this.bodyAnalysis.hands.right ? {
              landmarks: this.bodyAnalysis.hands.right.landmarks,
              gesture: this.bodyAnalysis.hands.right.gesture,
              handedness: this.bodyAnalysis.hands.right.handedness
            } : null
          };
        }
        
        // Create data record
        const dataRecord: DataRecord = {
          userId: this.userId,
          imageData: imageData,
          timestamp: new Date(),
          movementDetected: true,
          jsonData: jsonData
        };
        
        // Store captured movement data for later sending to Spring Boot
        this.capturedMovements.push(jsonData);
        
        console.log('💾 Saving data record:', dataRecord);
        
        // Save the data record
        this.dataService.saveDataRecord(dataRecord).subscribe({
          next: (record) => {
            console.log('📸 Image captured and saved:', record.id);
          },
          error: (err) => {
            console.error('❌ Error saving image data to backend:', err);
            // Fallback to local storage if backend is not available
            this.dataService.saveDataRecordLocal(dataRecord).subscribe({
              next: (localRecord) => {
                console.log('📸 Image captured and saved locally:', localRecord.id);
              },
              error: (localErr) => {
                console.error('❌ Error saving image data locally:', localErr);
              }
            });
          }
        });
      }
    } catch (error) {
      console.error('❌ Error capturing image:', error);
    }
  }

  private checkForMovement(): void {
    const currentTime = Date.now();
    
    console.log('🔍 Checking for movement - Current analysis:', this.bodyAnalysis);
    console.log('🔍 Current user ID:', this.userId);
    console.log('🔍 Is tracking:', this.isTracking);
    console.log('🔍 Last capture time:', this.lastCaptureTime);
    console.log('🔍 Current time:', currentTime);
    console.log('🔍 Time since last capture:', currentTime - this.lastCaptureTime);
    console.log('🔍 Capture interval:', this.captureInterval);
    
    // Check if enough time has passed since last capture
    if (currentTime - this.lastCaptureTime < this.captureInterval) {
      console.log('⏰ Too soon since last capture, skipping...');
      return;
    }
    
    console.log('🔍 Pose confidence:', this.bodyAnalysis?.poseConfidence);
    console.log('🔍 Movement threshold:', this.movementThreshold);
    
    // Check if there's significant movement (pose confidence above threshold)
    if (this.bodyAnalysis && 
        this.bodyAnalysis.poseConfidence !== undefined && 
        this.bodyAnalysis.poseConfidence > this.movementThreshold) {
      
      console.log('🏃 Movement detected with confidence:', this.bodyAnalysis.poseConfidence);
      this.captureImage();
      this.lastCaptureTime = currentTime;
      
      // Start recording if not already recording
      if (!this.isRecording) {
        this.startRecording();
      }
    } else if (this.isRecording && (currentTime - this.recordingStartTime > this.recordingDuration)) {
      // Stop recording after 30 seconds
      console.log('⏹️ Stopping recording after 30 seconds');
      this.stopRecording();
    } else {
      console.log('🚶 No significant movement detected. Confidence:', this.bodyAnalysis?.poseConfidence, 'Threshold:', this.movementThreshold);
    }
  }

  private startRecording(): void {
    console.log('⏺️ Starting 30-second recording...');
    this.isRecording = true;
    this.recordingStartTime = Date.now();
    
    // Start actual video recording using MediaRecorder
    if (this.stream && typeof window !== 'undefined' && window.MediaRecorder) {
      try {
        this.recordedChunks = [];
        this.mediaRecorder = new MediaRecorder(this.stream, { mimeType: 'video/webm' });
        
        this.mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.recordedChunks.push(event.data);
          }
        };
        
        this.mediaRecorder.onstop = () => {
          console.log('⏺️ Recording stopped, saving video data...');
          this.saveRecordedVideo();
        };
        
        this.mediaRecorder.start();
        console.log('⏺️ MediaRecorder started');
      } catch (error) {
        console.error('❌ Error starting MediaRecorder:', error);
      }
    } else {
      console.log('⏭️ MediaRecorder not available, using placeholder');
    }
  }

  private stopRecording(): void {
    console.log('⏹️ Stopping recording after 30 seconds');
    this.isRecording = false;
    
    // Stop actual video recording
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
      console.log('⏹️ MediaRecorder stopped');
    } else {
      // If MediaRecorder is not available, save placeholder data
      this.savePlaceholderVideoData();
    }
  }

  private savePlaceholderVideoData(): void {
    // Create a data record for the video segment
    const videoRecord: DataRecord = {
      userId: this.userId,
      videoUrl: `video_segment_${Date.now()}.mp4`, // Placeholder URL
      timestamp: new Date(),
      movementDetected: true,
      jsonData: {
        type: 'video_segment',
        duration: 30,
        startTime: this.recordingStartTime,
        endTime: Date.now(),
        poseConfidence: this.bodyAnalysis?.poseConfidence || 0
      }
    };
    
    // Save the video record
    this.dataService.saveDataRecord(videoRecord).subscribe({
      next: (record) => {
        console.log('📹 Video segment saved:', record.id);
      },
      error: (err) => {
        console.error('❌ Error saving video data to backend:', err);
        // Fallback to local storage if backend is not available
        this.dataService.saveDataRecordLocal(videoRecord).subscribe({
          next: (localRecord) => {
            console.log('📹 Video segment saved locally:', localRecord.id);
          },
          error: (localErr) => {
            console.error('❌ Error saving video data locally:', localErr);
          }
        });
      }
    });
  }

  private saveRecordedVideo(): void {
    if (this.recordedChunks.length === 0) {
      console.log('⏭️ No video data to save');
      return;
    }

    // Create a blob from the recorded chunks
    const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
    
    // Store video metadata for later sending to Spring Boot
    const videoMetadata = {
      type: 'video_segment',
      duration: Date.now() - this.recordingStartTime,
      startTime: this.recordingStartTime,
      endTime: Date.now(),
      poseConfidence: this.bodyAnalysis?.poseConfidence || 0,
      fileSize: blob.size
    };
    
    this.capturedVideos.push({ blob, metadata: videoMetadata });
    
    // Create a data record for the video segment
    const videoRecord: DataRecord = {
      userId: this.userId,
      videoUrl: `video_segment_${Date.now()}.webm`, // Actual video URL
      timestamp: new Date(),
      movementDetected: true,
      jsonData: videoMetadata
    };
    
    // Save the video record
    this.dataService.saveDataRecord(videoRecord).subscribe({
      next: (record) => {
        console.log('📹 Video segment saved:', record.id);
      },
      error: (err) => {
        console.error('❌ Error saving video data to backend:', err);
        // Fallback to local storage if backend is not available
        this.dataService.saveDataRecordLocal(videoRecord).subscribe({
          next: (localRecord) => {
            console.log('📹 Video segment saved locally:', localRecord.id);
          },
          error: (localErr) => {
            console.error('❌ Error saving video data locally:', localErr);
          }
        });
      }
    });
  }

  // Method to manually trigger data capture for testing
  triggerCapture(): void {
    console.log('🧪 Manual capture triggered');
    this.captureImage();
  }

  /**
   * Send captured video and movement data to Spring Boot backend
   */
  private sendCapturedDataToSpringBoot(): void {
    console.log('📤 Sending captured data to Spring Boot...');
    
    // Send captured movement data
    if (this.capturedMovements.length > 0) {
      console.log(`📤 Sending ${this.capturedMovements.length} movement records to Spring Boot`);
      
      this.capturedMovements.forEach((movementData, index) => {
        const dataRecord = {
          userId: this.userId,
          timestamp: new Date(),
          movementDetected: true,
          jsonData: movementData
        };
        
        this.dataService.saveDataRecord(dataRecord).subscribe({
          next: (record) => {
            console.log(`✅ Movement record ${index + 1}/${this.capturedMovements.length} sent to Spring Boot:`, record.id);
          },
          error: (err) => {
            console.error(`❌ Error sending movement record ${index + 1} to Spring Boot:`, err);
            // Fallback to local storage
            this.dataService.saveDataRecordLocal(dataRecord).subscribe({
              next: (localRecord) => {
                console.log(`💾 Movement record ${index + 1} saved locally:`, localRecord.id);
              },
              error: (localErr) => {
                console.error(`❌ Error saving movement record ${index + 1} locally:`, localErr);
              }
            });
          }
        });
      });
      
      // Clear the captured movements array
      this.capturedMovements = [];
    } else {
      console.log('📭 No movement data to send to Spring Boot');
    }
    
    // Send captured videos
    if (this.capturedVideos.length > 0) {
      console.log(`📤 Sending ${this.capturedVideos.length} video segments to Spring Boot`);
      
      this.capturedVideos.forEach((videoData, index) => {
        // For now, we'll send metadata about the video
        // In a real implementation, you might upload the actual video file
        const videoRecord = {
          userId: this.userId,
          timestamp: new Date(),
          movementDetected: true,
          videoUrl: `video_segment_${Date.now()}_${index}.webm`,
          jsonData: {
            type: 'video_segment',
            metadata: videoData.metadata,
            fileSize: videoData.blob.size,
            mimeType: videoData.blob.type
          }
        };
        
        this.dataService.saveDataRecord(videoRecord).subscribe({
          next: (record) => {
            console.log(`✅ Video record ${index + 1}/${this.capturedVideos.length} sent to Spring Boot:`, record.id);
          },
          error: (err) => {
            console.error(`❌ Error sending video record ${index + 1} to Spring Boot:`, err);
            // Fallback to local storage
            this.dataService.saveDataRecordLocal(videoRecord).subscribe({
              next: (localRecord) => {
                console.log(`💾 Video record ${index + 1} saved locally:`, localRecord.id);
              },
              error: (localErr) => {
                console.error(`❌ Error saving video record ${index + 1} locally:`, localErr);
              }
            });
          }
        });
      });
      
      // Clear the captured videos array
      this.capturedVideos = [];
    } else {
      console.log('📭 No video data to send to Spring Boot');
    }
    
    console.log('📤 All captured data sent to Spring Boot');
  }
}