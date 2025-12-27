import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { TestService, CourseLesson } from '../services/test.service';
import { Offer, OfferService } from '../services/offer.service';
import { AuthService, User } from '../auth.service';
import { forkJoin, of, Subject } from 'rxjs';
import { catchError, takeUntil, filter } from 'rxjs/operators';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.scss']
})
export class LandingComponent implements OnInit, OnDestroy {
  offers: Offer[] = [];
  lessons: CourseLesson[] = [];
  currentUser: User | null = null;
  isAuthenticated: boolean = false;
  userId: number | null = null;
  userOfferStatuses: Map<number, string> = new Map();
  userOffers: any[] = [];
  userOffersLoading = false;

  private destroy$ = new Subject<void>();
  private refreshIntervals: number[] = [];

  constructor(
    private offerService: OfferService,
    private testService: TestService,
    private authService: AuthService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadCurrentUser();
    this.loadLessons();

    // ✅ NOUVEAU: Subscribe aux changements de statut
    this.offerService.statusChange$
      .pipe(takeUntil(this.destroy$))
      .subscribe(({ offerId, status }) => {
        if (offerId) {  // Vérifier que l'offerId n'est pas undefined
          console.log(`✅ Status changed: ${offerId} -> ${status}`);
          this.userOfferStatuses.set(offerId, status);
          
          // Forcer le rafraîchissement de l'interface
          // Instead of calling loadOffers(), just refresh statuses to avoid interference
          if (this.userId) {
            this.checkUserOfferStatuses();
          }
        } else {
          console.log('⚠️ Status change with undefined offerId:', status);
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.refreshIntervals.forEach(interval => clearInterval(interval));
  }

  loadOffers(): void {
    this.offerService.getAllActiveOffers().subscribe({
      next: (offers) => {
        this.offers = offers;
        console.log('📋 Loaded offers:', offers.map(o => ({id: o.id, title: o.title})), 'Current userId:', this.userId);
        console.log('📊 Current userOfferStatuses before refresh:', this.userOfferStatuses);
        
        // If we have a valid userId, refresh statuses
        if (this.userId) {
          // Définir un délai pour éviter les appels répétitifs
          setTimeout(() => {
            if (this.userId) {
              this.checkUserOfferStatuses();
              this.loadUserOffers();
            }
          }, 100);
        } else {
          // If user is not logged in, clear the statuses
          this.userOfferStatuses.clear();
          console.log('🧹 Cleared statuses - user not logged in');
        }
      },
      error: (error) => {
        console.error('Error loading offers:', error);
        this.offers = [];
      }
    });
  }

  private checkUserOfferStatuses(): void {
    if (!this.userId) {
      console.log('No user ID available, skipping status check');
      return;
    }

    this.userOfferStatuses.clear();
    
    console.log(`📡 Loading statuses for user: ${this.userId}`);
    
    forkJoin({
      pending: this.offerService.getUserPendingOffers(this.userId).pipe(catchError((error) => {
        console.error('Error loading pending offers:', error);
        console.log('Pending offers error details:', error.message || error);
        return of([]);
      })),
      approved: this.offerService.getUserApprovedOffers(this.userId).pipe(catchError((error) => {
        console.error('Error loading approved offers:', error);
        console.log('Approved offers error details:', error.message || error);
        return of([]);
      })),
      rejected: this.offerService.getUserRejectedOffers(this.userId).pipe(catchError((error) => {
        console.error('Error loading rejected offers:', error);
        console.log('Rejected offers error details:', error.message || error);
        return of([]);
      })),
      purchased: this.offerService.getUserPurchasedOffers(this.userId).pipe(catchError((error) => {
        console.error('Error loading purchased offers:', error);
        console.log('Purchased offers error details:', error.message || error);
        // Log more specific error information
        if (error.status === 400) {
          console.warn('Bad request for user purchased offers - user may have no purchased offers');
        } else if (error.status === 401 || error.status === 403) {
          console.warn('Unauthorized access - token may have expired');
        }
        return of([]);
      }))
    }).subscribe({
      next: (results) => {
        console.log('📊 Raw results:', {
          pending: results.pending.length,
          approved: results.approved.length,
          rejected: results.rejected.length,
          purchased: results.purchased.length
        });
        
        // Log the actual content of the results to see the structure
        console.log('📝 Raw pending offers:', results.pending);
        console.log('📝 Raw approved offers:', results.approved);
        console.log('📝 Raw rejected offers:', results.rejected);
        console.log('📝 Raw purchased offers:', results.purchased);
        
        // Create a temporary map to store new statuses
        const newStatuses = new Map<number, string>();
        
        // First, add pending, approved, and rejected offers with priority
        console.log('🔍 Processing pending, approved, and rejected offers...');
        [...results.pending, ...results.approved, ...results.rejected].forEach((userOffer, index) => {
          console.log(`🔍 Processing userOffer ${index}:`, userOffer);
          // Handle both structures: direct offerId or nested offer.id
          const offerId = userOffer.offerId || (userOffer.offer && userOffer.offer.id);
          if (userOffer && offerId !== undefined && offerId !== null) {
            console.log(`📝 Setting status for offer ${offerId}: ${userOffer.approvalStatus}`);
            newStatuses.set(offerId, userOffer.approvalStatus);
          } else {
            console.log(`⚠️ Missing offerId or userOffer at index ${index}:`, userOffer);
          }
        });
        
        // Then, for purchased offers that might not be in the above lists,
        // set their status based on isActive and expiration
        console.log('🔍 Processing purchased offers...');
        results.purchased.forEach((userOffer, index) => {
          console.log(`🔍 Processing purchased userOffer ${index}:`, userOffer);
          // Handle both structures: direct offerId or nested offer.id
          const offerId = userOffer.offerId || (userOffer.offer && userOffer.offer.id);
          if (userOffer && offerId !== undefined && offerId !== null) {
            // Only set status if not already set from specific status lists
            if (!newStatuses.has(offerId)) {
              // If offer has approval status, use that; otherwise determine from active status
              if (userOffer.approvalStatus) {
                console.log(`📝 Setting status for purchased offer ${offerId}: ${userOffer.approvalStatus}`);
                newStatuses.set(offerId, userOffer.approvalStatus);
              } else {
                // Default to APPROVED if active and not expired
                const status = userOffer.isActive ? 'APPROVED' : 'REJECTED';
                console.log(`📝 Setting status for purchased offer ${offerId}: ${status}`);
                newStatuses.set(offerId, status);
              }
            } else {
              console.log(`📝 Purchased offer ${offerId} already has status, skipping`);
            }
          } else {
            console.log(`⚠️ Missing offerId or userOffer in purchased at index ${index}:`, userOffer);
          }
        });
        
        // Update the main map with new statuses
        this.userOfferStatuses = newStatuses;
        
        console.log('✅ Final statuses loaded:', this.userOfferStatuses);
        console.log(`📊 Total statuses: ${this.userOfferStatuses.size}`);
      },
      error: (err) => {
        console.error('❌ Error loading statuses:', err);
        // Ensure the map is initialized even if there's an error
        this.userOfferStatuses = new Map<number, string>();
      }
    });
  }

  loadLessons(): void {
    this.testService.getAllCourseLessons().subscribe({
      next: (lessons) => this.lessons = lessons,
      error: (error) => {
        console.error('Error loading lessons:', error);
        this.lessons = [];
      }
    });
  }

  purchaseOffer(offerId: number): void {
    if (this.isButtonDisabled(offerId)) {
      alert(`This offer is ${this.getOfferStatus(offerId).toLowerCase()}. Cannot purchase again.`);
      return;
    }

    this.authService.checkAndLoadUser();
    const currentUser = this.authService.getCurrentUser();

    setTimeout(() => {
      if (!this.authService.isLoggedIn() || !currentUser?.id) {
        alert('You must be logged in.');
        window.location.href = '/login';
        return;
      }

      this.userId = currentUser.id;

      this.offerService.purchaseOffer(offerId).subscribe({
        next: (userOffer) => {
          // ✅ IMMÉDIAT: Mettre à jour le cache avec le statut approprié
          const status = userOffer.approvalStatus || 'PENDING';
          this.userOfferStatuses.set(offerId, status);

          if (status === 'APPROVED') {
            alert('✅ Offer approved! You have access now.');
          } else {
            alert('✅ Offer purchased! Waiting for admin approval.');
          }

          // ✅ RAFRAÎCHIR IMMÉDIATEMENT les offres pour mettre à jour l'interface
          
          // ✅ DÉLAIS: Rafraîchir après le serveur
          setTimeout(() => {
            if (this.userId) {
              this.checkUserOfferStatuses();
              this.loadUserOffers();
            }
          }, 500);

          setTimeout(() => {
            if (this.userId) {
              this.checkUserOfferStatuses();
            }
          }, 2000);
        },
        error: (err) => {
          console.error('Error purchasing:', err);
          if (err.status === 401 || err.status === 403) {
            alert('You must be logged in.');
            this.authService.logout();
            window.location.href = '/login';
          } else {
            alert('Failed to purchase offer.');
          }
        }
      });
    }, 200);
  }

  startLesson(lessonId: number): void {
    window.location.href = `/course-lessons/${lessonId}`;
  }

  startJourney(): void {
    window.location.href = '/dashboard';
  }

  private loadCurrentUser(): void {
    // First, trigger a check to load the user if not already loaded
    this.authService.checkAndLoadUser();
    
    // Subscribe to user changes
    this.authService.currentUser
      .pipe(
        takeUntil(this.destroy$),
        // Filter to only process when user has valid ID
        filter(user => user !== undefined && user !== null)
      )
      .subscribe(user => {
        this.currentUser = user;
        this.isAuthenticated = !!user?.id;
        if (user?.id) {
          this.userId = user.id;
          console.log(`👤 User loaded with ID: ${this.userId}`);
          // Only load offers after user ID is properly set
          this.loadOffers();
          this.loadUserOffers();
          // Charger les statuts des offres utilisateur
          this.checkUserOfferStatuses();
        } else {
          this.userId = null;
          this.userOfferStatuses.clear();
          this.userOffers = [];
          console.log('👤 User not logged in, loading offers without status checking');
          // User is not logged in, still load offers but without status checking
          this.loadOffers();
        }
      });
  }

  private loadUserOffers(): void {
    if (!this.userId) return;
    this.userOffersLoading = true;

    forkJoin({
      pending: this.offerService.getUserPendingOffers(this.userId).pipe(catchError(() => of([]))),
      approved: this.offerService.getUserApprovedOffers(this.userId).pipe(catchError(() => of([]))),
      rejected: this.offerService.getUserRejectedOffers(this.userId).pipe(catchError(() => of([]))),
      purchased: this.offerService.getUserPurchasedOffers(this.userId).pipe(catchError((error) => {
        console.error('Error loading purchased offers in loadUserOffers:', error);
        if (error.status === 400) {
          console.warn('Bad request for user purchased offers - user may have no purchased offers');
        } else if (error.status === 401 || error.status === 403) {
          console.warn('Unauthorized access - token may have expired');
        }
        return of([]);
      }))
    }).subscribe({
      next: (results) => {
        this.userOffers = [...results.pending, ...results.approved, ...results.rejected, ...results.purchased];
        this.userOffersLoading = false;
      },
      error: (error) => {
        console.error('Error loading user offers:', error);
        this.userOffersLoading = false;
      }
    });
  }

  getOfferStatus(offerId: number): string {
    if (!this.userId) {
      return 'AVAILABLE'; // If not logged in, all offers are available
    }
    return this.userOfferStatuses.get(offerId) || 'AVAILABLE';
  }

  getButtonText(offerId: number): string {
    const status = this.getOfferStatus(offerId);
    const texts: {[key: string]: string} = {
      'PENDING': '⏳ Pending Approval',
      'APPROVED': '✅ Access Granted',
      'REJECTED': '❌ Offer Rejected',
      'AVAILABLE': 'Acheter'
    };
    return texts[status] || 'Acheter';
  }

  isButtonDisabled(offerId: number): boolean {
    const status = this.getOfferStatus(offerId);
    return ['PENDING', 'APPROVED', 'REJECTED'].includes(status);
  }

  getStatusClass(status: string): string {
    const classes: {[key: string]: string} = {
      'PENDING': 'status-pending',
      'APPROVED': 'status-approved',
      'REJECTED': 'status-rejected'
    };
    return classes[status] || 'status-default';
  }

  goToLessons(): void {
    this.router.navigate(['/course-lessons']);
  }
}
