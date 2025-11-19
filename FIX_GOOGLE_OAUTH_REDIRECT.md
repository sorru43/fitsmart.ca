# Fix Google OAuth Redirect URI Mismatch Error

## Error: `redirect_uri_mismatch`

This error occurs when the redirect URI sent by your application doesn't exactly match what's configured in Google Cloud Console.

## Quick Fix Steps

### 1. Check What Redirect URI Your App is Using

The application uses: `https://fitsmart.ca/login/google/callback`

**Important**: The redirect URI must match EXACTLY, including:
- Protocol (http vs https)
- Domain (with or without www)
- Path (exact path, no trailing slash)
- Port (if using non-standard port)

### 2. Update Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Under **Authorized redirect URIs**, add these EXACT URIs:

```
https://fitsmart.ca/login/google/callback
https://www.fitsmart.ca/login/google/callback
```

**Important Notes**:
- ✅ Include both `www` and non-`www` versions if your site uses both
- ✅ Use `https://` (not `http://`) for production
- ✅ No trailing slash: `/login/google/callback` (not `/login/google/callback/`)
- ✅ Exact path: `/login/google/callback` (not `/auth/google/callback`)

### 3. Common Mistakes to Avoid

❌ **Wrong**: `http://fitsmart.ca/login/google/callback` (HTTP instead of HTTPS)
❌ **Wrong**: `https://fitsmart.ca/login/google/callback/` (trailing slash)
❌ **Wrong**: `https://fitsmart.ca/auth/google/callback` (wrong path)
❌ **Wrong**: `https://fitsmart.ca:443/login/google/callback` (port number)
✅ **Correct**: `https://fitsmart.ca/login/google/callback`

### 4. For Development (Local Testing)

If testing locally, also add:
```
http://localhost:5000/login/google/callback
```

### 5. Verify Configuration

After updating Google Cloud Console:

1. **Wait 1-2 minutes** for changes to propagate
2. **Clear your browser cache** or use incognito mode
3. **Try logging in again**

### 6. Check Application Logs

The application now logs the redirect URI being used. Check your server logs to see what URI is being sent:

```bash
# On your server
tail -f /path/to/your/logs/app.log | grep "Google OAuth redirect URI"
```

You should see:
```
Google OAuth redirect URI: https://fitsmart.ca/login/google/callback
```

### 7. If Still Not Working

1. **Verify the redirect URI in logs matches Google Console exactly**
2. **Check if your site redirects www to non-www (or vice versa)**
   - If your site redirects `www.fitsmart.ca` → `fitsmart.ca`, you need BOTH in Google Console
3. **Check if you're behind a proxy/load balancer**
   - May need to configure `PREFERRED_URL_SCHEME = 'https'` in your `.env`
4. **Verify environment variables are loaded**:
   ```bash
   # Check if Google OAuth is configured
   grep GOOGLE_CLIENT_ID .env
   grep GOOGLE_CLIENT_SECRET .env
   ```

## Configuration in .env (Optional)

If your site is behind a proxy or load balancer, you may need to set:

```env
PREFERRED_URL_SCHEME=https
SERVER_NAME=fitsmart.ca
```

## Testing

1. Go to: `https://fitsmart.ca/login`
2. Click "Sign in with Google"
3. You should be redirected to Google's login page
4. After logging in, you should be redirected back to your site

## Still Having Issues?

1. Check Google Cloud Console → APIs & Services → OAuth consent screen
   - Make sure your app is published (if not in testing mode)
   - Add test users if app is in testing mode

2. Check application logs for the exact redirect URI being used

3. Verify your domain matches exactly:
   - `fitsmart.ca` vs `www.fitsmart.ca`
   - `https://` vs `http://`

4. Try adding both www and non-www versions in Google Console

## Summary

**The redirect URI must be EXACTLY**:
```
https://fitsmart.ca/login/google/callback
```

Add this (and the www version if needed) to Google Cloud Console → OAuth 2.0 Client → Authorized redirect URIs.

