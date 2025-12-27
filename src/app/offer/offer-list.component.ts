import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Offer, OfferService, UserOffer } from '../services/offer.service';
import { AuthService } from '../auth.service';
import { forkJoin, of, Subject } from 'rxjs';
import { catchError, takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-offer-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './offer-list.component.html',
  styleUrls: ['./offer-list.component.css']
})
export class OfferListComponent implements OnInit, OnDestroy {
  offers: Offer[] = [];
  loading = false;
  error: string | null = null;
  isPurchasing = false;
  userId: number | null = null;
  userOfferStatuses: Map<number, string> = new Map();
  userOffers: UserOffer[] = [];
  userOffersLoading = false;

  private destroy$ = new Subject<void>();

  constructor(
    private offerService: OfferService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // ✅ DEBUG: Vérifier le token
    const token = localStorage.getItem('accessToken');
    const user = this.authService.getCurrentUser();
    console.log('🔍 DEBUG:', {
      token: token ? token.substring(0, 20) + '...' : 'NO TOKEN',
      userId: user?.id,
      email: user?.email
    });

    this.loadCurrentUser();

    setTimeout(() => {
      this.loadOffers();
      setTimeout(() => {
        if (this.userId) this.checkUserOfferStatuses();
      }, 1000);
    }, 500);

    // ✅ NOUVEAU: Subscribe aux changements
    this.offerService.statusChange$
      .pipe(takeUntil(this.destroy$))
      .subscribe(({ offerId, status }) => {
        console.log(`✅ Status changed: ${offerId} -> ${status}`);
        this.userOfferStatuses.set(offerId, status);
      });

    setInterval(() => {
      if (this.userId) this.checkUserOfferStatuses();
    }, 30000);

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden && this.userId) {
        setTimeout(() => this.checkUserOfferStatuses(), 1000);
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadCurrentUser(): void {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser?.id) {
      this.userId = currentUser.id;
      setTimeout(() => {
        if (this.userId) {
          this.checkUserOfferStatuses();
          this.loadUserOffers();
        }
      }, 100);
    }

    if (!this.authService.isLoggedIn()) {
      this.authService.checkAndLoadUser();
    }

    this.authService.currentUser
      .pipe(takeUntil(this.destroy$))
      .subscribe(user => {
        if (user?.id) {
          this.userId = user.id;
          setTimeout(() => {
            if (this.userId) {
              this.checkUserOfferStatuses();
              this.loadUserOffers();
            }
          }, 100);
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
      purchased: this.offerService.getUserPurchasedOffers(this.userId).pipe(catchError(() => of([])))
    }).subscribe({
      next: (results) => {
        this.userOffers = [...results.pending, ...results.approved, ...results.rejected, ...results.purchased];
        this.userOffersLoading = false;
      },
      error: (error) => {
        console.error('Error:', error);
        this.userOffersLoading = false;
      }
    });
  }

  private loadOffers(): void {
    this.loading = true;
    this.error = null;
    this.offerService.getAllActiveOffers().subscribe({
      next: (offers) => {
        this.offers = offers;
        this.loading = false;
        if (this.userId) {
          this.checkUserOfferStatuses();
          this.loadUserOffers();
        }
      },
      error: (err) => {
        console.error('Error:', err);
        this.error = 'Failed to load offers.';
        this.loading = false;
      }
    });
  }

  private checkUserOfferStatuses(): void {
    if (!this.userId) {
      console.error('❌ userId is null!');
      return;
    }

    console.log(`📡 Fetching offers for userId: ${this.userId}`);

    const newStatuses = new Map();

    forkJoin({
      pending: this.offerService.getUserPendingOffers(this.userId).pipe(
        catchError(err => {
          console.error('❌ Error pending:', err);
          return of([]);
        })
      ),
      approved: this.offerService.getUserApprovedOffers(this.userId).pipe(
        catchError(err => {
          console.error('❌ Error approved:', err);
          return of([]);
        })
      ),
      rejected: this.offerService.getUserRejectedOffers(this.userId).pipe(
        catchError(err => {
          console.error('❌ Error rejected:', err);
          return of([]);
        })
      ),
      purchased: this.offerService.getUserPurchasedOffers(this.userId).pipe(
        catchError(err => {
          console.error('❌ Error purchased:', err);
          return of([]);
        })
      )
    }).subscribe({
      next: (results) => {
        console.log('✅ Offers loaded:', results);
        [...results.pending, ...results.approved, ...results.rejected].forEach(userOffer => {
          if (userOffer?.offerId) {
            newStatuses.set(userOffer.offerId, userOffer.approvalStatus);
          }
        });

        results.purchased.forEach(userOffer => {
          if (userOffer?.offerId && !newStatuses.has(userOffer.offerId)) {
            newStatuses.set(userOffer.offerId, userOffer.approvalStatus || (userOffer.isActive ? 'APPROVED' : 'REJECTED'));
          }
        });

        this.userOfferStatuses = newStatuses;
      },
      error: (err) => console.error('❌ Error:', err)
    });
  }

  purchaseOffer(offerId: number): void {
    if (this.isButtonDisabled(offerId)) {
      this.error = `Cannot purchase. Status: ${this.getOfferStatus(offerId).toLowerCase()}`;
      return;
    }

    this.authService.checkAndLoadUser();
    const currentUser = this.authService.getCurrentUser();

    setTimeout(() => {
      if (!this.authService.isLoggedIn() || !currentUser?.id) {
        this.error = 'You must be logged in.';
        this.router.navigate(['/login']);
        return;
      }

      this.userId = currentUser.id;
      this.isPurchasing = true;
      this.error = null;

      this.offerService.purchaseOffer(offerId).subscribe({
        next: (userOffer) => {
          this.isPurchasing = false;

          // ✅ IMMÉDIAT: Mettre à jour
          this.userOfferStatuses.set(offerId, userOffer.approvalStatus || 'PENDING');

          if (userOffer.approvalStatus === 'APPROVED') {
            alert('✅ Offer approved! You have access.');
          } else {
            alert('✅ Offer purchased! Waiting for admin approval.');
          }

          // ✅ DÉLAIS: Rafraîchir
          setTimeout(() => {
            if (this.userId) {
              this.checkUserOfferStatuses();
              this.loadUserOffers();
            }
          }, 500);

          setTimeout(() => {
            if (this.userId) {
              this.checkUserOfferStatuses();
              this.loadUserOffers();
            }
          }, 3000);
        },
        error: (err) => {
          console.error('Error:', err);
          this.isPurchasing = false;
          if (err.status === 401 || err.status === 403) {
            this.error = 'You must be logged in.';
            this.authService.forceReloadUser();
            setTimeout(() => this.router.navigate(['/login']), 1000);
          } else {
            this.error = 'Failed to purchase offer.';
          }
        }
      });
    }, 200);
  }

  getOfferStatus(offerId: number): string {
    if (!this.userId) return 'LOADING';
    return this.userOfferStatuses.get(offerId) || 'AVAILABLE';
  }

  getButtonText(offerId: number): string {
    const status = this.getOfferStatus(offerId);
    const texts: {[key: string]: string} = {
      'LOADING': 'Loading...',
      'PENDING': '⏳ Pending Approval',
      'APPROVED': '✅ Access Granted',
      'REJECTED': '❌ Offer Rejected'
    };
    return texts[status] || 'Purchase';
  }

  isButtonDisabled(offerId: number): boolean {
    const status = this.getOfferStatus(offerId);
    return status === 'LOADING' || ['PENDING', 'APPROVED', 'REJECTED'].includes(status);
  }

  getButtonClass(offerId: number): string {
    const status = this.getOfferStatus(offerId);
    const classes: {[key: string]: string} = {
      'LOADING': 'btn btn-secondary',
      'PENDING': 'btn btn-warning',
      'APPROVED': 'btn btn-success',
      'REJECTED': 'btn btn-danger'
    };
    return classes[status] || 'btn btn-primary';
  }

  forceRefresh(): void {
    // Refresh user authentication state first
    this.authService.forceReloadUser();
    
    // Small delay to ensure user is reloaded
    setTimeout(() => {
      this.loadCurrentUser();
      
      setTimeout(() => {
        if (this.userId) {
          // Reload offers and statuses
          this.loadOffers();
          
          setTimeout(() => {
            if (this.userId) {
              this.checkUserOfferStatuses();
              this.loadUserOffers(); // Reload user's offers
            }
          }, 500);
        }
      }, 500);
    }, 500);
  }
  
  goToLessons(): void {
    this.router.navigate(['/course-lessons']);
  }
  
  // Missing methods that are referenced in the template
  createOffer(): void {
    this.router.navigate(['/offers/create']);
  }

  editOffer(offerId: number): void {
    this.router.navigate(['/offers/edit', offerId]);
  }

  deleteOffer(offerId: number): void {
    if (confirm('Are you sure you want to delete this offer?')) {
      this.offerService.deleteOffer(offerId).subscribe({
        next: () => {
          console.log('Offer deleted successfully');
          this.loadOffers();
        },
        error: (err) => {
          console.error('Error deleting offer:', err);
          this.error = 'Failed to delete offer. Please try again later.';
        }
      });
    }
  }
  
  getStatusClass(status: string): string {
    const classes: {[key: string]: string} = {
      'PENDING': 'status-pending',
      'APPROVED': 'status-approved', 
      'REJECTED': 'status-rejected'
    };
    return classes[status] || 'status-default';
  }
}
