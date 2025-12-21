import { Component, OnInit } from '@angular/core';
import { AuthService, User } from '../auth.service';
import { Router } from '@angular/router';
import { NgIf, NgFor, DatePipe } from '@angular/common';

@Component({
  selector: 'app-user-list',
  imports: [NgIf, NgFor, DatePipe],
  templateUrl: './user-list.component.html',
  styleUrl: './user-list.component.scss'
})
export class UserListComponent implements OnInit {
  users: User[] = [];
  loading: boolean = false;
  error: string = '';

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  viewUserProfile(userId: number): void {
    this.router.navigate(['/profile', userId]);
  }

  loadUsers(): void {
    // Get all users
    this.authService.getAllUsers().subscribe({
      next: (users) => {
        this.users = users;
      },
      error: (error) => {
        console.error('Error loading users:', error);
        // Fallback to current user if we can't load all users
        const currentUser = this.authService.getCurrentUser();
        if (currentUser) {
          this.users = [currentUser];
        }
      }
    });
  }
}
