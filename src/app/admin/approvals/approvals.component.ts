import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../auth.service';
import { OfferService } from '../../services/offer.service';

interface UserOffer {
  id: number;
  userId: number;
  offerId: number;
  approvalStatus: string; // PENDING, APPROVED, REJECTED
  purchaseDate: string;
  expirationDate: string;
  createdAt: string;
  updatedAt: string;
  user: {
    id: number;
    firstname: string;
    lastname: string;
    email: string;
  };
  offer: {
    id: number;
    title: string;
    description: string;
    price: number;
  };
}

@Component({
  selector: 'app-approvals',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './approvals.component.html',
  styleUrls: ['./approvals.component.scss']
})
export class ApprovalsComponent implements OnInit {
  userOffers: UserOffer[] = [];
  pendingApprovals: UserOffer[] = [];
  loading = true;
  error: string | null = null;

  constructor(
    private authService: AuthService,
    private offerService: OfferService
  ) {}

  ngOnInit(): void {
    if (this.authService.getCurrentUser()?.role === 'ADMIN') {
      this.loadPendingApprovals();
    } else {
      // If not admin, redirect to course lessons page
      window.location.href = '/course-lessons';
    }
  }

  loadPendingApprovals(): void {
    // Get all user offers to see pending approvals
    // We'll need to create a method in the service to get all user offers for admin
    // For now, we'll get user offers for the admin user
    const adminId = this.authService.getCurrentUser()?.id;
    if (adminId) {
      this.offerService.getUserPurchasedOffers(adminId).subscribe({
        next: (data: any[]) => {
          this.userOffers = data as UserOffer[];
          this.pendingApprovals = data.filter((offer: any) => offer.approvalStatus === 'PENDING') as UserOffer[];
          this.loading = false;
        },
        error: (error: any) => {
          this.error = 'Failed to load pending approvals';
          this.loading = false;
          console.error('Error loading pending approvals:', error);
        }
      });
    }
  }

  approveOffer(userOfferId: number): void {
    this.offerService.approveOffer(userOfferId).subscribe({
      next: () => {
        this.loadPendingApprovals(); // Refresh the list
      },
      error: (error: any) => {
        console.error('Error approving offer:', error);
      }
    });
  }

  rejectOffer(userOfferId: number): void {
    this.offerService.rejectOffer(userOfferId).subscribe({
      next: () => {
        this.loadPendingApprovals(); // Refresh the list
      },
      error: (error: any) => {
        console.error('Error rejecting offer:', error);
      }
    });
  }
}