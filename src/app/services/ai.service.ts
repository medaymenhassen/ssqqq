import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface MovementRecord {
  id?: number;
  user: number;
  image_data?: string;
  video_url?: string;
  json_data?: any;
  movement_detected?: boolean;
  timestamp?: string;
}

export interface PoseData {
  body_part: string;
  x_position: number;
  y_position: number;
  z_position?: number;
  confidence?: number;
}

export interface FaceData {
  eye_openness_left?: number;
  eye_openness_right?: number;
  mouth_openness?: number;
  head_position_x?: number;
  head_position_y?: number;
  head_position_z?: number;
}

export interface HandData {
  hand: string;
  gesture?: string;
  confidence?: number;
  landmarks?: any;
}

@Injectable({
  providedIn: 'root'
})
export class AiService {
  private aiApiUrl = environment.aiApiUrl;

  constructor(private http: HttpClient) {}

  // Create a new movement record
  createMovementRecord(record: MovementRecord): Observable<any> {
    return this.http.post(`${this.aiApiUrl}/movement-records/create/`, record);
  }

  // Get all movement records
  getMovementRecords(): Observable<MovementRecord[]> {
    return this.http.get<MovementRecord[]>(`${this.aiApiUrl}/movement-records/`);
  }

  // Get movement records for a specific user
  getUserMovementRecords(userId: number): Observable<MovementRecord[]> {
    return this.http.get<MovementRecord[]>(`${this.aiApiUrl}/movement-records/user/${userId}/`);
  }

  // Get a specific movement record by ID
  getMovementRecord(id: number): Observable<MovementRecord> {
    return this.http.get<MovementRecord>(`${this.aiApiUrl}/movement-records/${id}/`);
  }

  // Update a movement record
  updateMovementRecord(id: number, record: MovementRecord): Observable<MovementRecord> {
    return this.http.put<MovementRecord>(`${this.aiApiUrl}/movement-records/${id}/`, record);
  }

  // Delete a movement record
  deleteMovementRecord(id: number): Observable<any> {
    return this.http.delete(`${this.aiApiUrl}/movement-records/${id}/`);
  }
}