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
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';

      const { email, password } = this.loginForm.value;

      this.authService.login(email, password).subscribe({
        next: (response) => {
          this.isLoading = false;
          // Wait a bit for the user to be loaded, then redirect based on role
          setTimeout(() => {
            const user = this.authService.getCurrentUser();
            if (user && user.role === 'ADMIN') {
              this.router.navigate(['/admin/approvals']);
            } else {
              this.router.navigate(['/profile']);
            }
          }, 100);
        },
        error: (error) => {
          this.isLoading = false;
          this.errorMessage = error.error?.message || 'Erreur de connexion. Veuillez vérifier vos identifiants.';
        }
      });
    }
  }
}
