import { Component, OnInit } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from './auth.service';
import { AsyncPipe, NgIf } from '@angular/common';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, NgIf],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = '3Dproject';
  
  constructor(public authService: AuthService) {}
  
  ngOnInit(): void {
    // Load current user if token exists
    this.authService.loadCurrentUser();
  }
  
  logout(): void {
    this.authService.logout();
  }
}
