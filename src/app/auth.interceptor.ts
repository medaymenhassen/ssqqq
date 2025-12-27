import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<unknown>> => {
  const authService = inject(AuthService);
  
  // Check if this is a request to the Django backend (should not be intercepted)
  // Django backend is accessed via /ai/ path (both in dev and prod)
  const isDjangoBackend = req.url.includes('/ai/');
  
  if (!isDjangoBackend) {
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
  }
  
  // Handle the request and catch errors
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      
      // Only handle 401 errors for non-Django backend requests
      const isDjangoBackendError = error.url?.includes('/ai/');
      
      if (error.status === 401 && !isDjangoBackendError) {
        
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