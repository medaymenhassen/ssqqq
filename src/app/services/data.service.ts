import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpRequest } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { DataRecord } from '../models/data.model';
import { AuthService } from '../auth.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private apiUrl = `${environment.apiUrl}/data`; // Adjust to your backend URL
  
  constructor(private http: HttpClient, private authService: AuthService) { }

  // Save a new data record
  saveDataRecord(record: DataRecord): Observable<DataRecord> {
    const token = this.authService.getAccessToken();
    let headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return this.http.post<DataRecord>(this.apiUrl, record, { headers });
  }

  // Get all data records for a user
  getDataRecordsByUserId(userId: number): Observable<DataRecord[]> {
    const token = this.authService.getAccessToken();
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return this.http.get<DataRecord[]>(`${this.apiUrl}/user/${userId}`, { headers });
  }

  // Get a specific data record by ID
  getDataRecordById(id: number): Observable<DataRecord> {
    const token = this.authService.getAccessToken();
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return this.http.get<DataRecord>(`${this.apiUrl}/${id}`, { headers });
  }

  // Update an existing data record
  updateDataRecord(record: DataRecord): Observable<DataRecord> {
    const token = this.authService.getAccessToken();
    let headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return this.http.put<DataRecord>(`${this.apiUrl}/${record.id}`, record, { headers });
  }

  // Delete a data record
  deleteDataRecord(id: number): Observable<void> {
    const token = this.authService.getAccessToken();
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    return this.http.delete<void>(`${this.apiUrl}/${id}`, { headers });
  }

  // Save a data record with video blob
  saveDataRecordWithVideo(record: DataRecord, videoBlob?: Blob): Observable<DataRecord> {
    const token = this.authService.getAccessToken();
    let headers = new HttpHeaders();
    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }
    
    // If we have a video blob, send it as multipart/form-data
    if (videoBlob) {
      const formData = new FormData();
      formData.append('dataRecord', JSON.stringify({
        userId: record.userId,
        imageData: record.imageData,
        videoUrl: record.videoUrl,
        jsonData: record.jsonData,
        timestamp: record.timestamp,
        movementDetected: record.movementDetected
      }));
      formData.append('video', videoBlob, 'video.webm');
      
      return this.http.post<DataRecord>(this.apiUrl + '/with-video', formData, {
        headers: headers,
        reportProgress: true
      });
    } else {
      // Otherwise, send as regular JSON
      headers = headers.set('Content-Type', 'application/json');
      return this.http.post<DataRecord>(this.apiUrl, record, { headers });
    }
  }

  // For demo purposes, we'll store data locally if backend is not available
  private localDataStore: DataRecord[] = [];
  private nextId = 1;

  saveDataRecordLocal(record: DataRecord): Observable<DataRecord> {
    const newRecord = { ...record, id: this.nextId++ };
    this.localDataStore.push(newRecord);
    return of(newRecord);
  }

  getDataRecordsByUserIdLocal(userId: number): Observable<DataRecord[]> {
    const userRecords = this.localDataStore.filter(record => record.userId === userId);
    return of(userRecords);
  }
}