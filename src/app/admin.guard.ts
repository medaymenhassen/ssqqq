import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AdminGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    const user = this.authService.getCurrentUser();
    
    if (user && user.role === 'ADMIN') {
      return true;
    } else {
      // Redirect to home if not admin
      this.router.navigate(['/']);
      return false;
    }
  }
}