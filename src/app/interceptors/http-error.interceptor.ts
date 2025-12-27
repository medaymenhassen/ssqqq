import { HttpInterceptorFn } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

export const httpErrorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: any) => {
      // Check if it's an HTTP error response with string content (like HTML)
      if (error.status && error.error && typeof error.error === 'string') {
        // This might be an HTML error page or plain text response
        // Create a new error with a more descriptive message
        const newError = {
          ...error,
          error: { error: error.error },
          statusText: error.statusText || 'Unknown Error'
        };
        return throwError(() => newError);
      }
      
      // Handle JSON parsing errors specifically
      if (error.name === 'SyntaxError') {
        // This is likely a JSON parsing error
        const newError = {
          ...error,
          error: { error: 'Server returned invalid response format' },
          status: 500,
          statusText: 'Invalid Response Format'
        };
        return throwError(() => newError);
      }
      
      // Return the original error for other cases
      return throwError(() => error);
    })
  );
};