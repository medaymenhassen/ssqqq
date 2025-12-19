import { Component, OnInit } from '@angular/core';
import { UserTypeService, UserType } from '../user-type.service';
import { Router } from '@angular/router';
import { NgIf, NgFor } from '@angular/common';

@Component({
  selector: 'app-user-type-list',
  imports: [NgIf, NgFor],
  templateUrl: './user-type-list.component.html',
  styleUrl: './user-type-list.component.scss'
})
export class UserTypeListComponent implements OnInit {
  userTypes: UserType[] = [];
  loading: boolean = false;
  error: string = '';

  constructor(
    private userTypeService: UserTypeService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadUserTypes();
  }

  loadUserTypes(): void {
    this.loading = true;
    this.error = '';

    this.userTypeService.getAllUserTypes().subscribe({
      next: (userTypes) => {
        this.userTypes = userTypes;
        this.loading = false;
      },
      error: (error) => {
        // Provide more specific error messages
        if (error.message) {
          this.error = error.message;
        } else {
          this.error = 'Erreur lors du chargement des types d\'utilisateurs. Vous devez être administrateur pour accéder à cette fonctionnalité.';
        }
        this.loading = false;
        console.error(error);
      }
    });
  }

  editUserType(id: number): void {
    this.router.navigate(['/user-types', id, 'edit']);
  }

  deleteUserType(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce type d\'utilisateur ?')) {
      this.userTypeService.deleteUserType(id).subscribe({
        next: () => {
          // Reload the list after deletion
          this.loadUserTypes();
        },
        error: (error) => {
          this.error = 'Erreur lors de la suppression du type d\'utilisateur';
          console.error(error);
        }
      });
    }
  }

  createUserType(): void {
    this.router.navigate(['/user-types/create']);
  }
}
