import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface DjUser {
  id: number;
  email: string;
  firstname: string;
  lastname: string;
  role: string;
  is_authenticated: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class DjAuthService {
  private djangoApiUrl = environment.aiApiUrl;
  private currentUserSubject = new BehaviorSubject<DjUser | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Check if user is already logged in from a previous session
    this.checkCurrentSession();
  }

  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  // Check if there's an active session
  private checkCurrentSession(): void {
    this.getCurrentUser().subscribe({
      next: (user) => {
        if (user && user.is_authenticated) {
          this.currentUserSubject.next(user);
        }
      },
      error: () => {
        // User is not authenticated
        this.currentUserSubject.next(null);
      }
    });
  }

  // Login to Django authentication system
  login(email: string, password: string): Observable<DjUser> {
    const loginData = { email, password };
    return this.http.post<DjUser>(`${this.djangoApiUrl}/auth/login/`, loginData, {
      headers: this.getAuthHeaders()
    }).pipe(
      map(user => {
        this.currentUserSubject.next(user);
        return user;
      }),
      catchError(error => {
        console.error('Django login error:', error);
        throw error;
      })
    );
  }

  // Get current user from Django
  getCurrentUser(): Observable<DjUser | null> {
    return this.http.get<DjUser>(`${this.djangoApiUrl}/auth/user/`, {
      headers: this.getAuthHeaders()
    }).pipe(
      map(user => {
        if (user && user.is_authenticated) {
          this.currentUserSubject.next(user);
          return user;
        } else {
          this.currentUserSubject.next(null);
          return null;
        }
      }),
      catchError(error => {
        // Handle 404 specifically - means user is not authenticated
        if (error.status === 404) {
          console.log('User not authenticated with Django (404)');
          this.currentUserSubject.next(null);
          return of(null);
        } else {
          console.error('Get current user error:', error);
          this.currentUserSubject.next(null);
          return of(null);
        }
      })
    );
  }

  // Logout from Django
  logout(): Observable<any> {
    // Note: Django session will be cleared on the server side
    // We just need to clear the local state
    this.currentUserSubject.next(null);
    return of({ success: true });
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const currentUser = this.currentUserSubject.value;
    return currentUser !== null && currentUser.is_authenticated;
  }

  // Get current user
  getCurrentUserValue(): DjUser | null {
    return this.currentUserSubject.value;
  }
}