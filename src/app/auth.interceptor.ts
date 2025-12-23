import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<unknown>> => {
  const authService = inject(AuthService);
  
  // Get the current JWT token from storage
  const token = authService.getAccessToken();

  // If token exists, add it to the request Authorization header
  if (token) {
    // Clone the request and set the Authorization header
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  // Handle the request and catch errors
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      
      // Handle 401 Unauthorized - Token may be expired
      if (error.status === 401) {
        
        // Try to refresh the token
        return authService.refreshToken().pipe(
          switchMap(() => {
            
            // Token refreshed successfully, retry the original request with new token
            const newToken = authService.getAccessToken();
            
            if (newToken) {
              // Clone the original request and add new token
              const authReq = req.clone({
                setHeaders: {
                  Authorization: `Bearer ${newToken}`
                }
              });
              
              // Retry the request with new token
              return next(authReq);
            } else {
              // No token after refresh, logout user
              authService.logout();
              return throwError(() => error);
            }
          }),
          catchError((refreshError) => {
            
            // Token refresh failed, logout user
            authService.logout();
            return throwError(() => refreshError);
          })
        );
      }

      // Re-throw the error for the caller to handle
      return throwError(() => error);
    })
  );
};