/**
 * Debug script to check authentication state in the browser
 * Run this in the browser console to diagnose authentication issues
 */

console.log('=== Authentication State Debug ===');

// Check if we're in a browser environment
if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
  console.log('🔧 Browser environment detected');
  
  // Check localStorage for tokens
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  
  console.log('🔐 Access Token:', accessToken ? `Present (${accessToken.length} chars)` : 'Absent');
  console.log('🔄 Refresh Token:', refreshToken ? `Present (${refreshToken.length} chars)` : 'Absent');
  
  // Decode token if present
  if (accessToken) {
    try {
      const parts = accessToken.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        console.log('🔓 Token Payload:', payload);
        console.log('⏱️ Token Expires:', new Date(payload.exp * 1000));
        console.log('👤 Token Subject:', payload.sub);
        console.log('🎭 Token Role:', payload.role);
      } else {
        console.log('❌ Invalid token format');
      }
    } catch (e) {
      console.log('❌ Error decoding token:', e);
    }
  }
  
  // Check if AuthService is available
  if (typeof angular !== 'undefined') {
    console.log('🅰️ Angular detected');
    // Try to access AuthService if available
    try {
      const authService = angular.element(document.body).injector().get('AuthService');
      if (authService) {
        console.log('✅ AuthService found');
        console.log('👤 Current User:', authService.getCurrentUser());
        console.log('🔒 Logged In:', authService.isLoggedIn());
      }
    } catch (e) {
      console.log('⚠️ Could not access AuthService:', e);
    }
  } else {
    console.log('ℹ️ Not an Angular app or Angular not loaded yet');
  }
  
  // Check for Angular elements
  const appRoot = document.querySelector('app-root');
  if (appRoot) {
    console.log('🏠 App root found');
  } else {
    console.log('❌ App root not found');
  }
  
  // Check navigation component
  const navComponent = document.querySelector('app-navigation');
  if (navComponent) {
    console.log('🧭 Navigation component found');
    const logoutButton = navComponent.querySelector('button');
    if (logoutButton) {
      console.log('🚪 Logout button found:', logoutButton.textContent);
    } else {
      console.log('❌ Logout button not found');
    }
  } else {
    console.log('❌ Navigation component not found');
  }
  
} else {
  console.log('⚠️ Not in browser environment or localStorage not available');
}

console.log('=== End Debug ===');