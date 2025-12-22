import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Offer, OfferService } from '../services/offer.service';
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
      },
      error: (err) => {
        console.error('Error loading offers:', err);
        this.error = 'Failed to load offers. Please try again later.';
        this.loading = false;
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
        alert('Offer purchased successfully! You now have access to course content.');
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
}