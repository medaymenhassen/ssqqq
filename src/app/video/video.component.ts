import { Component, OnInit, OnDestroy, ViewChild, ElementRef, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VideoService, BodyAnalysis } from '../video.service';
import { AuthService, User } from '../auth.service';
import { DataService } from '../services/data.service';
import { AiService } from '../services/ai.service';
import { DocumentService } from '../services/document.service';
import { VideoUploadService } from '../services/video-upload.service';

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
export class VideoComponent implements OnInit, OnDestroy {
  @ViewChild('videoElement') videoElement!: ElementRef;
  @ViewChild('canvasElement') canvasElement!: ElementRef;

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
  private imageCaptureInterval: any;
  
  // For image file upload
  public selectedImageFile: File | null = null;
  public isProcessingImage = false;

  constructor(
    private videoService: VideoService,
    private authService: AuthService,
    private dataService: DataService,
    private aiService: AiService,
    private documentService: DocumentService,
    private videoUploadService: VideoUploadService
  ) {}

  ngOnInit(): void {
    this.loadCurrentUser();
    this.setupBodyAnalysisSubscription();
  }

ngOnDestroy(): void {
  this.stopCamera();
  this.stopDataSending();
  
  // Optionnel: appeler dispose() s'il existe
  if (this.videoService && typeof (this.videoService as any).dispose === 'function') {
    (this.videoService as any).dispose();
  }
}

  private loadCurrentUser(): void {
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
      this.bodyAnalysis = analysis;
      if (analysis.isAnalyzing) {
        this.collectMovementData(Date.now());
        // Also detect movements and capture images when movement is detected
        this.detectMovementAndCapture();
      }
    });
  }

  async startCamera(): Promise<void> {
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
      }
    } catch (error) {
      this.errorMessage = 'Failed to start camera: ' + (error as Error).message;
      this.isTracking = false;
    }
  }
  
  // Override stopCamera to also stop data sending
  stopCamera(): void {
    this.isTracking = false;

    this.analysisEndTime = Date.now();

    // Stop recording
    this.stopRecording();

    // Stop image capture interval
    this.stopImageCapture();

    // Stop data sending
    this.stopDataSending();

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
    // Clear any existing interval
    this.stopDataSending();
    
    // Start sending detailed data every 5 seconds as requested
    this.dataSendInterval = setInterval(() => {
      // Check authentication status
      const currentUser = this.authService.getCurrentUser();
      
      // Only send data if user ID is available
      if (this.userId) {

        this.sendMovementData();
      } else {
        console.warn('❌ User ID not available, skipping data send');
        // Try to reload user if not available
        this.loadCurrentUser();
      }
    }, 5000); // Every 5 seconds
  }
  
  private stopDataSending(): void {
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
    // Vérifier que nous avons des images et des données
    if (this.capturedImagesForSend.length === 0 || !this.userId) {

      return;
    }
    

    
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
    

    
    // Send to Django backend via document service (the only service that handles this)
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
      // Add more sophisticated movement detection here if needed
    }
  }
  
  private startRecording(): void {
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

    let csvContent = 'Timestamp,Face Confidence,Mouth Open,Eye Blink Left,Eye Blink Right,Eye Look Left,Eye Look Right,Head X,Head Y,Head Z\n';

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
        data.headPosition?.z || 0
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

    let csvContent = 'Timestamp,Hand,Gesture,Confidence,Landmark Count\n';

    this.handsDataHistory.forEach(entry => {
      const data = entry.data;
      
      // Left hand data
      if (data.left) {
        const row = [
          entry.timestamp,
          'Left',
          data.left.gesture || '',
          data.left.confidence || 0,
          data.left.landmarks ? data.left.landmarks.length : 0
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
          data.right.landmarks ? data.right.landmarks.length : 0
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
    let csvContent = 'Timestamp,Pose Confidence,Head X,Head Y,Head Z,Head Confidence,Left Shoulder X,Left Shoulder Y,Left Shoulder Z,Left Shoulder Confidence,Right Shoulder X,Right Shoulder Y,Right Shoulder Z,Right Shoulder Confidence,Left Hip X,Left Hip Y,Left Hip Z,Left Hip Confidence,Right Hip X,Right Hip Y,Right Hip Z,Right Hip Confidence,Face Confidence,Mouth Open,Eye Blink Left,Eye Blink Right,Eye Look Left,Eye Look Right,Head Position X,Head Position Y,Head Position Z,Left Hand Gesture,Left Hand Confidence,Left Hand Landmarks,Right Hand Gesture,Right Hand Confidence,Right Hand Landmarks\n';

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

    // Check if backend is available before attempting to create video
    fetch('http://localhost:8080/health', { method: 'GET' })
      .then(response => {
        if (response.ok) {
          // Backend is available, proceed with API call
          this.videoUploadService.createVideoFromCSV(
            csvContent,
            this.userId,
            videoName
          ).subscribe({
            next: (response) => {
              // Update the stored video URL with the one from the backend
              if (response.videoUrl) {
                // Prepend the API URL if it's a relative path
                const fullVideoUrl = response.videoUrl.startsWith('http') ? 
                  response.videoUrl : 
                  `http://localhost:8080${response.videoUrl}`;
                this.storedVideoUrl = fullVideoUrl;
                
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
        } else {
          // Backend not available, create video locally
          this.createVideoLocally(csvContent, videoName);
        }
      })
      .catch(error => {
        // Backend not available, create video locally
        this.createVideoLocally(csvContent, videoName);
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

    let csvContent = 'Timestamp,Face Confidence,Mouth Open,Eye Blink Left,Eye Blink Right,Eye Look Left,Eye Look Right,Head X,Head Y,Head Z\n';

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
        data.headPosition?.z || 0
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

    let csvContent = 'Timestamp,Hand,Gesture,Confidence,Landmark Count\n';

    this.handsDataHistory.forEach(entry => {
      const data = entry.data;
      
      // Left hand data
      if (data.left) {
        const row = [
          entry.timestamp,
          'Left',
          data.left.gesture || '',
          data.left.confidence || 0,
          data.left.landmarks ? data.left.landmarks.length : 0
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
          data.right.landmarks ? data.right.landmarks.length : 0
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
          } : null
        }
      });
    }

    // Collect face data
    if (hasFaceData) {
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
          } : null
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
            confidence: 0  // Placeholder since confidence isn't available
          } : null,
          right: this.bodyAnalysis!.hands!.right ? {
            gesture: this.bodyAnalysis!.hands!.right.gesture || 'unknown',
            handedness: this.bodyAnalysis!.hands!.right.handedness || 'unknown',
            landmarks: this.bodyAnalysis!.hands!.right.landmarks ? this.bodyAnalysis!.hands!.right.landmarks.map((landmark: any) => ({
              x: landmark.x !== undefined ? landmark.x : 0,
              y: landmark.y !== undefined ? landmark.y : 0,
              z: landmark.z !== undefined ? landmark.z : 0
            })) : [],
            confidence: 0  // Placeholder since confidence isn't available
          } : null
        }
      });
    }
    
  }

  private sendCapturedDataToBackends(): void {
    
    // Check if backend is available before sending data
    fetch('http://localhost:8080/health', { method: 'GET' })
      .then(response => {
        if (response.ok) {
          // Backend is available, proceed with API calls
          this.sendDataToBackend();
        } else {
          this.storeDataLocally();
        }
      })
      .catch(error => {
        this.storeDataLocally();
      });
    
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
        face: faceEntry?.data || null,
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
        face: faceEntry?.data || null,
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
    if (confidence > 80) return 'Visage clair';
    if (confidence > 60) return 'Visage visible';
    if (confidence > 40) return 'Visage partiel';
    if (confidence > 20) return 'Visage flou';
    return 'Visage invisible';
  }

  // Get face expression
  getFaceExpression(): string {
    if (!this.bodyAnalysis?.face) return 'Aucune expression';
    // This would be implemented based on actual face data
    return 'Neutre';
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
      // In a real implementation, we would process the video file using MediaPipe
      // For now, we'll simulate the processing by creating a URL for the selected file
      const videoUrl = URL.createObjectURL(this.selectedVideoFile);
      
      // Set the video element source to the selected file
      if (this.videoElement) {
        this.videoElement.nativeElement.src = videoUrl;
        this.videoElement.nativeElement.play();
        
        // Initialize MediaPipe for the video file
        await this.videoService.initializeMediaPipe();
        await this.videoService.setupHolistic(this.videoElement.nativeElement);
        
        this.isTracking = true;
        this.isVideoInitialized = true;
        this.analysisStartTime = Date.now();
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
        this.videoElement.nativeElement.play();
        
        // Initialize MediaPipe for the image file
        await this.videoService.initializeMediaPipe();
        await this.videoService.setupHolistic(this.videoElement.nativeElement);
        
        this.isTracking = true;
        this.isVideoInitialized = true;
        this.analysisStartTime = Date.now();
      }
    } catch (error) {
      this.errorMessage = 'Erreur lors du traitement de l' + "'" + 'image: ' + (error as Error).message;
    } finally {
      this.isProcessingImage = false;
    }
  }

}
