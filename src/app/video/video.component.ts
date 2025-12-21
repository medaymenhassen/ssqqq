import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideoService, BodyAnalysis } from '../video.service';
import { AuthService, User } from '../auth.service';
import { DataService } from '../services/data.service';
import { AiService } from '../services/ai.service';
import { DocumentService } from '../services/document.service';

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
  templateUrl: './video.component.html',
  styleUrls: ['./video.component.scss'],
  imports: [CommonModule]
})
export class VideoComponent implements OnInit, OnDestroy {
  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvasElement') canvasElement!: ElementRef<HTMLCanvasElement>;
  
  // State variables
  isTracking = false;
  isVideoInitialized = false;
  stream: MediaStream | null = null;
  bodyAnalysis: BodyAnalysis | null = null;
  userId: number = 0;
  confidenceTrend: 'increasing' | 'decreasing' | 'stable' = 'stable';
  previousConfidence = 0;
  lastAnalysisTime = 0;
  analysisInterval = 100; // Analyze every 100ms
  isCsvDropdownOpen = false;
  fps = 0;
  errorMessage = '';
  
  // For capturing videos and movement data
  private mediaRecorder: MediaRecorder | null = null;
  private recordedChunks: Blob[] = [];
  public capturedVideos: CapturedVideo[] = [];
  public capturedMovements: any[] = [];
  
  // For movement data history
  public poseDataHistory: PoseDataHistory[] = [];
  public faceDataHistory: FaceDataHistory[] = [];
  public handsDataHistory: HandsDataHistory[] = [];
  
  // For temporary video creation
  public temporaryVideoBlob: Blob | null = null;
  private analysisStartTime: number | null = null;
  private analysisEndTime: number | null = null;
  
  constructor(
    private videoService: VideoService,
    private authService: AuthService,
    private dataService: DataService,
    private aiService: AiService,
    private documentService: DocumentService
  ) {}

  ngOnInit(): void {
    console.log('🎬 Video component initialized');
    this.loadCurrentUser();
    this.setupBodyAnalysisSubscription();
  }

  ngOnDestroy(): void {
    console.log('🧹 Cleaning up video component resources');
    this.stopCamera();
    this.videoService.dispose();
  }

  private loadCurrentUser(): void {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.userId = currentUser.id;
      console.log('👤 Current user loaded:', this.userId);
    }
  }

  private setupBodyAnalysisSubscription(): void {
    this.videoService.bodyAnalysis$.subscribe(analysis => {
      this.bodyAnalysis = analysis;
      if (analysis.isAnalyzing) {
        this.collectMovementData(Date.now());
      }
    });
  }

  async startCamera(): Promise<void> {
    console.log('📷 Starting camera...');
    
    if (this.isTracking) {
      console.log('⏭️ Camera already started');
      return;
    }
    
    try {
      // Request camera access
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720 },
        audio: false 
      });
      
      if (this.videoElement) {
        this.videoElement.nativeElement.srcObject = this.stream;
        this.videoElement.nativeElement.play();
        
        // Initialize MediaPipe
        await this.videoService.initializeMediaPipe();
        
        // Setup holistic tracking
        await this.videoService.setupHolistic(this.videoElement.nativeElement);
        
        // Set tracking state
        this.isTracking = true;
        this.isVideoInitialized = true;
        this.analysisStartTime = Date.now();
        this.lastAnalysisTime = 0;
        
        console.log('✅ Camera started and MediaPipe initialized');
      }
    } catch (error) {
      console.error('❌ Error starting camera:', error);
      this.errorMessage = 'Failed to start camera: ' + (error as Error).message;
      this.isTracking = false;
    }
  }

  stopCamera(): void {
    console.log('⏹️ Stopping camera...');
    
    this.isTracking = false;
    
    // Set analysis end time when stopping camera
    this.analysisEndTime = Date.now();
    
    // Create temporary video from analysis period
    this.createTemporaryVideo();

    // Upload all CSV data to backend
    this.uploadAllCSV();

    // Send captured data to backends before stopping
    this.sendCapturedDataToBackends();

    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    
    console.log('⏹️ Camera stopped');
  }

  getBodyConfidence(): number {
    if (!this.bodyAnalysis) return 0;
    
    const poseConfidence = this.bodyAnalysis.poseConfidence || 0;
    const faceConfidence = this.bodyAnalysis.faceConfidence || 0;
    const handsDetected = this.bodyAnalysis.handsDetected || { left: false, right: false };
    const handsCount = (handsDetected.left ? 1 : 0) + (handsDetected.right ? 1 : 0);
    
    // Weighted average: 50% pose, 30% face, 20% hands
    const confidence = (poseConfidence * 0.5) + (faceConfidence * 0.3) + (handsCount * 50 * 0.2);
    return Math.min(100, Math.round(confidence));
  }

  // Methods for template bindings
  getPoseConfidence(): number {
    return this.bodyAnalysis?.poseConfidence || 0;
  }

  getPoseStatus(): string {
    const confidence = this.getPoseConfidence();
    if (confidence > 80) return 'Excellent';
    if (confidence > 60) return 'Bon';
    if (confidence > 40) return 'Moyen';
    if (confidence > 20) return 'Faible';
    return 'Très faible';
  }

  getPoseDetails(): string {
    if (!this.bodyAnalysis?.pose) return 'Aucune donnée';
    
    const keypoints = Object.keys(this.bodyAnalysis.pose);
    return `Points clés détectés: ${keypoints.length}`;
  }

  getFaceConfidence(): number {
    return this.bodyAnalysis?.faceConfidence || 0;
  }

  getFaceStatus(): string {
    const confidence = this.bodyAnalysis?.faceConfidence || 0;
    if (confidence > 80) return 'Détection excellente';
    if (confidence > 60) return 'Détection bonne';
    if (confidence > 40) return 'Détection moyenne';
    if (confidence > 20) return 'Détection faible';
    return 'Pas de visage détecté';
  }

  getFaceExpression(): string {
    if (!this.bodyAnalysis?.face) return 'Aucune expression';
    
    // Simple expression detection based on face metrics
    if (this.bodyAnalysis.face.mouth_open && this.bodyAnalysis.face.mouth_open > 30) {
      return 'Bouche ouverte';
    }
    
    if (this.bodyAnalysis.face.eye_blink_left || this.bodyAnalysis.face.eye_blink_right) {
      return 'Clignement';
    }
    
    return 'Neutre';
  }

  getHandsStatus(): string {
    if (!this.bodyAnalysis?.hands) return 'Mains non détectées';
    
    const leftDetected = !!this.bodyAnalysis.hands.left;
    const rightDetected = !!this.bodyAnalysis.hands.right;
    
    if (leftDetected && rightDetected) return 'Deux mains détectées';
    if (leftDetected) return 'Main gauche détectée';
    if (rightDetected) return 'Main droite détectée';
    return 'Mains non détectées';
  }

  getHandsGestures(): string {
    if (!this.bodyAnalysis?.hands) return 'Aucun geste';
    
    const gestures = [];
    if (this.bodyAnalysis.hands.left?.gesture) {
      gestures.push(`Gauche: ${this.bodyAnalysis.hands.left.gesture}`);
    }
    if (this.bodyAnalysis.hands.right?.gesture) {
      gestures.push(`Droite: ${this.bodyAnalysis.hands.right.gesture}`);
    }
    
    return gestures.length > 0 ? gestures.join(', ') : 'Aucun geste détecté';
  }

  getSystemStatus(): any {
    return {
      camera: this.isVideoInitialized ? '🟢 Actif' : '🔴 Inactif',
      analysis: this.isTracking ? '🟢 En cours' : '🔴 Arrêté',
      fps: `${this.fps} FPS`,
      posture: this.bodyAnalysis?.pose ? '🟢 Détectée' : '🔴 Absente'
    };
  }

  getPoseInfo(): string {
    if (!this.bodyAnalysis?.pose) {
      return 'Pas de pose détectée';
    }
    
    const poseKeys = Object.keys(this.bodyAnalysis.pose);
    if (poseKeys.length === 0) {
      return 'Pas de pose détectée';
    }
    
    // Show first few key points
    const firstPoints = poseKeys.slice(0, 3);
    return firstPoints.map(key => {
      const point = this.bodyAnalysis!.pose![key];
      if (point?.position) {
        return `${key}: (${point.position.x.toFixed(2)}, ${point.position.y.toFixed(2)})`;
      }
      return key;
    }).join(' | ');
  }

  getFaceInfo(): string {
    if (!this.bodyAnalysis?.face) {
      return 'Pas de visage détecté';
    }
    
    // Check for face metrics
    const face = this.bodyAnalysis.face;
    if (face.mouth_open !== undefined) {
      return `Bouche: ${face.mouth_open > 20 ? 'ouverte' : 'fermée'}`;
    }
    
    if (face.eye_blink_left !== undefined || face.eye_blink_right !== undefined) {
      const left = face.eye_blink_left || 0;
      const right = face.eye_blink_right || 0;
      return `Clignotement: G(${left}%) D(${right}%)`;
    }
    
    return 'Visage détecté';
  }

  getHandsInfo(): string {
    if (!this.bodyAnalysis?.hands) {
      return 'Pas détectée | Pas détectée';
    }
    
    const left = this.bodyAnalysis.hands.left ? 
      `Gauche: ${this.bodyAnalysis.hands.left.landmarks?.length || 0} points` : 
      'Pas détectée';
      
    const right = this.bodyAnalysis.hands.right ? 
      `Droite: ${this.bodyAnalysis.hands.right.landmarks?.length || 0} points` : 
      'Pas détectée';
      
    return `${left} | ${right}`;
  }

  toggleCsvDropdown(): void {
    this.isCsvDropdownOpen = !this.isCsvDropdownOpen;
  }

  /**
   * Capture image and movement data
   */
  private async captureImage(): Promise<void> {
    if (!this.isTracking || !this.videoElement || !this.canvasElement) {
      return;
    }
    
    try {
      const video = this.videoElement.nativeElement;
      const canvas = this.canvasElement.nativeElement;
      const ctx = canvas.getContext('2d');
      
      if (!ctx) return;
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw current video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Get image data as base64
      const imageData = canvas.toDataURL('image/jpeg', 0.8);
      
      // Get current body analysis data
      const currentAnalysis = this.videoService.getCurrentAnalysis();
      const jsonData = {
        pose: currentAnalysis.pose,
        face: currentAnalysis.face,
        hands: currentAnalysis.hands,
        timestamp: new Date().toISOString()
      };
      
      // Create data record
      const dataRecord = {
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
      
      // Also save movement data as a document
      const jsonDataString = JSON.stringify(jsonData, null, 2);
      const jsonDataBlob = new Blob([jsonDataString], { type: 'application/json' });
      const jsonDataFile = new File([jsonDataBlob], `movement_data_${Date.now()}.json`, { type: 'application/json' });
      this.documentService.uploadDocumentForLessonOrAnalysis(this.userId, 'movement_data', jsonDataFile).subscribe({
        next: (document) => {
          console.log('📊 Movement data uploaded as document:', document);
        },
        error: (err) => {
          console.error('❌ Error uploading movement data as document:', err);
        }
      });
    } catch (error) {
      console.error('❌ Error capturing image:', error);
    }
  }

  private collectMovementData(timestamp: number): void {
    // Collect pose data
    if (this.bodyAnalysis?.pose) {
      this.poseDataHistory.push({
        timestamp,
        data: {
          confidence: this.bodyAnalysis.poseConfidence || 0,
          head: this.bodyAnalysis.pose['Head'] ? {
            x: this.bodyAnalysis.pose['Head'].position?.x || 0,
            y: this.bodyAnalysis.pose['Head'].position?.y || 0,
            z: this.bodyAnalysis.pose['Head'].position?.z || 0,
            confidence: this.bodyAnalysis.pose['Head'].confidence || 0
          } : null,
          leftShoulder: this.bodyAnalysis.pose['LeftShoulder'] ? {
            x: this.bodyAnalysis.pose['LeftShoulder'].position?.x || 0,
            y: this.bodyAnalysis.pose['LeftShoulder'].position?.y || 0,
            z: this.bodyAnalysis.pose['LeftShoulder'].position?.z || 0,
            confidence: this.bodyAnalysis.pose['LeftShoulder'].confidence || 0
          } : null,
          rightShoulder: this.bodyAnalysis.pose['RightShoulder'] ? {
            x: this.bodyAnalysis.pose['RightShoulder'].position?.x || 0,
            y: this.bodyAnalysis.pose['RightShoulder'].position?.y || 0,
            z: this.bodyAnalysis.pose['RightShoulder'].position?.z || 0,
            confidence: this.bodyAnalysis.pose['RightShoulder'].confidence || 0
          } : null,
          leftHip: this.bodyAnalysis.pose['LeftHip'] ? {
            x: this.bodyAnalysis.pose['LeftHip'].position?.x || 0,
            y: this.bodyAnalysis.pose['LeftHip'].position?.y || 0,
            z: this.bodyAnalysis.pose['LeftHip'].position?.z || 0,
            confidence: this.bodyAnalysis.pose['LeftHip'].confidence || 0
          } : null,
          rightHip: this.bodyAnalysis.pose['RightHip'] ? {
            x: this.bodyAnalysis.pose['RightHip'].position?.x || 0,
            y: this.bodyAnalysis.pose['RightHip'].position?.y || 0,
            z: this.bodyAnalysis.pose['RightHip'].position?.z || 0,
            confidence: this.bodyAnalysis.pose['RightHip'].confidence || 0
          } : null
        }
      });
    }
    
    // Collect face data
    if (this.bodyAnalysis?.face) {
      this.faceDataHistory.push({
        timestamp,
        data: {
          confidence: this.bodyAnalysis.faceConfidence || 0,
          mouthOpen: this.bodyAnalysis.face.mouth_open || 0,
          eyeBlinkLeft: this.bodyAnalysis.face.eye_blink_left || 0,
          eyeBlinkRight: this.bodyAnalysis.face.eye_blink_right || 0,
          eyeLookLeft: this.bodyAnalysis.face.eye_look_left || 0,
          eyeLookRight: this.bodyAnalysis.face.eye_look_right || 0,
          headPosition: this.bodyAnalysis.face.Head ? {
            x: this.bodyAnalysis.face.Head.position?.x || 0,
            y: this.bodyAnalysis.face.Head.position?.y || 0,
            z: this.bodyAnalysis.face.Head.position?.z || 0
          } : null
        }
      });
    }
    
    // Collect hands data
    if (this.bodyAnalysis?.hands) {
      this.handsDataHistory.push({
        timestamp,
        data: {
          left: this.bodyAnalysis.hands.left ? {
            gesture: this.bodyAnalysis.hands.left.gesture || 'unknown',
            handedness: this.bodyAnalysis.hands.left.handedness || 'unknown',
            landmarks: this.bodyAnalysis.hands.left.landmarks ? this.bodyAnalysis.hands.left.landmarks.map((landmark: any) => ({
              x: landmark.x || 0,
              y: landmark.y || 0,
              z: landmark.z || 0
            })) : []
          } : null,
          right: this.bodyAnalysis.hands.right ? {
            gesture: this.bodyAnalysis.hands.right.gesture || 'unknown',
            handedness: this.bodyAnalysis.hands.right.handedness || 'unknown',
            landmarks: this.bodyAnalysis.hands.right.landmarks ? this.bodyAnalysis.hands.right.landmarks.map((landmark: any) => ({
              x: landmark.x || 0,
              y: landmark.y || 0,
              z: landmark.z || 0
            })) : []
          } : null
        }
      });
    }
  }
  
  /**
   * Download the temporary analysis video
   */
  downloadTemporaryVideo(): void {
    console.log('📥 Downloading temporary video');
    
    if (!this.temporaryVideoBlob) {
      console.log('⏭️ No temporary video available');
      return;
    }
    
    // Create download link
    const url = URL.createObjectURL(this.temporaryVideoBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
    
    console.log('📥 Temporary video downloaded');
  }
  
  /**
   * Generate and download CSV file for pose data
   */
  downloadPoseCSV(): void {
    console.log('📥 Downloading pose CSV data');
    
    if (this.poseDataHistory.length === 0) {
      console.log('⏭️ No pose data available');
      return;
    }
    
    // Generate CSV content
    let csvContent = 'Timestamp,Pose Confidence,Head X,Head Y,Head Z,Head Confidence,Left Shoulder X,Left Shoulder Y,Left Shoulder Z,Left Shoulder Confidence,Right Shoulder X,Right Shoulder Y,Right Shoulder Z,Right Shoulder Confidence,Left Hip X,Left Hip Y,Left Hip Z,Left Hip Confidence,Right Hip X,Right Hip Y,Right Hip Z,Right Hip Confidence\n';
    
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
        data.rightHip?.confidence || 0
      ].join(',');
      csvContent += row + '\n';
    });
    
    // Create and download CSV file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pose-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
    
    console.log('📥 Pose CSV data downloaded');
  }

  /**
   * Generate and upload CSV file for pose data to backend
   */
  uploadPoseCSV(): void {
    console.log('📤 Uploading pose CSV data to backend');
    
    if (this.poseDataHistory.length === 0) {
      console.log('⏭️ No pose data available');
      return;
    }
    
    // Generate CSV content
    let csvContent = 'Timestamp,Pose Confidence,Head X,Head Y,Head Z,Head Confidence,Left Shoulder X,Left Shoulder Y,Left Shoulder Z,Left Shoulder Confidence,Right Shoulder X,Right Shoulder Y,Right Shoulder Z,Right Shoulder Confidence,Left Hip X,Left Hip Y,Left Hip Z,Left Hip Confidence,Right Hip X,Right Hip Y,Right Hip Z,Right Hip Confidence\n';
    
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
        data.rightHip?.confidence || 0
      ].join(',');
      csvContent += row + '\n';
    });
    
    // Create CSV file and upload to backend
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const csvFile = new File([blob], `pose-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`, { type: 'text/csv;charset=utf-8;' });
    
    if (this.userId) {
      this.documentService.uploadDocumentForLessonOrAnalysis(this.userId, 'pose_data', csvFile).subscribe({
        next: (document) => {
          console.log('📊 Pose CSV data uploaded as document:', document);
        },
        error: (err) => {
          console.error('❌ Error uploading pose CSV data as document:', err);
        }
      });
    }
    
    console.log('📤 Pose CSV data upload initiated');
  }

  /**
   * Generate and download CSV file for face data
   */
  downloadFaceCSV(): void {
    console.log('📥 Downloading face CSV data');
    
    if (this.faceDataHistory.length === 0) {
      console.log('⏭️ No face data available');
      return;
    }
    
    // Generate CSV content
    let csvContent = 'Timestamp,Face Confidence,Mouth Open,Eye Blink Left,Eye Blink Right,Eye Look Left,Eye Look Right,Head Position X,Head Position Y,Head Position Z\n';
    
    this.faceDataHistory.forEach(entry => {
      const data = entry.data;
      const row = [
        entry.timestamp,
        data.confidence || 0,
        data.mouthOpen ? 1 : 0,
        data.eyeBlinkLeft ? 1 : 0,
        data.eyeBlinkRight ? 1 : 0,
        data.eyeLookLeft ? 1 : 0,
        data.eyeLookRight ? 1 : 0,
        data.headPosition?.x || 0,
        data.headPosition?.y || 0,
        data.headPosition?.z || 0
      ].join(',');
      csvContent += row + '\n';
    });
    
    // Create and download CSV file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `face-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
    
    console.log('📥 Face CSV data downloaded');
  }

  /**
   * Generate and upload CSV file for face data to backend
   */
  uploadFaceCSV(): void {
    console.log('📤 Uploading face CSV data to backend');
    
    if (this.faceDataHistory.length === 0) {
      console.log('⏭️ No face data available');
      return;
    }
    
    // Generate CSV content
    let csvContent = 'Timestamp,Face Confidence,Mouth Open,Eye Blink Left,Eye Blink Right,Eye Look Left,Eye Look Right,Head Position X,Head Position Y,Head Position Z\n';
    
    this.faceDataHistory.forEach(entry => {
      const data = entry.data;
      const row = [
        entry.timestamp,
        data.confidence || 0,
        data.mouthOpen ? 1 : 0,
        data.eyeBlinkLeft ? 1 : 0,
        data.eyeBlinkRight ? 1 : 0,
        data.eyeLookLeft ? 1 : 0,
        data.eyeLookRight ? 1 : 0,
        data.headPosition?.x || 0,
        data.headPosition?.y || 0,
        data.headPosition?.z || 0
      ].join(',');
      csvContent += row + '\n';
    });
    
    // Create CSV file and upload to backend
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const csvFile = new File([blob], `face-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`, { type: 'text/csv;charset=utf-8;' });
    
    if (this.userId) {
      this.documentService.uploadDocumentForLessonOrAnalysis(this.userId, 'face_data', csvFile).subscribe({
        next: (document) => {
          console.log('📊 Face CSV data uploaded as document:', document);
        },
        error: (err) => {
          console.error('❌ Error uploading face CSV data as document:', err);
        }
      });
    }
    
    console.log('📤 Face CSV data upload initiated');
  }

  /**
   * Generate and download CSV file for hands data
   */
  downloadHandsCSV(): void {
    console.log('📥 Downloading hands CSV data');
    
    if (this.handsDataHistory.length === 0) {
      console.log('⏭️ No hands data available');
      return;
    }
    
    // Generate CSV content
    let csvContent = 'Timestamp,Left Gesture,Left Handedness,Left Landmarks Count,Right Gesture,Right Handedness,Right Landmarks Count\n';
    
    this.handsDataHistory.forEach(entry => {
      const data = entry.data;
      const row = [
        entry.timestamp,
        data.left?.gesture || 'unknown',
        data.left?.handedness || 'unknown',
        data.left?.landmarks?.length || 0,
        data.right?.gesture || 'unknown',
        data.right?.handedness || 'unknown',
        data.right?.landmarks?.length || 0
      ].join(',');
      csvContent += row + '\n';
    });
    
    // Create and download CSV file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hands-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
    
    console.log('📥 Hands CSV data downloaded');
  }

  /**
   * Generate and upload CSV file for hands data to backend
   */
  uploadHandsCSV(): void {
    console.log('📤 Uploading hands CSV data to backend');
    
    if (this.handsDataHistory.length === 0) {
      console.log('⏭️ No hands data available');
      return;
    }
    
    // Generate CSV content
    let csvContent = 'Timestamp,Left Gesture,Left Handedness,Left Landmarks Count,Right Gesture,Right Handedness,Right Landmarks Count\n';
    
    this.handsDataHistory.forEach(entry => {
      const data = entry.data;
      const row = [
        entry.timestamp,
        data.left?.gesture || 'unknown',
        data.left?.handedness || 'unknown',
        data.left?.landmarks?.length || 0,
        data.right?.gesture || 'unknown',
        data.right?.handedness || 'unknown',
        data.right?.landmarks?.length || 0
      ].join(',');
      csvContent += row + '\n';
    });
    
    // Create CSV file and upload to backend
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const csvFile = new File([blob], `hands-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`, { type: 'text/csv;charset=utf-8;' });
    
    if (this.userId) {
      this.documentService.uploadDocumentForLessonOrAnalysis(this.userId, 'hands_data', csvFile).subscribe({
        next: (document) => {
          console.log('📊 Hands CSV data uploaded as document:', document);
        },
        error: (err) => {
          console.error('❌ Error uploading hands CSV data as document:', err);
        }
      });
    }
    
    console.log('📤 Hands CSV data upload initiated');
  }

  /**
   * Download all CSV data as a ZIP file
   */
  downloadAllCSV(): void {
    console.log('📥 Downloading all CSV data');
    
    // For simplicity, we'll download each CSV separately
    this.downloadPoseCSV();
    this.downloadFaceCSV();
    this.downloadHandsCSV();
    
    console.log('📥 All CSV data download initiated');
  }

  /**
   * Upload all CSV data to backend
   */
  uploadAllCSV(): void {
    console.log('📤 Uploading all CSV data to backend');
    
    // Upload each CSV separately
    this.uploadPoseCSV();
    this.uploadFaceCSV();
    this.uploadHandsCSV();
    
    console.log('📤 All CSV data upload initiated');
  }

  /**
   * Create a temporary video from the analysis period
   */
  private createTemporaryVideo(): void {
    console.log('🎥 Creating temporary video from analysis period');
    
    if (!this.analysisStartTime || !this.analysisEndTime) {
      console.log('⏭️ Analysis start or end time not set');
      return;
    }
    
    const duration = this.analysisEndTime - this.analysisStartTime;
    console.log(`⏱️ Analysis duration: ${duration}ms`);
    
    // For now, we'll create a placeholder blob
    // In a real implementation, you would combine all the captured video segments
    const videoData = `Video analysis from ${new Date(this.analysisStartTime).toLocaleTimeString()} to ${new Date(this.analysisEndTime).toLocaleTimeString()}`;
    const blob = new Blob([videoData], { type: 'text/plain' });
    this.temporaryVideoBlob = blob;
    
    console.log('🎥 Temporary video created');
    
    // You could also save this to the captured videos array
    const videoMetadata = {
      type: 'temporary_analysis_video',
      startTime: this.analysisStartTime,
      endTime: this.analysisEndTime,
      duration: duration,
      fileSize: blob.size
    };
    
    this.capturedVideos.push({ blob, metadata: videoMetadata });
    
    // Upload the temporary video to the backend
    if (this.userId) {
      const videoFile = new File([blob], `analysis-video-${new Date(this.analysisStartTime).toISOString().slice(0, 19).replace(/:/g, '-')}.txt`, { type: 'text/plain' });
      this.documentService.uploadDocumentForLessonOrAnalysis(this.userId, 'analysis_video', videoFile).subscribe({
        next: (document) => {
          console.log('📹 Analysis video uploaded as document:', document);
        },
        error: (err) => {
          console.error('❌ Error uploading analysis video as document:', err);
        }
      });
    }
    
    // Notify user that temporary video is ready
    console.log('✅ Temporary analysis video is ready for download');
  }

  /**
   * Send captured video and movement data to both Spring Boot and Django AI backends
   */
  private sendCapturedDataToBackends(): void {
    console.log('📤 Sending captured data to backends...');
    
    // Send captured movement data to Spring Boot
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
    
    // Send captured videos to Spring Boot
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
    
    // Send captured movement data to Django AI backend
    if (this.capturedMovements.length > 0) {
      console.log(`📤 Sending ${this.capturedMovements.length} movement records to Django AI`);
      
      this.capturedMovements.forEach((movementData, index) => {
        const aiRecord = {
          user: this.userId,
          json_data: movementData,
          movement_detected: true
        };
        
        this.aiService.createMovementRecord(aiRecord).subscribe({
          next: (record) => {
            console.log(`✅ Movement record ${index + 1}/${this.capturedMovements.length} sent to Django AI:`, record.id);
          },
          error: (err) => {
            console.error(`❌ Error sending movement record ${index + 1} to Django AI:`, err);
          }
        });
      });
    } else {
      console.log('📭 No movement data to send to Django AI');
    }
    
    console.log('📤 All captured data sent to backends');
  }
}