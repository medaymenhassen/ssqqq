import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Offer, OfferService, UserOffer } from '../services/offer.service';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-offer-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './offer-list.component.html',
  styleUrls: ['./offer-list.component.css']
})
export class OfferListComponent implements OnInit {
  offers: Offer[] = [];
  loading = false;
  error: string | null = null;
  isPurchasing = false;
  userId: number | null = null;
  userOfferStatuses: Map<number, string> = new Map(); // Maps offerId to status (PURCHASED, PENDING, APPROVED, REJECTED)

  constructor(
    private offerService: OfferService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadCurrentUser();
    this.loadOffers();
  }

  private loadCurrentUser(): void {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.userId = currentUser.id;
    }
  }

  private loadOffers(): void {
    this.loading = true;
    this.error = null;
    
    this.offerService.getAllActiveOffers().subscribe({
      next: (offers) => {
        this.offers = offers;
        this.loading = false;
        
        // If user is logged in, check their offer statuses
        if (this.userId) {
          this.checkUserOfferStatuses();
        }
      },
      error: (err) => {
        console.error('Error loading offers:', err);
        this.error = 'Failed to load offers. Please try again later.';
        this.loading = false;
      }
    });
  }
  
  private checkUserOfferStatuses(): void {
    // Get all user's offer statuses (pending, approved, rejected)
    this.offerService.getUserPendingOffers(this.userId!).subscribe({
      next: (pendingOffers) => {
        pendingOffers.forEach(userOffer => {
          this.userOfferStatuses.set(userOffer.offerId, userOffer.approvalStatus);
        });
        
        // Get approved offers
        this.offerService.getUserApprovedOffers(this.userId!).subscribe({
          next: (approvedOffers) => {
            approvedOffers.forEach(userOffer => {
              this.userOfferStatuses.set(userOffer.offerId, userOffer.approvalStatus);
            });
            
            // Get rejected offers
            this.offerService.getUserRejectedOffers(this.userId!).subscribe({
              next: (rejectedOffers) => {
                rejectedOffers.forEach(userOffer => {
                  this.userOfferStatuses.set(userOffer.offerId, userOffer.approvalStatus);
                });
              },
              error: (err) => {
                console.error('Error loading rejected offers:', err);
              }
            });
          },
          error: (err) => {
            console.error('Error loading approved offers:', err);
          }
        });
      },
      error: (err) => {
        console.error('Error loading pending offers:', err);
      }
    });
  }

  purchaseOffer(offerId: number): void {
    if (!this.userId) {
      this.error = 'You must be logged in to purchase offers.';
      return;
    }
    
    this.isPurchasing = true;
    this.error = null;
    
    this.offerService.purchaseOffer(offerId, this.userId).subscribe({
      next: (userOffer) => {
        console.log('Offer purchased successfully:', userOffer);
        this.isPurchasing = false;
        
        // Update the status for this offer
        this.userOfferStatuses.set(offerId, userOffer.approvalStatus || 'PENDING');
        
        if (userOffer.approvalStatus === 'APPROVED') {
          alert('Offer purchased and approved! You now have access to course content.');
        } else {
          alert('Offer purchased successfully! Admin approval is pending. You will get access after approval.');
        }
        
        // Reload offers to reflect the purchase
        this.loadOffers();
      },
      error: (err) => {
        console.error('Error purchasing offer:', err);
        this.error = 'Failed to purchase offer. ' + (err.error?.message || 'Please try again later.');
        this.isPurchasing = false;
      }
    });
  }

  // CRUD Operations
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
          // Reload offers after deletion
          this.loadOffers();
        },
        error: (err) => {
          console.error('Error deleting offer:', err);
          this.error = 'Failed to delete offer. Please try again later.';
        }
      });
    }
  }
  
  getOfferStatus(offerId: number): string {
    return this.userOfferStatuses.get(offerId) || 'AVAILABLE';
  }
  
  getButtonText(offerId: number): string {
    const status = this.getOfferStatus(offerId);
    
    switch(status) {
      case 'PENDING':
        return 'Pending Approval';
      case 'APPROVED':
        return 'Access Granted';
      case 'REJECTED':
        return 'Offer Rejected';
      default:
        return 'Purchase';
    }
  }
  
  isButtonDisabled(offerId: number): boolean {
    const status = this.getOfferStatus(offerId);
    return status === 'PENDING' || status === 'APPROVED' || status === 'REJECTED';
  }
  
  getButtonClass(offerId: number): string {
    const status = this.getOfferStatus(offerId);
    
    switch(status) {
      case 'PENDING':
        return 'btn btn-warning';
      case 'APPROVED':
        return 'btn btn-success';
      case 'REJECTED':
        return 'btn btn-danger';
      default:
        return 'btn btn-primary';
    }
  }
}