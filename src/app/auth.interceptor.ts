import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from './auth.service';

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn): Observable<HttpEvent<unknown>> => {
  const authService = inject(AuthService);
  
  // Get the current JWT token from storage
  const token = authService.getAccessToken();
  console.log('🔐 [AuthInterceptor] Intercepting request:', {
    url: req.url,
    hasToken: !!token,
    tokenLength: token?.length,
    method: req.method
  });

  // If token exists, add it to the request Authorization header
  if (token) {
    // Clone the request and set the Authorization header
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    console.log('🔐 [AuthInterceptor] Added authorization header to request:', req.url);
  } else {
    console.log('🔐 [AuthInterceptor] No token available for request:', req.url);
  }

  // Handle the request and catch errors
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      console.log('🔐 [AuthInterceptor] HTTP Error occurred:', {
        url: req.url,
        status: error.status,
        message: error.message,
        error: error.error
      });
      
      // Handle 401 Unauthorized - Token may be expired
      if (error.status === 401) {
        console.log('🔐 [AuthInterceptor] 401 error detected, attempting token refresh for:', req.url);
        
        // Try to refresh the token
        return authService.refreshToken().pipe(
          switchMap(() => {
            console.log('🔐 [AuthInterceptor] Token refresh successful, retrying request:', req.url);
            
            // Token refreshed successfully, retry the original request with new token
            const newToken = authService.getAccessToken();
            console.log('🔐 [AuthInterceptor] Retrieved new token after refresh:', {
              hasNewToken: !!newToken,
              newTokenLength: newToken?.length
            });
            
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
              console.log('🔐 [AuthInterceptor] No new token after refresh, logging out user');
              authService.logout();
              return throwError(() => error);
            }
          }),
          catchError((refreshError) => {
            console.log('🔐 [AuthInterceptor] Token refresh failed:', refreshError);
            
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