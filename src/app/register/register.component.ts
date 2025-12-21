import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../auth.service';
import { UserTypeService, UserType } from '../user-type.service';
import { DocumentService } from '../services/document.service';
import { NgIf, NgFor } from '@angular/common';

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, NgIf, NgFor, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss'
})
export class RegisterComponent implements OnInit {
  registerForm: FormGroup;
  documentForm: FormGroup;
  errorMessage: string = '';
  isLoading: boolean = false;
  userTypes: UserType[] = [];
  selectedFiles: File[] = [];
  showDocumentForm: boolean = false;
  registrationComplete: boolean = false;
  registeredUserId: number | null = null;
  selectedUserType: UserType | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private userTypeService: UserTypeService,
    private documentService: DocumentService,
    public router: Router
  ) {
    this.registerForm = this.fb.group({
      firstname: ['', [Validators.required, Validators.minLength(2)]],
      lastname: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required, Validators.minLength(6)]],
      userTypeId: [''],
      rgpdAccepted: [false, Validators.requiredTrue],
      ccpaAccepted: [false]
    });

    this.documentForm = this.fb.group({
      documents: ['']
    });
  }

  ngOnInit(): void {
    this.loadUserTypes();
  }

  loadUserTypes(): void {
    this.userTypeService.getAllUserTypes().subscribe({
      next: (types) => {
        this.userTypes = types;
      },
      error: (error) => {
        console.error('Error loading user types:', error);
      }
    });
  }

  onUserTypeChange(event: any): void {
    const userTypeId = event.target.value;
    if (userTypeId) {
      const userType = this.userTypes.find(type => type.id === parseInt(userTypeId));
      // Since all user types are now considered special, show document form for all types
      this.showDocumentForm = true;
      this.selectedUserType = userType || null;
    } else {
      this.showDocumentForm = false;
      this.selectedUserType = null;
    }
  }

  onFileSelect(event: any): void {
    const files = event.target.files;
    if (files && files.length > 0) {
      this.selectedFiles = Array.from(files);
    }
  }

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';

      const request = {
        firstname: this.registerForm.get('firstname')?.value,
        lastname: this.registerForm.get('lastname')?.value,
        email: this.registerForm.get('email')?.value,
        password: this.registerForm.get('password')?.value,
        rgpdAccepted: this.registerForm.get('rgpdAccepted')?.value,
        ccpaAccepted: this.registerForm.get('ccpaAccepted')?.value
      };

      this.authService.register(request).subscribe({
        next: (response) => {
          this.isLoading = false;
          this.registrationComplete = true;
          // In a real app, you would get the user ID from the response
          // For now, we'll simulate it
          this.registeredUserId = Math.floor(Math.random() * 10000);
          
          // If user selected a type, show document form (all types now require documents)
          const userTypeId = this.registerForm.get('userTypeId')?.value;
          if (userTypeId) {
            const userType = this.userTypes.find(type => type.id === parseInt(userTypeId));
            // Since all user types are now considered special, show document form for all types
            this.showDocumentForm = true;
            this.selectedUserType = userType || null;
          }
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage = error.error?.message || 'Erreur lors de l\'inscription. Veuillez réessayer.';
        }
      });
    }
  }

  onSubmitDocuments(): void {
    if (this.selectedFiles.length > 0 && this.registeredUserId && this.selectedUserType) {
      this.isLoading = true;
      this.documentService.uploadDocuments(
        this.registeredUserId, 
        this.selectedUserType.id, 
        this.selectedFiles
      ).subscribe({
        next: (response) => {
          this.isLoading = false;
          // Redirect to login page after successful document submission
          this.router.navigate(['/login']);
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage = error.error?.message || 'Erreur lors de l\'envoi des documents. Veuillez réessayer.';
        }
      });
    }
  }
}
