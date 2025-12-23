import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError, timeout, of } from 'rxjs';
import { catchError, map, retry } from 'rxjs/operators';
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
  commercialUseConsent: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('accessToken');
      if (token && this.isTokenFormatValid(token)) {
        this.loadCurrentUser();
      } else if (token) {
        this.logout();
      }
    }
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // REGISTRATION
  // ═════════════════════════════════════════════════════════════════════════════════════

    
  register(request: RegisterRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/register`, request)
      .pipe(
        map((response: LoginResponse) => {
          // Store tokens in localStorage
          if (typeof window !== 'undefined') {
            localStorage.setItem('accessToken', response.accessToken);
            
            // ✅ Si refreshToken absent, utilise accessToken comme fallback
            const refreshToken = response.refreshToken || response.accessToken;
            localStorage.setItem('refreshToken', refreshToken);
          }

          // Load user profile after registration
          this.loadCurrentUser(0);
          return response;
        }),
        catchError(this.handleError)
      );
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // LOGIN - AVEC GESTION DE REFRESH TOKEN MANQUANT
  // ═════════════════════════════════════════════════════════════════════════════════════

  login(email: string, password: string): Observable<LoginResponse> {
    const loginRequest = { email, password };
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, loginRequest)
      .pipe(
        map((response: LoginResponse) => {
          
          if (typeof window !== 'undefined') {
            localStorage.setItem('accessToken', response.accessToken);
            
            // ✅ Si refreshToken absent, utilise accessToken comme fallback
            const refreshToken = response.refreshToken || response.accessToken;
            localStorage.setItem('refreshToken', refreshToken);
            

          }

          // Load user profile after login
          this.loadCurrentUser(0);
          return response;
        }),
        catchError(this.handleError)
      );
  }
  // ═════════════════════════════════════════════════════════════════════════════════════
  // LOGOUT
  // ═════════════════════════════════════════════════════════════════════════════════════

  logout(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      
      localStorage.removeItem('refreshToken');
    }

    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // LOAD CURRENT USER - FIXED VERSION
  // ═════════════════════════════════════════════════════════════════════════════════════

  loadCurrentUser(retryCount: number = 0): void {
    const token = this.getAccessToken();

    // ✅ Pas de token? Rien à faire
    if (!token) {
      return;
    }

    // ✅ Token format invalide? Logout
    if (!this.isTokenFormatValid(token)) {
      this.logout();
      return;
    }

    try {
      const payload = this.decodeToken(token);
      const headers = new HttpHeaders({
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      });
      


      this.http.get<User>(`${this.apiUrl}/user/profile`, { headers })
        .pipe(
          timeout(10000), // ✅ INCREASED to 10 seconds (was 5000ms)
          retry({
            count: 1, // ✅ Retry once before giving up
            delay: 500 // ✅ Wait 500ms before retry
          }),
          catchError((error: any) => {

            // ✅ IF 401/403 → Try refresh token first
            if (error.status === 401 || error.status === 403) {

              if (retryCount < 2) {
                this.refreshToken().subscribe({
                  next: (response: LoginResponse) => {
                    this.loadCurrentUser(retryCount + 1);
                  },
                  error: (refreshError: any) => {
                    this.logout();
                  }
                });
              }

              // ✅ Return empty observable to prevent unhandled rejection
              return of(null);
            }

            // ✅ IF timeout OR network error AND retries available → retry later
            if ((error.name === 'TimeoutError' || error.status === 0) && retryCount < 2) {
              setTimeout(() => {
                this.loadCurrentUser(retryCount + 1);
              }, 1000);

              // ✅ Return empty observable to prevent unhandled rejection
              return of(null);
            }

            // ✅ OTHER ERRORS → Just return empty observable
            return of(null);
          })
        )
        .subscribe({
          next: (user: User | null) => {
            if (user) {
              this.currentUserSubject.next(user);
            }
          },
          error: (err: any) => {
          }
        });

    } catch (error) {
      // Token decoding failed, likely invalid token
    }
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // TOKEN VALIDATION & DECODING
  // ═════════════════════════════════════════════════════════════════════════════════════

  private isTokenFormatValid(token: string): boolean {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return false;
    }

    try {
      const decoded = atob(parts[1]);
      const payload = JSON.parse(decoded);
      return typeof payload === 'object';
    } catch (error) {
      return false;
    }
  }

  private decodeToken(token: string): any {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid JWT format');
      }

      const decoded = atob(parts[1]);
      return JSON.parse(decoded);
    } catch (error) {
      // Token decoding failed
      throw error;
    }
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // HEADERS & TOKEN MANAGEMENT
  // ═════════════════════════════════════════════════════════════════════════════════════

  private getAuthHeaders(): HttpHeaders {
    const token = this.getAccessToken();
    
    if (token) {
      return new HttpHeaders({
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      });
    }

    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  getAccessToken(): string | null {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      return localStorage.getItem('accessToken');
    }
    return null;
  }

  getRefreshToken(): string | null {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      return localStorage.getItem('refreshToken');
    }
    return null;
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // AUTH STATE
  // ═════════════════════════════════════════════════════════════════════════════════════

  isLoggedIn(): boolean {
    const token = this.getAccessToken();
    return !!token && this.isTokenFormatValid(token);
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // USER OPERATIONS
  // ═════════════════════════════════════════════════════════════════════════════════════

  getUserById(id: number): Observable<User> {
    const headers = this.getAuthHeaders();
    return this.http.get<User>(`${this.apiUrl}/users/${id}`, { headers })
      .pipe(catchError(this.handleError));
  }

  getAllUsers(): Observable<User[]> {
    const headers = this.getAuthHeaders();
    return this.http.get<User[]>(`${this.apiUrl}/users`, { headers })
      .pipe(catchError(this.handleError));
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // TOKEN REFRESH
  // ═════════════════════════════════════════════════════════════════════════════════════

  refreshToken(): Observable<LoginResponse> {
    const refreshToken = this.getRefreshToken();
    
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    const refreshRequest = { refreshToken };
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/refresh-token`, refreshRequest)
      .pipe(
        map((response: LoginResponse) => {
          if (typeof window !== 'undefined') {
            localStorage.setItem('accessToken', response.accessToken);
            
            localStorage.setItem('refreshToken', response.refreshToken);
          }
          return response;
        }),
        catchError(this.handleError)
      );
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // ERROR HANDLING
  // ═════════════════════════════════════════════════════════════════════════════════════

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;

      if (error.error && typeof error.error === 'object') {
        if (error.error.error) {
          errorMessage = error.error.error;
        } else if (error.error.message) {
          errorMessage = error.error.message;
        }
      }
    }

    return throwError(() => error);
  }

  // ═════════════════════════════════════════════════════════════════════════════════════
  // UTILITY METHODS
  // ═════════════════════════════════════════════════════════════════════════════════════

  checkAndLoadUser(): void {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      const token = localStorage.getItem('accessToken');
      if (token && this.isTokenFormatValid(token)) {
        this.loadCurrentUser();
      } else if (token) {
        this.logout();
      }
    }
  }

  forceReloadUser(): void {
    this.loadCurrentUser(0);
  }

  debugAuthState(): void {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      const accessToken = localStorage.getItem('accessToken');

      if (accessToken) {
        try {
          const payload = this.decodeToken(accessToken);
        } catch (e) {
          // Token decoding failed
        }
      }

    }
  }
}