import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { UserTypeService, UserType, UserTypeRequest } from '../user-type.service';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-user-type-form',
  imports: [ReactiveFormsModule, NgIf],
  templateUrl: './user-type-form.component.html',
  styleUrl: './user-type-form.component.scss'
})
export class UserTypeFormComponent implements OnInit {
  userTypeForm: FormGroup;
  isEditMode: boolean = false;
  userTypeID: number | null = null;
  loading: boolean = false;
  error: string = '';

  constructor(
    private fb: FormBuilder,
    private userTypeService: UserTypeService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.userTypeForm = this.fb.group({
      nom: ['', [Validators.required, Validators.minLength(2)]],
      description: ['', [Validators.maxLength(500)]],
      special: [false]
    });
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.userTypeID = +id;
      this.loadUserType(this.userTypeID);
    }
  }

  loadUserType(id: number): void {
    this.loading = true;
    this.userTypeService.getUserTypeById(id).subscribe({
      next: (userType) => {
        this.userTypeForm.patchValue({
          nom: userType.nom,
          description: userType.description,
          special: userType.special
        });
        this.loading = false;
      },
      error: (error) => {
        this.error = 'Erreur lors du chargement du type d\'utilisateur';
        this.loading = false;
        console.error(error);
      }
    });
  }

  onSubmit(): void {
    if (this.userTypeForm.valid) {
      this.loading = true;
      this.error = '';

      const request: UserTypeRequest = this.userTypeForm.value;

      if (this.isEditMode && this.userTypeID) {
        // Update existing user type
        this.userTypeService.updateUserType(this.userTypeID, request).subscribe({
          next: (userType) => {
            this.loading = false;
            this.router.navigate(['/user-types']);
          },
          error: (error) => {
            this.loading = false;
            if (error.message) {
              this.error = error.message;
            } else {
              this.error = 'Erreur lors de la mise à jour du type d\'utilisateur. Vous devez être administrateur pour effectuer cette action.';
            }
            console.error(error);
          }
        });
      } else {
        // Create new user type
        this.userTypeService.createUserType(request).subscribe({
          next: (userType) => {
            this.loading = false;
            this.router.navigate(['/user-types']);
          },
          error: (error) => {
            this.loading = false;
            if (error.message) {
              this.error = error.message;
            } else {
              this.error = 'Erreur lors de la création du type d\'utilisateur. Vous devez être administrateur pour effectuer cette action.';
            }
            console.error(error);
          }
        });
      }
    }
  }

  onCancel(): void {
    this.router.navigate(['/user-types']);
  }
}
