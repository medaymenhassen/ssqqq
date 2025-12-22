# Authentication Debugging Guide

## Debugging Steps

### Step 1: Verify Backend Token Generation

Run the backend test to ensure tokens are being generated correctly:

```bash
run_debug_auth.bat
```

This will test:
1. User registration and token generation
2. User login and token generation  
3. User profile access with token
4. Token refresh functionality

Expected output:
- All steps should return status 200
- Tokens should be present with appropriate lengths
- User profile should be accessible with valid token

### Step 2: Check Browser Storage

Open browser developer tools (F12) and go to the Application/Storage tab:

1. Check Local Storage for `localhost:4200`
2. Verify `accessToken` and `refreshToken` entries exist after login/registration
3. Check token lengths (should be long JWT strings)

### Step 3: Run Browser Debug Script

Paste the following in the browser console after the app loads:

```javascript
// Wait for app to load, then run:
setTimeout(() => {
  console.log('=== Auth Debug ===');
  
  // Check localStorage
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  
  console.log('Access Token:', accessToken ? `Present (${accessToken.length} chars)` : 'Absent');
  console.log('Refresh Token:', refreshToken ? `Present (${refreshToken.length} chars)` : 'Absent');
  
  // Try to decode token
  if (accessToken) {
    try {
      const parts = accessToken.split('.');
      if (parts.length === 3) {
        const payload = parts[1];
        const padded = payload + '='.repeat((4 - payload.length % 4) % 4);
        const decoded = atob(padded);
        const json = JSON.parse(decoded);
        console.log('Token Payload:', json);
        console.log('Expires:', new Date(json.exp * 1000));
      }
    } catch (e) {
      console.log('Token decode error:', e);
    }
  }
  
  // Test API access
  if (accessToken) {
    fetch('/api/user/profile', {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
      console.log('API Response Status:', response.status);
      return response.json();
    })
    .then(data => console.log('Profile Data:', data))
    .catch(e => console.log('API Error:', e));
  }
}, 3000);
```

### Step 4: Check Angular Authentication State

Look at the browser console for these log messages:

1. `🔧 AuthService initialized`
2. `🔍 Checking for existing tokens in localStorage...`
3. `🔐 Access token found: Yes/No`
4. `✅ Token format is valid, loading current user` or `🔍 No valid token found`

### Step 5: Verify HTTP Interceptor

Check that the interceptor is working by looking for these logs:

1. `🔐 [AuthInterceptor] Added Authorization header to request: /api/user/profile`
2. `🔄 Loading user profile from endpoint`

### Step 6: Check Navigation Component

Inspect the DOM to see which buttons are visible:

1. Right-click on the navigation bar and select "Inspect"
2. Look for either:
   - Login/Register buttons (when logged out)
   - User info and Logout button (when logged in)

## Common Issues and Solutions

### Issue 1: "Window not available, cannot retrieve token"

**Cause**: Trying to access localStorage before browser environment is ready

**Solution**: 
- Ensure AuthService methods check `typeof window !== 'undefined'` and `typeof localStorage !== 'undefined'`
- Delay initialization until browser is ready

### Issue 2: Logout button not visible

**Cause**: User profile never loaded successfully

**Solution**:
- Check that HTTP interceptor is attaching tokens to requests
- Verify `/api/user/profile` endpoint is accessible with token
- Check NavigationComponent subscription to `currentUser`

### Issue 3: "Could not refresh token" error

**Cause**: Refresh token endpoint not working or token format invalid

**Solution**:
- Test refresh endpoint with `debug_auth_steps.py`
- Verify token format in backend JwtUtil
- Check refresh token payload contains required claims

## Manual Debug Buttons

The app now includes debug buttons in the top-left corner:

1. **Debug Auth**: Shows current authentication state
2. **Reload User**: Forces reload of user profile
3. **Check & Load**: Manually checks for tokens and loads user

Click these buttons to trigger debugging output in the console.

## Expected Flow After Fixes

1. **Registration/Login**:
   - Tokens stored in localStorage
   - Console shows: `✅ Tokens stored in localStorage`

2. **User Profile Loading**:
   - Console shows: `👤 User profile loaded: {user object}`
   - Navigation updates with user info

3. **Logout Button Visibility**:
   - Logout button appears in navigation bar
   - Console shows: `Navigation - Current user updated: {user object}`

4. **HTTP Requests**:
   - All API calls include Authorization header
   - Console shows: `🔐 [AuthInterceptor] Added Authorization header to request`

## Testing Checklist

- [ ] Backend generates valid tokens (run `run_debug_auth.bat`)
- [ ] Tokens stored in browser localStorage after login/registration
- [ ] HTTP interceptor attaches tokens to requests
- [ ] User profile loads successfully
- [ ] Navigation component shows logout button when logged in
- [ ] Token refresh works when tokens expire
- [ ] Logout clears tokens and redirects to login page

## If Issues Persist

1. Clear browser cache and localStorage
2. Restart development servers
3. Check browser network tab for failed requests
4. Verify backend is running on correct port
5. Check CORS configuration in backend