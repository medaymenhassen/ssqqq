import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { environment } from '../../environments/environment';

export interface DjangoUser {
  id: number;
  email: string;
  firstname: string;
  lastname: string;
  role: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface DjangoOffer {
  id: number;
  title: string;
  description: string;
  price: number;
  duration_hours: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DjangoUserOffer {
  id: number;
  user_id: number;
  offer_id: number;
  purchase_date: string;
  expiration_date: string;
  is_active: boolean;
  approval_status: 'PENDING' | 'APPROVED' | 'REJECTED';
  created_at: string;
  updated_at: string;
}

export interface DjangoCourseLesson {
  id: number;
  title: string;
  description: string;
  video_url?: string;
  animation_3d_url?: string;
  content_title?: string;
  content_description?: string;
  display_order: number;
  lesson_order: number;
  is_service: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface DjangoTestQuestion {
  id: number;
  question_text: string;
  course_test_id: number;
  question_order?: number;
  points: number;
  question_type: string;
  expected_answer_type?: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class DjDataService {
  private djangoApiUrl = environment.aiApiUrl;

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    // Check if we're in the browser environment before accessing localStorage
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      // Get user info from localStorage or session storage that Angular has
      const userInfo = localStorage.getItem('currentUser');
      if (userInfo) {
        const user = JSON.parse(userInfo);
        // Pass user ID in headers for Django to identify the user
        return new HttpHeaders({
          'Content-Type': 'application/json',
          'X-User-ID': user.id?.toString() || '',
          'X-User-Email': user.email || ''
        });
      }
    }
    
    // If no user info available or not in browser, return basic headers
    // Don't include user-specific headers when no user is logged in
    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  // Get all users from Django
  getAllUsers(): Observable<DjangoUser[]> {
    return this.http.get<DjangoUser[]>(`${this.djangoApiUrl}/users/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get user by ID from Django
  getUserById(id: number): Observable<DjangoUser> {
    return this.http.get<DjangoUser>(`${this.djangoApiUrl}/users/${id}/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get all offers from Django
  getAllOffers(): Observable<DjangoOffer[]> {
    return this.http.get<DjangoOffer[]>(`${this.djangoApiUrl}/offers/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get offer by ID from Django
  getOfferById(id: number): Observable<DjangoOffer> {
    return this.http.get<DjangoOffer>(`${this.djangoApiUrl}/offers/${id}/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get all user offers from Django
  getAllUserOffers(): Observable<DjangoUserOffer[]> {
    return this.http.get<DjangoUserOffer[]>(`${this.djangoApiUrl}/user-offers/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get user offers by user ID from Django
  getUserOffersByUserId(userId: number): Observable<DjangoUserOffer[]> {
    return this.http.get<DjangoUserOffer[]>(`${this.djangoApiUrl}/user-offers/user/${userId}/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get all course lessons from Django
  getAllCourseLessons(): Observable<DjangoCourseLesson[]> {
    return this.http.get<DjangoCourseLesson[]>(`${this.djangoApiUrl}/course-lessons/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get course lesson by ID from Django
  getCourseLessonById(id: number): Observable<DjangoCourseLesson> {
    return this.http.get<DjangoCourseLesson>(`${this.djangoApiUrl}/course-lessons/${id}/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get all test questions from Django
  getAllTestQuestions(): Observable<DjangoTestQuestion[]> {
    return this.http.get<DjangoTestQuestion[]>(`${this.djangoApiUrl}/test-questions/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get test questions by course test ID from Django
  getTestQuestionsByTestId(testId: number): Observable<DjangoTestQuestion[]> {
    return this.http.get<DjangoTestQuestion[]>(`${this.djangoApiUrl}/test-questions/test/${testId}/`, {
      headers: this.getAuthHeaders()
    });
  }

  // Methods for updating approval status (admin functionality)
  approveUserOffer(userOfferId: number): Observable<DjangoUserOffer> {
    return this.http.put<DjangoUserOffer>(`${this.djangoApiUrl}/user-offers/${userOfferId}/approve/`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  rejectUserOffer(userOfferId: number): Observable<DjangoUserOffer> {
    return this.http.put<DjangoUserOffer>(`${this.djangoApiUrl}/user-offers/${userOfferId}/reject/`, {}, {
      headers: this.getAuthHeaders()
    });
  }
}