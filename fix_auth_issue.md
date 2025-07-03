# Fix Authentication Issue - Immediate Logout

## Problem
Users can sign in but are immediately logged out after successful authentication.

## Debugging Steps

### 1. Check Environment Variables
First, verify your Supabase environment variables are correctly set:

**In your frontend directory, create a `.env` file:**
```bash
cd frontend
# Create .env file with your Supabase credentials
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

### 2. Check Browser Console
1. Open your browser's Developer Tools (F12)
2. Go to the Console tab
3. Look for authentication-related log messages starting with 🔍, 🔑, 🔄, etc.
4. Look for any errors related to Supabase or authentication

### 3. Check Network Tab
1. In Developer Tools, go to Network tab
2. Try to log in
3. Look for any failed requests to Supabase
4. Check if there are any 401 or 403 responses

### 4. Clear Browser Storage
Sometimes old/corrupted session data can cause issues:
```javascript
// Run this in browser console to clear all Supabase data
localStorage.removeItem('sb-your-project-auth-token');
sessionStorage.clear();
// Then refresh the page
```

### 5. Check Supabase Dashboard
1. Go to your Supabase project dashboard
2. Navigate to Authentication > Users
3. Verify your test user exists and is confirmed
4. Check if email confirmation is required

### 6. Test with Direct Supabase Client
Run this in browser console after logging in:
```javascript
// Check current session
supabase.auth.getSession().then(({data, error}) => {
  console.log('Session:', data.session);
  console.log('Error:', error);
});

// Check current user
supabase.auth.getUser().then(({data, error}) => {
  console.log('User:', data.user);
  console.log('Error:', error);
});
```

## Common Solutions

### Solution 1: Environment Variables
Ensure your `.env` file in the frontend directory has:
```
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

**Restart your dev server after adding .env file!**

### Solution 2: Browser Storage Issues
Clear all browser data for localhost:5173 and try again.

### Solution 3: Session Configuration
The updated Supabase client now has better session persistence. If still having issues, try:
```javascript
// In browser console, force refresh the session
supabase.auth.refreshSession();
```

### Solution 4: Email Confirmation
If your Supabase project requires email confirmation:
1. Check your email for confirmation link
2. Or disable email confirmation in Supabase dashboard:
   - Go to Authentication > Settings
   - Turn off "Enable email confirmations"

### Solution 5: CORS Issues
If you see CORS errors, check your Supabase project settings:
1. Go to Settings > API
2. Add your frontend URL (http://localhost:5173) to allowed origins

## Testing the Fix

After applying solutions:

1. **Clear browser cache and storage**
2. **Restart your frontend dev server**
3. **Try signing in again**
4. **Watch the debug panel in the top-right corner**
5. **Check browser console for detailed logs**

## Current Debugging Features Added

1. **Enhanced logging** in useAuth hook with 🔍, 🔑, 🔄 emojis
2. **AuthDebug component** showing real-time auth state
3. **Better error handling** and session validation
4. **Improved Supabase client configuration** with session persistence

## If Still Having Issues

1. Check the AuthDebug panel in the top-right corner of your app
2. Look for mismatches between useAuth state and direct Supabase state
3. Check console logs for specific error messages
4. Verify your Supabase project is active and accessible

The debug panel will show you exactly what's happening with your authentication state in real-time. 