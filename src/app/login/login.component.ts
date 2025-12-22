import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../auth.service';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, NgIf, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  onSubmit(): void {
    console.log('🔐 [LoginComponent.onSubmit] Starting login process');
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';

      const { email, password } = this.loginForm.value;
      console.log('🔐 [LoginComponent.onSubmit] Form values:', { email, password: password ? '***' : '' });

      this.authService.login(email, password).subscribe({
        next: (response) => {
          console.log('🔐 [LoginComponent.onSubmit] Login successful, navigating to bodyanalytics');
          this.isLoading = false;
          // Redirect to bodyanalytics page
          this.router.navigate(['/bodyanalytics']);
        },
        error: (error) => {
          console.log('🔐 [LoginComponent.onSubmit] Login failed:', error);
          this.isLoading = false;
          this.errorMessage = error.error?.message || 'Erreur de connexion. Veuillez vérifier vos identifiants.';
        }
      });
    }
  }
}
