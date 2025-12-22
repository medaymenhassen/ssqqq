import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class VideoUploadService {
  private springBootUrl = environment.apiUrl.replace('/api', ''); // Spring Boot API URL

  constructor(private http: HttpClient) {}

  /**
   * Create a video from CSV data
   * @param csvContent The CSV content as a string
   * @param userId The user ID
   * @param videoName The name for the resulting video
   * @returns Observable with the response
   */
  createVideoFromCSV(csvContent: string, userId: number, videoName: string): Observable<any> {
    const formData = new FormData();
    const csvBlob = new Blob([csvContent], { type: 'text/csv' });
    formData.append('file', csvBlob, `${videoName.replace('.mp4', '')}.csv`);
    formData.append('userId', userId.toString());
    formData.append('videoName', videoName);

    return this.http.post(`${this.springBootUrl}/springboot/csv/create-video`, formData);
  }

  /**
   * Upload a video file
   * @param videoBlob The video as a Blob
   * @param userId The user ID
   * @param filename The filename for the video
   * @returns Observable with the response
   */
  uploadVideo(videoBlob: Blob, userId: number, filename: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', videoBlob, filename);
    formData.append('userId', userId.toString());

    return this.http.post(`${this.springBootUrl}/springboot/csv/upload-video`, formData);
  }
}