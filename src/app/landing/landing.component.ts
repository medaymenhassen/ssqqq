import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { TestService, CourseLesson } from '../services/test.service';
import { Offer, OfferService } from '../services/offer.service';


@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.scss']
})
export class LandingComponent implements OnInit {
  offers: Offer[] = [];
  lessons: CourseLesson[] = [];

  constructor(
    private offerService: OfferService, 
    private testService: TestService
  ) { }

  ngOnInit(): void {
    this.loadOffers();
    this.loadLessons();
  }

  loadOffers(): void {
    // Load offers from the API
    this.offerService.getAllActiveOffers().subscribe({
      next: (offers) => {
        this.offers = offers;
      },
      error: (error) => {
        // Set to empty array if API fails
        this.offers = [];
      }
    });
  }

  loadLessons(): void {
    // Load lessons from the API
    this.testService.getAllCourseLessons().subscribe({
      next: (lessons) => {
        this.lessons = lessons;
      },
      error: (error) => {
        // Set to empty array if API fails
        this.lessons = [];
      }
    });
  }

  purchaseOffer(offerId: number): void {
    // Get current user from localStorage since AuthService is not available
    let currentUser = null;
    
    // Safely get token from localStorage
    const token = this.getToken();
    
    if (token) {
      // Extract user info from token (simplified approach)
      try {
        // Decode JWT token
        const parts = token.split('.');
        if (parts.length === 3) {
          const payload = parts[1];
          const decodedPayload = atob(payload);
          const user = JSON.parse(decodedPayload);
          // Try to get user ID from different possible fields
          // Prioritize numeric IDs over email addresses
          let userId = null;
          if (user.id && !isNaN(user.id)) {
            userId = user.id;
          } else if (user.userId && !isNaN(user.userId)) {
            userId = user.userId;
          } else if (user.user_id && !isNaN(user.user_id)) {
            userId = user.user_id;
          } else if (user.sub && !isNaN(user.sub)) {
            // Only use sub if it's numeric (not an email)
            userId = user.sub;
          }
          
          if (userId !== null) {
            currentUser = { id: +userId, email: user.sub, role: user.role };
          }
        }
      } catch (e) {
        console.error('Error decoding token:', e);
      }
    }
    
    if (!currentUser) {
      alert('You must be logged in to purchase an offer.');
      // Navigate to login using window.location
      window.location.href = '/login';
      return;
    }
    
    // Call the purchase API
    this.offerService.purchaseOffer(offerId, currentUser.id).subscribe({
      next: (userOffer) => {
        console.log('Offer purchased successfully:', userOffer);
        
        if (userOffer.approvalStatus === 'APPROVED') {
          alert('Offer purchased and approved! You now have access to course content.');
        } else {
          alert('Offer purchased successfully! Admin approval is pending. You will get access after approval.');
        }
        
        // Optionally reload offers to reflect status changes
        this.loadOffers();
      },
      error: (err) => {
        console.error('Error purchasing offer:', err);
        alert('Failed to purchase offer. ' + (err.error?.message || 'Please try again later.'));
      }
    });
  }

  startLesson(lessonId: number): void {
    // Navigate to the lesson page without authentication check
    // Navigate to the lesson detail page using window.location
    window.location.href = `/course-lessons/${lessonId}`;
  }

  startJourney(): void {
    // Navigate to the dashboard or onboarding using window.location
    window.location.href = '/dashboard';
  }
  
  private getToken(): string | null {
    if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
      try {
        return localStorage.getItem('accessToken');
      } catch (e) {
        // Handle case where localStorage is not available
        return null;
      }
    }
    return null;
  }
}