import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
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

  // For temporary video creation
  public temporaryVideoBlob: Blob | null = null;
  private temporaryVideoUrl: string | null = null;
  private analysisStartTime: number | null = null;
  private analysisEndTime: number | null = null;
  
  // For video file upload
  public selectedVideoFile: File | null = null;
  public isProcessingVideo = false;
  public storedVideoUrl: string | null = null;
  
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
    this.videoService.dispose();
  }

  private loadCurrentUser(): void {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.userId = currentUser.id;
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
    if (this.isTracking) {
      return;
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
      }
    } catch (error) {
      console.error('Error starting camera:', error);
      this.errorMessage = 'Failed to start camera: ' + (error as Error).message;
      this.isTracking = false;
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
        console.error('MediaRecorder error:', event);
        this.errorMessage = 'Error recording video';
      };

      // Start recording with 1 second chunks
      this.mediaRecorder.start(1000);
    } catch (error) {
      console.error('Error starting recording:', error);
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
      console.error('Error creating temporary video:', error);
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
              console.log('Video created and stored:', response);
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
              console.error('Error creating video from CSV:', err);
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
        console.error('Backend not available, creating video locally:', error);
        // Backend not available, create video locally
        this.createVideoLocally(csvContent, videoName);
      });
  }

  // Create video locally when backend is not available
  private createVideoLocally(csvContent: string, videoName: string): void {
    alert('Le backend n\'est pas disponible. La vidéo sera créée localement.');
    
    // In a real implementation, we would convert the CSV data to a video locally
    // For now, we'll just create a placeholder video
    const placeholderVideo = new Blob([], { type: 'video/mp4' });
    const videoUrl = URL.createObjectURL(placeholderVideo);
    this.storedVideoUrl = videoUrl;
    this.temporaryVideoUrl = videoUrl;
    
    // Create and download the CSV file for user to use with backend later
    const csvBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const csvUrl = URL.createObjectURL(csvBlob);
    const a = document.createElement('a');
    a.href = csvUrl;
    a.download = `movement-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();
    
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(csvUrl);
    }, 100);
    
    console.log('Local video processing completed, CSV file downloaded for later backend processing');
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
          console.log('Pose CSV data uploaded as document:', document);
        },
        error: (err) => {
          console.error('Error uploading pose CSV data as document:', err);
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
          console.log('Face CSV data uploaded as document:', document);
        },
        error: (err) => {
          console.error('Error uploading face CSV data as document:', err);
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
          console.log('Hands CSV data uploaded as document:', document);
        },
        error: (err) => {
          console.error('Error uploading hands CSV data as document:', err);
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
    console.log('Sending captured data to backends...');
    
    // Check if backend is available before sending data
    fetch('http://localhost:8080/health', { method: 'GET' })
      .then(response => {
        if (response.ok) {
          // Backend is available, proceed with API calls
          this.sendDataToBackend();
        } else {
          console.log('Backend not available, storing data locally');
          this.storeDataLocally();
        }
      })
      .catch(error => {
        console.log('Backend not available, storing data locally');
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
    

    
    
    console.log('All captured data processed');
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
    
    console.log(`Preparing to send ${allMovementData.length} movement records to Django AI`);
    
    if (allMovementData.length > 0) {
      allMovementData.forEach((movementData, index) => {
        const aiRecord = {
          user: this.userId,
          json_data: movementData,
          movement_detected: true
        };

        this.aiService.createMovementRecord(aiRecord).subscribe({
          next: (record) => {
            console.log(`Movement record ${index + 1}/${allMovementData.length} sent to Django AI:`, record.id);
          },
          error: (err) => {
            console.error(`Error sending movement record ${index + 1} to Django AI:`, err);
          }
        });
      });
    } else {
      console.log('No movement data to send to Django AI');
    }
    
    console.log('All captured data sent to backends');
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
    
    // Store in localStorage
    const dataStr = JSON.stringify(localData);
    localStorage.setItem('movementData', dataStr);
    
    console.log('Movement data stored locally for later upload');
    
    // Also create a downloadable file
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `movement-data-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }

  // ========== MÉTHODES MANQUANTES POUR LE TEMPLATE ==========

  // Toggle CSV dropdown
  toggleCsvDropdown(): void {
    this.isCsvDropdownOpen = !this.isCsvDropdownOpen;
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
      console.log('⏭️ No user ID available');
      this.errorMessage = 'No user ID available';
      return;
    }

    const filename = `recorded-video-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.webm`;
    
    this.videoUploadService.uploadVideo(this.temporaryVideoBlob, this.userId, filename).subscribe({
      next: (response) => {
        console.log('Temporary video uploaded successfully:', response);
        alert('Video uploaded successfully!');
      },
      error: (err) => {
        console.error('Error uploading temporary video:', err);
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
      console.error('Error processing video file:', error);
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
      console.log('⏭️ No stored video to download');
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
      console.error('Error processing image file:', error);
      this.errorMessage = 'Erreur lors du traitement de l' + "'" + 'image: ' + (error as Error).message;
    } finally {
      this.isProcessingImage = false;
    }
  }

  // Override stopCamera to also store the analyzed video
  stopCamera(): void {
    this.isTracking = false;

    this.analysisEndTime = Date.now();

    // Stop recording
    this.stopRecording();

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
}