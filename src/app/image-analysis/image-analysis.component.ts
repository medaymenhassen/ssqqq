import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ImageBodyAnalysisService } from '../services/image-body-analysis.service';
import { AuthService } from '../auth.service';
import { VideoUploadService } from '../services/video-upload.service';

@Component({
  selector: 'app-image-analysis',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './image-analysis.component.html',
  styleUrls: ['./image-analysis.component.scss']
})
export class ImageAnalysisComponent implements OnInit {
  selectedFile: File | null = null;
  isAnalyzing = false;
  analysisResult: any = null;
  errorMessage = '';
  userId: number = 0;

  constructor(
    private imageAnalysisService: ImageBodyAnalysisService,
    private authService: AuthService,
    private videoUploadService: VideoUploadService
  ) {}

  ngOnInit(): void {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.userId = currentUser.id;
    }
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.errorMessage = '';
    }
  }

  async analyzeImage(): Promise<void> {
    if (!this.selectedFile) {
      this.errorMessage = 'Veuillez sélectionner une image à analyser.';
      return;
    }

    this.isAnalyzing = true;
    this.errorMessage = '';

    try {
      // In a real implementation, we would convert the file to a URL and analyze it
      // For demo purposes, we'll simulate analysis of the provided screenshot
      const imageUrl = '../../Capture d’écran 2025-12-13 140829.jpg';
      
      this.analysisResult = await this.imageAnalysisService.analyzeImageFromUrl(imageUrl);
      console.log('✅ Image analysis completed:', this.analysisResult);
    } catch (error) {
      console.error('❌ Error analyzing image:', error);
      this.errorMessage = 'Erreur lors de l\'analyse de l\'image: ' + (error as Error).message;
    } finally {
      this.isAnalyzing = false;
    }
  }

  downloadPoseCSV(): void {
    if (!this.analysisResult) return;
    
    const csvContent = this.imageAnalysisService.generatePoseCSV(this.analysisResult);
    this.downloadCSV(csvContent, 'pose-data.csv');
  }

  downloadFaceCSV(): void {
    if (!this.analysisResult) return;
    
    const csvContent = this.imageAnalysisService.generateFaceCSV(this.analysisResult);
    this.downloadCSV(csvContent, 'face-data.csv');
  }

  downloadHandsCSV(): void {
    if (!this.analysisResult) return;
    
    const csvContent = this.imageAnalysisService.generateHandsCSV(this.analysisResult);
    this.downloadCSV(csvContent, 'hands-data.csv');
  }

  downloadAllCSV(): void {
    if (!this.analysisResult) return;
    
    const poseCSV = this.imageAnalysisService.generatePoseCSV(this.analysisResult);
    const faceCSV = this.imageAnalysisService.generateFaceCSV(this.analysisResult);
    const handsCSV = this.imageAnalysisService.generateHandsCSV(this.analysisResult);
    
    // Combine all CSV data
    const combinedCSV = poseCSV + faceCSV + handsCSV;
    this.downloadCSV(combinedCSV, 'all-body-data.csv');
  }

  createVideoFromData(): void {
    if (!this.analysisResult) return;
    
    const csvContent = this.imageAnalysisService.generateCombinedCSV(this.analysisResult);
    
    // In a real implementation, this would call the video upload service
    // this.videoUploadService.createVideoFromCSV(csvContent, this.userId, 'analysis-video.mp4')
    //   .subscribe(...)
    
    // For demo, just show an alert
    alert('Dans une implémentation réelle, cela créerait une vidéo à partir des données CSV.');
    console.log('🎥 Would create video from CSV data');
  }

  private downloadCSV(csvContent: string, filename: string): void {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
  }
}