import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Offer, OfferService } from '../services/offer.service';

@Component({
  selector: 'app-offer-create',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './offer-create.component.html',
  styleUrls: ['./offer-create.component.scss']
})
export class OfferCreateComponent {
  offerForm: FormGroup;
  isSubmitting = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private offerService: OfferService,
    private router: Router
  ) {
    this.offerForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      price: [0, [Validators.required, Validators.min(0.01)]],
      durationHours: [1, [Validators.required, Validators.min(1)]]
    });
  }

  onSubmit(): void {
    if (this.offerForm.valid) {
      this.isSubmitting = true;
      this.errorMessage = null;
      
      const offerData: Offer = {
        id: 0, // Will be assigned by the server
        title: this.offerForm.value.title,
        description: this.offerForm.value.description,
        price: this.offerForm.value.price,
        durationHours: this.offerForm.value.durationHours,
        userTypeId: null,
        isActive: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      this.offerService.createOffer(offerData).subscribe({
        next: (offer) => {
          console.log('Offer created successfully:', offer);
          this.isSubmitting = false;
          // Redirect to offers list
          this.router.navigate(['/offers']);
        },
        error: (err) => {
          console.error('Error creating offer:', err);
          this.errorMessage = 'Failed to create offer. Please try again later.';
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