# Fix Google OAuth Redirect URI Mismatch Error

## Error: redirect_uri_mismatch

This error occurs when the redirect URI in your Google Cloud Console doesn't match what your application is sending.

## Solution

### Step 1: Check Your Current Redirect URI

Your application is using:
- **Local Development**: `http://localhost:5000/login/google/callback`
- **Production**: `https://fitsmart.ca/login/google/callback`

### Step 2: Update Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: **fitsmart-web**
3. Navigate to: **APIs & Services** → **Credentials**
4. Find your OAuth 2.0 Client ID (the one with Client ID: `449583623550-uvvmm095s5m7r3aoiljs4pbprad0qo32`)
5. Click **Edit** (pencil icon)
6. Under **Authorized redirect URIs**, add these EXACT URLs:

```
http://localhost:5000/login/google/callback
https://fitsmart.ca/login/google/callback
```

**Important Notes:**
- The URLs must match EXACTLY (including http vs https, trailing slashes, etc.)
- No trailing slashes
- Include the port number for localhost
- Use lowercase

### Step 3: Save and Wait

1. Click **Save**
2. Wait 1-2 minutes for changes to propagate
3. Try signing in again

### Step 4: Verify Redirect URI in Code

The redirect URI is generated in `routes/main_routes.py`:
```python
redirect_uri = url_for('main.google_callback', _external=True)
```

This will generate:
- `http://localhost:5000/login/google/callback` (local)
- `https://fitsmart.ca/login/google/callback` (production)

## Common Issues

### Issue 1: Missing Port Number
❌ Wrong: `http://localhost/login/google/callback`
✅ Correct: `http://localhost:5000/login/google/callback`

### Issue 2: Trailing Slash
❌ Wrong: `http://localhost:5000/login/google/callback/`
✅ Correct: `http://localhost:5000/login/google/callback`

### Issue 3: HTTP vs HTTPS
- Local development: Use `http://`
- Production: Use `https://`

### Issue 4: Wrong Path
❌ Wrong: `/auth/google/callback`
✅ Correct: `/login/google/callback`

## Testing

After updating:
1. Clear browser cache
2. Try signing in again
3. Check browser console for any errors

## Still Not Working?

1. Double-check the redirect URI in Google Console matches exactly
2. Wait a few minutes for Google's servers to update
3. Try in an incognito window
4. Check the browser's Network tab to see the exact redirect URI being sent

