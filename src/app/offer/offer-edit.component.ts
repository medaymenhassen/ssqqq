import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Offer, OfferService } from '../services/offer.service';

@Component({
  selector: 'app-offer-edit',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './offer-edit.component.html',
  styleUrls: ['./offer-edit.component.scss']
})
export class OfferEditComponent implements OnInit {
  offerForm: FormGroup;
  offer: Offer | null = null;
  offerId: number | null = null;
  isSubmitting = false;
  loading = false;
  error: string | null = null;

  constructor(
    private fb: FormBuilder,
    private offerService: OfferService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.offerForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      price: [0, [Validators.required, Validators.min(0.01)]],
      durationHours: [1, [Validators.required, Validators.min(1)]]
    });
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.offerId = +params['id'];
        this.loadOffer(this.offerId);
      }
    });
  }

  loadOffer(id: number): void {
    this.loading = true;
    this.error = null;
    
    this.offerService.getOfferById(id).subscribe({
      next: (offer) => {
        this.offer = offer;
        this.loading = false;
        // Populate form with offer data
        this.offerForm.patchValue({
          title: offer.title,
          description: offer.description,
          price: offer.price,
          durationHours: offer.durationHours
        });
      },
      error: (err) => {
        console.error('Error loading offer:', err);
        this.error = 'Failed to load offer. Please try again later.';
        this.loading = false;
      }
    });
  }

  onSubmit(): void {
    if (this.offerForm.valid && this.offerId) {
      this.isSubmitting = true;
      this.error = null;
      
      // We need to provide a complete Offer object, but the ID will be ignored in the update
      const offerData: Offer = {
        id: this.offerId!,
        title: this.offerForm.value.title,
        description: this.offerForm.value.description,
        price: this.offerForm.value.price,
        durationHours: this.offerForm.value.durationHours,
        userTypeId: this.offer!.userTypeId,
        isActive: this.offer!.isActive,
        createdAt: this.offer!.createdAt,
        updatedAt: new Date().toISOString()
      };
      
      this.offerService.updateOffer(this.offerId!, offerData).subscribe({
        next: (offer) => {
          console.log('Offer updated successfully:', offer);
          this.isSubmitting = false;
          // Redirect to offers list
          this.router.navigate(['/offers']);
        },
        error: (err) => {
          console.error('Error updating offer:', err);
          this.error = 'Failed to update offer. Please try again later.';
          this.isSubmitting = false;
        }
      });
    } else {
      // Mark all fields as touched to show validation errors
      Object.keys(this.offerForm.controls).forEach(key => {
        const control = this.offerForm.get(key);
        control?.markAsTouched();
      });
    }
  }

  onCancel(): void {
    this.router.navigate(['/offers']);
  }
}