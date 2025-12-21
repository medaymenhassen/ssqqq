import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../environments/environment';

export interface UserType {
  id: number;
  nameFr: string;
  nameEn: string;
  descFr: string;
  descEn: string;
  bigger: string;
  createdAt: string;
  updatedAt: string;
}

export interface Document {
  id: number;
  name: string;
  description: string;
  filePath: string;
  userId?: number; // User who uploaded the document
  userTypeId: number;
  createdAt: string;
  updatedAt: string;
}

export interface UserTypeRequest {
  nameFr: string;
  nameEn: string;
  descFr: string;
  descEn: string;
  bigger: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserTypeService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Get authorization headers
  private getAuthHeaders(): HttpHeaders {
    // Check if we're in browser context
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('accessToken');
      if (token) {
        return new HttpHeaders({
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        });
      }
    }
    // Return default headers if no token or in SSR context
    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  // Create a new user type
  createUserType(request: UserTypeRequest): Observable<UserType> {
    return this.http.post<UserType>(`${this.apiUrl}/user-types`, request, {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Get all user types
  getAllUserTypes(): Observable<UserType[]> {
    // This endpoint is publicly accessible, so we don't need to send auth headers
    return this.http.get<UserType[]>(`${this.apiUrl}/user-types`).pipe(
      catchError(this.handleError)
    );
  }

  // Get user type by ID
  getUserTypeById(id: number): Observable<UserType> {
    return this.http.get<UserType>(`${this.apiUrl}/user-types/${id}`).pipe(
      catchError(this.handleError)
    );
  }

  // Update user type
  updateUserType(id: number, request: UserTypeRequest): Observable<UserType> {
    return this.http.put<UserType>(`${this.apiUrl}/user-types/${id}`, request, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Delete user type
  deleteUserType(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/user-types/${id}`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Handle HTTP errors
  private handleError(error: any): Observable<never> {
    console.error('An error occurred:', error);
    
    // Handle specific error cases
    if (error.status === 403) {
      // User doesn't have permission
      throw new Error('Accès refusé. Vous devez être administrateur pour effectuer cette action.');
    } else if (error.status === 401) {
      // User not authenticated
      throw new Error('Vous devez vous connecter pour effectuer cette action.');
    } else {
      // Generic error
      throw new Error('Une erreur est survenue. Veuillez réessayer plus tard.');
    }
  }
}