import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
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
  createdAt: string;
  updatedAt: string;
}

@Injectable({
  providedIn: 'root'
})
export class OfferService {
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

  // Get all active offers
  getAllActiveOffers(): Observable<Offer[]> {
    return this.http.get<Offer[]>(`${this.apiUrl}/offers`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get offer by ID
  getOfferById(id: number): Observable<Offer> {
    return this.http.get<Offer>(`${this.apiUrl}/offers/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  // Create a new offer (admin only)
  createOffer(offer: Offer): Observable<Offer> {
    return this.http.post<Offer>(`${this.apiUrl}/offers`, offer, {
      headers: this.getAuthHeaders()
    });
  }

  // Update an offer (admin only)
  updateOffer(id: number, offer: Offer): Observable<Offer> {
    return this.http.put<Offer>(`${this.apiUrl}/offers/${id}`, offer, {
      headers: this.getAuthHeaders()
    });
  }

  // Delete an offer (admin only)
  deleteOffer(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/offers/${id}`, {
      headers: this.getAuthHeaders()
    });
  }

  // Purchase an offer
  purchaseOffer(offerId: number, userId: number): Observable<UserOffer> {
    return this.http.post<UserOffer>(`${this.apiUrl}/offers/${offerId}/purchase?userId=${userId}`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  // Check if user has access to content
  userHasAccess(userId: number): Observable<boolean> {
    return this.http.get<boolean>(`${this.apiUrl}/offers/user/${userId}/access`, {
      headers: this.getAuthHeaders()
    });
  }

  // Get user's purchased offers
  getUserPurchasedOffers(userId: number): Observable<UserOffer[]> {
    return this.http.get<UserOffer[]>(`${this.apiUrl}/offers/user/${userId}/purchases`, {
      headers: this.getAuthHeaders()
    });
  }
}