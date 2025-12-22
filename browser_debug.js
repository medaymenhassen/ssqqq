/**
 * Browser-side debugging script for authentication issues
 * Run this in the browser console after the app loads
 */

console.log('=== Browser Authentication Debug ===');

// Wait for Angular to load
setTimeout(() => {
  console.log('Checking authentication state...');
  
  // Step 1: Check localStorage
  console.log('\n--- Step 1: Checking localStorage ---');
  try {
    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    
    console.log('Access Token:', accessToken ? `Present (${accessToken.length} chars)` : 'Absent');
    console.log('Refresh Token:', refreshToken ? `Present (${refreshToken.length} chars)` : 'Absent');
    
    if (accessToken) {
      try {
        // Decode token payload
        const parts = accessToken.split('.');
        if (parts.length === 3) {
          const payload = parts[1];
          const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
          const decoded = atob(paddedPayload);
          const payloadJson = JSON.parse(decoded);
          console.log('Token Payload:', payloadJson);
          console.log('Token Expires:', new Date(payloadJson.exp * 1000));
        }
      } catch (e) {
        console.log('Error decoding token:', e);
      }
    }
  } catch (e) {
    console.log('Error accessing localStorage:', e);
  }
  
  // Step 2: Check if we can access Angular services
  console.log('\n--- Step 2: Checking Angular Services ---');
  try {
    // Try to get the root component
    const appRoot = document.querySelector('app-root');
    if (appRoot) {
      console.log('✅ App root found');
      
      // Try to access the Angular injector
      const injector = angular.element(appRoot).injector();
      if (injector) {
        console.log('✅ Angular injector found');
        
        // Try to get AuthService
        try {
          const authService = injector.get('AuthService');
          if (authService) {
            console.log('✅ AuthService found');
            console.log('Is Logged In:', authService.isLoggedIn());
            console.log('Current User:', authService.getCurrentUser());
            console.log('Access Token from Service:', authService.getAccessToken());
          } else {
            console.log('❌ AuthService not available');
          }
        } catch (e) {
          console.log('Error getting AuthService:', e);
        }
      } else {
        console.log('❌ Angular injector not found');
      }
    } else {
      console.log('❌ App root not found');
    }
  } catch (e) {
    console.log('Error accessing Angular services:', e);
  }
  
  // Step 3: Check DOM elements
  console.log('\n--- Step 3: Checking DOM Elements ---');
  const navComponent = document.querySelector('app-navigation');
  if (navComponent) {
    console.log('✅ Navigation component found');
    
    const loginButtons = navComponent.querySelectorAll('a[href="/login"], a[href="/register"]');
    const logoutButton = navComponent.querySelector('button');
    
    console.log('Login/Register buttons found:', loginButtons.length);
    console.log('Logout button found:', !!logoutButton);
    
    if (logoutButton) {
      console.log('Logout button text:', logoutButton.textContent);
      console.log('Logout button visible:', logoutButton.offsetParent !== null);
    }
  } else {
    console.log('❌ Navigation component not found');
  }
  
  // Step 4: Manual token test
  console.log('\n--- Step 4: Manual Token Test ---');
  if (typeof localStorage !== 'undefined') {
    const token = localStorage.getItem('accessToken');
    if (token) {
      console.log('Testing token with fetch API...');
      
      fetch('/api/user/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        console.log('Profile API response status:', response.status);
        return response.json();
      })
      .then(data => {
        console.log('Profile data:', data);
      })
      .catch(error => {
        console.log('Profile API error:', error);
      });
    } else {
      console.log('No token found for manual test');
    }
  }
  
  console.log('\n=== Debug Complete ===');
}, 3000); // Wait 3 seconds for app to load