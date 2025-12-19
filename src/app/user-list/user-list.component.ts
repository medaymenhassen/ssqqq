import { Component, OnInit } from '@angular/core';
import { AuthService, User } from '../auth.service';
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

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    // In a real application, you would have an endpoint to get all users
    // For now, we'll just show the current user as an example
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.users = [currentUser];
    }
  }
}
