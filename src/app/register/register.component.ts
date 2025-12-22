import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../auth.service';
import { UserTypeService, UserType } from '../user-type.service';
import { DocumentService } from '../services/document.service';
import { NgIf, NgFor } from '@angular/common';
import { OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, NgIf, NgFor, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss'
})
export class RegisterComponent implements OnInit, OnDestroy {
  registerForm!: FormGroup;
  documentForm!: FormGroup;
  loading = false;
  submitted = false;
  errorMessage = '';
  successMessage = '';
  selectedFiles: File[] = [];
  isLoading = false;
  registrationComplete = false;
  showDocumentForm = false;
  selectedUserType: UserType | null = null;
  userTypes: UserType[] = [];
  
  private destroy$ = new Subject<void>();

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    public router: Router
  ) {}

  ngOnInit(): void {
    this.initializeForm();
    
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/dashboard']);
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private initializeForm(): void {
    this.registerForm = this.formBuilder.group({
      firstname: ['', [Validators.required, Validators.minLength(2)]],
      lastname: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],
      rgpdAccepted: [false, Validators.requiredTrue],
      ccpaAccepted: [false],
      commercialUseConsent: [false, Validators.requiredTrue],
      userTypeId: ['']
    }, { 
      validators: this.passwordMatchValidator 
    });
    
    this.documentForm = this.formBuilder.group({
      documents: [null]
    });
  }

  private passwordMatchValidator(group: FormGroup): { [key: string]: any } | null {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;
    
    if (password && confirmPassword && password !== confirmPassword) {
      return { passwordMismatch: true };
    }
    
    return null;
  }

  onSubmit(): void {
    console.log('🔐 [RegisterComponent.onSubmit] Starting registration process');
    this.submitted = true;
    this.errorMessage = '';
    this.successMessage = '';

    if (this.registerForm.invalid) {
      console.log('🔐 [RegisterComponent.onSubmit] Form is invalid, returning');
      return;
    }

    this.loading = true;
    this.isLoading = true;

    const formData = this.registerForm.value;
    console.log('🔐 [RegisterComponent.onSubmit] Form data:', {
      firstname: formData.firstname,
      lastname: formData.lastname,
      email: formData.email,
      hasPassword: !!formData.password,
      rgpdAccepted: formData.rgpdAccepted,
      ccpaAccepted: formData.ccpaAccepted,
      commercialUseConsent: formData.commercialUseConsent
    });
    
    const registerRequest = {
      firstname: formData.firstname,
      lastname: formData.lastname,
      email: formData.email,
      password: formData.password,
      rgpdAccepted: formData.rgpdAccepted,
      ccpaAccepted: formData.ccpaAccepted,
      commercialUseConsent: formData.commercialUseConsent
    };

    this.authService.register(registerRequest)
      .pipe(
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (response) => {
          console.log('🔐 [RegisterComponent.onSubmit] Registration successful, response:', response);
          
          this.successMessage = '✅ Registration successful! Redirecting...';
          this.loading = false;

          // ✅ Les tokens sont DÉJÀ stockés par auth.service.register()
          // ✅ Charger l'utilisateur immédiatement après la réponse
          console.log('🔐 [RegisterComponent.onSubmit] About to load current user after registration');
          this.authService.loadCurrentUser();
          setTimeout(() => {
            console.log('🔐 [RegisterComponent.onSubmit] Navigating to home after registration');
            this.router.navigate(['/']);
          }, 500);  // Délai court pour que le profil soit chargé
        }, 
        error: (error) => {
          console.log('🔐 [RegisterComponent.onSubmit] Registration failed:', error);
          this.loading = false;

          if (error.error && typeof error.error === 'object') {
            if (error.error.error) {
              this.errorMessage = error.error.error;
            } else if (error.error.message) {
              this.errorMessage = error.error.message;
            } else {
              this.errorMessage = 'Registration failed. Please try again.';
            }
          } else if (error.status === 0) {
            this.errorMessage = 'Network error. Please check your connection.';
          } else {
            this.errorMessage = error.statusText || 'Registration failed. Please try again.';
          }
        }
      });
  }

  hasError(fieldName: string): boolean {
    const field = this.registerForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched || this.submitted));
  }

  getErrorMessage(fieldName: string): string {
    const field = this.registerForm.get(fieldName);
    
    if (!field || !field.errors) {
      return '';
    }

    if (field.errors['required']) {
      return `${this.formatFieldName(fieldName)} is required`;
    }
    
    if (field.errors['minlength']) {
      const minLength = field.errors['minlength'].requiredLength;
      return `${this.formatFieldName(fieldName)} must be at least ${minLength} characters`;
    }
    
    if (field.errors['email']) {
      return 'Please enter a valid email address';
    }
    
    if (fieldName === 'confirmPassword' && this.registerForm.errors?.['passwordMismatch']) {
      return 'Passwords do not match';
    }

    return 'Invalid input';
  }

  private formatFieldName(fieldName: string): string {
    return fieldName
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase())
      .trim();
  }

  get passwordsMatch(): boolean {
    const password = this.registerForm.get('password')?.value;
    const confirmPassword = this.registerForm.get('confirmPassword')?.value;
    
    if (!password || !confirmPassword) {
      return true;
    }
    
    return password === confirmPassword;
  }

  onUserTypeChange(event: any): void {
    const userTypeId = event.target.value;
    if (userTypeId) {
      // Show document form for special user types
      this.showDocumentForm = true;
    } else {
      this.showDocumentForm = false;
    }
  }

  onFileSelect(event: any): void {
    const files: FileList = event.target.files;
    this.selectedFiles = Array.from(files);
  }

  onSubmitDocuments(): void {
    this.isLoading = true;
    // Simulate document upload
    setTimeout(() => {
      this.isLoading = false;
      this.registrationComplete = true;
      this.showDocumentForm = false;
    }, 2000);
  }
}