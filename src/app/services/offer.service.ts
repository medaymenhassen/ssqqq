import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, Subject, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface Offer {
  id: number;
  title: string;
  description: string;
  price: number;
  durationHours: number;
  userTypeId: number | null;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface UserOffer {
  id: number;
  userId: number;
  offerId: number;
  purchaseDate: string;
  expirationDate: string;
  isActive: boolean;
  approvalStatus: 'PENDING' | 'APPROVED' | 'REJECTED';
  createdAt: string;
  updatedAt: string;
  // Added for EntityGraph response
  user?: {
    id: number;
    firstname: string;
    lastname: string;
    email: string;
  };
  offer?: {
    id: number;
    title: string;
    description: string;
    price: number;
    durationHours: number;
    userTypeId: number | null;
    isActive: boolean;
    createdAt: string;
    updatedAt: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class OfferService {
  private apiUrl = environment.apiUrl;
  
  // ✅ NOUVEAU: Subject pour broadcaster les changements
  private statusChangeSubject = new Subject<{ offerId: number; status: string }>();
  public statusChange$ = this.statusChangeSubject.asObservable();

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('accessToken');
      if (token) {
        return new HttpHeaders({
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        });
      }
    }
    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  getAllActiveOffers(): Observable<Offer[]> {
    return this.http.get<Offer[]>(`${this.apiUrl}/offers`, {
      headers: this.getAuthHeaders()
    });
  }

  getOfferById(id: number): Observable<Offer> {
    return this.http.get<Offer>(`${this.apiUrl}/offers/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  // ✅ CORRIGÉ: Émet le changement de statut immédiatement
  purchaseOffer(offerId: number): Observable<UserOffer> {
    return new Observable(observer => {
      this.http.post<UserOffer>(`${this.apiUrl}/offers/${offerId}/purchase`, {}, {
        headers: this.getAuthHeaders()
      }).subscribe({
        next: (userOffer) => {
          // Broadcaster le changement IMMÉDIATEMENT
          // Assurer que l'offerId est défini même si la réponse API ne le contient pas
          const actualOfferId = userOffer.offerId || offerId;
          this.statusChangeSubject.next({
            offerId: actualOfferId,
            status: userOffer.approvalStatus || 'PENDING'
          });
          console.log('✅ Purchase successful:', userOffer.approvalStatus);
          observer.next(userOffer);
          observer.complete();
        },
        error: (error) => {
          observer.error(error);
        }
      });
    });
  }

  getUserPendingOffers(userId: number): Observable<UserOffer[]> {
    return this.http.get<UserOffer[]>(`${this.apiUrl}/offers/user/${userId}/pending`, {
      headers: this.getAuthHeaders()
    });
  }

  getUserApprovedOffers(userId: number): Observable<UserOffer[]> {
    return this.http.get<UserOffer[]>(`${this.apiUrl}/offers/user/${userId}/approved`, {
      headers: this.getAuthHeaders()
    });
  }

  getUserRejectedOffers(userId: number): Observable<UserOffer[]> {
    return this.http.get<UserOffer[]>(`${this.apiUrl}/offers/user/${userId}/rejected`, {
      headers: this.getAuthHeaders()
    });
  }

  getUserPurchasedOffers(userId: number): Observable<UserOffer[]> {
    return this.http.get<UserOffer[]>(`${this.apiUrl}/offers/user/${userId}/purchases`, {
      headers: this.getAuthHeaders()
    }).pipe(
      catchError((error) => {
        if (error.status === 400) {
          console.warn(`User ${userId} has no purchased offers or request failed`);
          return of([]); // Return empty array instead of throwing error
        }
        console.error('Error getting user purchased offers:', error);
        throw error; // Re-throw other errors
      })
    );
  }

  // Method to get all pending offers for admin approval
  getAllPendingOffers(): Observable<UserOffer[]> {
    return this.http.get<UserOffer[]>(`${this.apiUrl}/offers/admin/pending`, {
      headers: this.getAuthHeaders()
    });
  }

  approveOffer(userOfferId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/offers/${userOfferId}/approve`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  rejectOffer(userOfferId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/offers/${userOfferId}/reject`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  createOffer(offer: Offer): Observable<Offer> {
    return this.http.post<Offer>(`${this.apiUrl}/offers`, offer, {
      headers: this.getAuthHeaders()
    });
  }

  updateOffer(id: number, offer: Offer): Observable<Offer> {
    return this.http.put<Offer>(`${this.apiUrl}/offers/${id}`, offer, {
      headers: this.getAuthHeaders()
    });
  }

  deleteOffer(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/offers/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  userHasAccess(userId: number): Observable<boolean> {
    return this.http.get<boolean>(`${this.apiUrl}/offers/user/${userId}/access`, {
      headers: this.getAuthHeaders()
    });
  }

  trackLessonTime(userId: number, lessonId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/offers/user/${userId}/track-lesson/${lessonId}`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  getUserRemainingTime(userId: number): Observable<{remainingMinutes: number}> {
    return this.http.get<{remainingMinutes: number}>(`${this.apiUrl}/offers/user/${userId}/remaining-time`, {
      headers: this.getAuthHeaders()
    });
  }
}
