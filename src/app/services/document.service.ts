import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Document {
  id: number;
  fileName: string;
  fileType: string;
  filePath: string;
  fileSize: number;
  userId: number;
  userTypeId: number;
  uploadedAt: string;
  approved: boolean;
  createdAt: string;
  updatedAt: string;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Get authorization headers
  private getAuthHeaders(): HttpHeaders {
    // Check if we're in browser context
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('accessToken');
      if (token) {
        return new HttpHeaders({
          'Authorization': `Bearer ${token}`
        });
      }
    }
    // Return default headers if no token or in SSR context
    return new HttpHeaders();
  }

  // Upload documents for special user type request
  uploadDocuments(userId: number, userTypeId: number, files: File[]): Observable<any> {
    const formData = new FormData();
    formData.append('userId', userId.toString());
    formData.append('userTypeId', userTypeId.toString());
    
    files.forEach(file => {
      formData.append('documents', file);
    });

    // Create headers without Content-Type for multipart/form-data
    const headers = this.getAuthHeaders().delete('Content-Type');
    
    return this.http.post(`${this.apiUrl}/special-user-requests/submit-request`, formData, {
      headers: headers
    });
  }

  // Get pending requests (for admins)
  getPendingRequests(): Observable<Document[]> {
    return this.http.get<Document[]>(`${this.apiUrl}/special-user-requests/pending`, {
      headers: this.getAuthHeaders()
    });
  }

  // Approve a special user request
  approveRequest(documentId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/special-user-requests/approve/${documentId}`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  // Reject a special user request
  rejectRequest(documentId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/special-user-requests/reject/${documentId}`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get documents for a specific user
  getUserDocuments(userId: number): Observable<Document[]> {
    return this.http.get<Document[]>(`${this.apiUrl}/special-user-requests/user/${userId}`, {
      headers: this.getAuthHeaders()
    });
  }
  
  // Upload document for lesson or body analysis
  uploadDocumentForLessonOrAnalysis(userId: number, context: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('userId', userId.toString());
    formData.append('context', context);
    formData.append('file', file);

    // Create headers without Content-Type for multipart/form-data
    const headers = this.getAuthHeaders().delete('Content-Type');
    
    return this.http.post(`${this.apiUrl}/documents/upload-for-lesson-or-analysis`, formData, {
      headers: headers
    });
  }
  
  // Upload movement data with images to Django backend
  uploadMovementData(movementData: any): Observable<any> {
    const formData = new FormData();
    
    // Add the movement data
    formData.append('user', movementData.user?.toString() || '1'); // Default to 1 if user is null
    formData.append('label', movementData.label || 'Movement Capture');
    formData.append('movementType', movementData.movementType || 'general');
    formData.append('timestamp', movementData.timestamp?.toString() || new Date().toISOString());
    
    // Add JSON data if it exists
    if (movementData.jsonData) {
      formData.append('jsonData', JSON.stringify(movementData.jsonData));
    }
    
    // Add images if they exist
    if (movementData.images && movementData.images.length > 0) {
      movementData.images.forEach((image: string, index: number) => {
        // Convert data URL to Blob
        const blob = this.dataURLToBlob(image);
        formData.append(`images`, blob, `movement_${Date.now()}_${index}.png`);
      });
    }
    
    // For Django backend, we don't need authentication headers
    // The auth interceptor is configured to skip Django requests
    // Create headers without Content-Type for multipart/form-data
    const headers = new HttpHeaders(); // No auth headers for Django
    

    
    // Send to Django backend using environment configuration
    const request = this.http.post(`${environment.aiApiUrl}/movements/upload/`, formData, {
      headers: headers
    });
    
    return request;
  }
  
  // Helper method to convert data URL to Blob
  private dataURLToBlob(dataURL: string): Blob {
    const arr = dataURL.split(',');
    const mimeMatch = arr[0].match(/:(.*?);/);
    const mime = mimeMatch ? mimeMatch[1] : 'image/png';
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    
    return new Blob([u8arr], { type: mime });
  }
}