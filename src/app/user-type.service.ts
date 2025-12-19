import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface UserType {
  id: number;
  nom: string;
  description: string;
  special: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Document {
  id: number;
  name: string;
  description: string;
  filePath: string;
  userTypeId: number;
  createdAt: string;
  updatedAt: string;
}

export interface UserTypeRequest {
  nom: string;
  description: string;
  special: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class UserTypeService {
  private apiUrl = 'http://localhost:8080/api';

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
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Get all user types
  getAllUserTypes(): Observable<UserType[]> {
    return this.http.get<UserType[]>(`${this.apiUrl}/user-types`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Get special user types only
  getSpecialUserTypes(): Observable<UserType[]> {
    return this.http.get<UserType[]>(`${this.apiUrl}/user-types/special`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Get normal user types only
  getNormalUserTypes(): Observable<UserType[]> {
    return this.http.get<UserType[]>(`${this.apiUrl}/user-types/normal`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Get user type by ID
  getUserTypeById(id: number): Observable<UserType> {
    return this.http.get<UserType>(`${this.apiUrl}/user-types/${id}`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Get documents for a user type
  getDocumentsByUserType(id: number): Observable<{userTypeId: number, documentsCount: number, documents: Document[]}> {
    return this.http.get<{userTypeId: number, documentsCount: number, documents: Document[]}>(`${this.apiUrl}/user-types/${id}/documents`, {
      headers: this.getAuthHeaders()
    }).pipe(
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