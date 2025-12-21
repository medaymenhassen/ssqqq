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
}