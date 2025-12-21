import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Router } from '@angular/router';
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

export interface User {
  id: number;
  firstname: string;
  lastname: string;
  email: string;
  role: string;
  enabled: boolean;
  userType?: UserType;
  createdAt: string;
  updatedAt: string;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
  message: string;
}

export interface RegisterRequest {
  firstname: string;
  lastname: string;
  email: string;
  password: string;
  confirmPassword?: string;
  rgpdAccepted: boolean;
  ccpaAccepted: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    // Check if user is already logged in (only in browser)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('accessToken');
      if (token) {
        // Optionally verify token validity
        this.loadCurrentUser();
      }
    }
  }

  // Register a new user
  register(request: RegisterRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register`, request)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Login user
  login(email: string, password: string): Observable<LoginResponse> {
    const loginRequest = { email, password };
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, loginRequest)
      .pipe(
        map(response => {
          // Store tokens in localStorage (only in browser)
          if (typeof window !== 'undefined') {
            localStorage.setItem('accessToken', response.accessToken);
            localStorage.setItem('refreshToken', response.refreshToken);
          }
          
          // Load current user
          this.loadCurrentUser();
          
          return response;
        }),
        catchError(this.handleError)
      );
  }

  // Logout user
  logout(): void {
    // Clear tokens from localStorage (only in browser)
    if (typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
    
    // Clear current user
    this.currentUserSubject.next(null);
    
    // Navigate to login page
    this.router.navigate(['/login']);
  }

  // Load current user information
  loadCurrentUser(): void {
    const token = this.getAccessToken();
    if (token) {
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
      this.http.get<User>(`${this.apiUrl}/user/profile`, { headers })
        .pipe(
          catchError(this.handleError)
        )
        .subscribe({
          next: (user) => {
            this.currentUserSubject.next(user);
          },
          error: () => {
            // If token is invalid, clear it
            this.logout();
          }
        });
    }
  }

  // Get authorization headers
  private getAuthHeaders(): HttpHeaders {
    const token = this.getAccessToken();
    if (token) {
      return new HttpHeaders({
        'Authorization': `Bearer ${token}`
      });
    }
    return new HttpHeaders();
  }

  // Get access token
  getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('accessToken');
    }
    return null;
  }

  // Get refresh token
  getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refreshToken');
    }
    return null;
  }

  // Check if user is logged in
  isLoggedIn(): boolean {
    return !!this.getAccessToken();
  }

  // Get current user
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  // Get user by ID
  getUserById(id: number): Observable<User> {
    const headers = this.getAuthHeaders();
    return this.http.get<User>(`${this.apiUrl}/users/${id}`, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  // Get all users
  getAllUsers(): Observable<User[]> {
    const headers = this.getAuthHeaders();
    return this.http.get<User[]>(`${this.apiUrl}/users`, { headers })
      .pipe(
        catchError(this.handleError)
      );
  }

  // Refresh token
  refreshToken(): Observable<LoginResponse> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    const refreshRequest = { refreshToken };
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/refresh-token`, refreshRequest)
      .pipe(
        map(response => {
          // Store new tokens
          localStorage.setItem('accessToken', response.accessToken);
          localStorage.setItem('refreshToken', response.refreshToken);
          return response;
        }),
        catchError(this.handleError)
      );
  }

  // Handle HTTP errors
  private handleError(error: any): Observable<never> {
    console.error('An error occurred:', error);
    return throwError(() => error);
  }
}