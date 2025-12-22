/**
 * Simple test to verify interceptor functionality
 * Run this in the browser console after the app loads
 */

console.log('=== Interceptor Test ===');

// Check if we can access the Angular services
setTimeout(() => {
  try {
    // Try to get the AuthService
    const authService = angular.element(document.body).injector().get('AuthService');
    if (authService) {
      console.log('✅ AuthService found');
      console.log('Is logged in:', authService.isLoggedIn());
      console.log('Current user:', authService.getCurrentUser());
      
      // Try to get access token
      const token = authService.getAccessToken();
      console.log('Access token:', token ? `Present (${token.length} chars)` : 'Absent');
    } else {
      console.log('❌ AuthService not found');
    }
  } catch (e) {
    console.log('⚠️ Could not access Angular services:', e);
  }
  
  // Check localStorage directly
  if (typeof localStorage !== 'undefined') {
    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    console.log('LocalStorage Access Token:', accessToken ? `Present (${accessToken.length} chars)` : 'Absent');
    console.log('LocalStorage Refresh Token:', refreshToken ? `Present (${refreshToken.length} chars)` : 'Absent');
  }
  
  console.log('=== End Interceptor Test ===');
}, 2000);