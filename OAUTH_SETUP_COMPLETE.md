# Complete OAuth Setup Guide for FitSmart

This guide will walk you through setting up Google OAuth authentication for your FitSmart application.

## 📋 Prerequisites

- Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- Your production domain: `fitsmart.ca` (or your actual domain)
- Access to your server's `.env` file

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click **"New Project"**
4. Enter project name: `FitSmart` (or any name you prefer)
5. Click **"Create"**
6. Wait for the project to be created, then select it

### Step 2: Configure OAuth Consent Screen

1. In Google Cloud Console, go to **"APIs & Services"** > **"OAuth consent screen"**
2. Choose **"External"** (unless you have Google Workspace)
3. Click **"Create"**
4. Fill in the required information:
   - **App name**: `FitSmart`
   - **User support email**: `fitsmart.ca@gmail.com` (or your support email)
   - **Developer contact information**: `fitsmart.ca@gmail.com`
   - Click **"Save and Continue"**

5. **Scopes** (Step 2):
   - Click **"Add or Remove Scopes"**
   - Add these scopes:
     - `email`
     - `profile`
     - `openid`
   - Click **"Update"** then **"Save and Continue"**

6. **Test users** (Step 3 - if in testing mode):
   - Add your email address as a test user
   - Click **"Save and Continue"**

7. **Summary** (Step 4):
   - Review and click **"Back to Dashboard"**

### Step 3: Enable Google Identity API

1. Go to **"APIs & Services"** > **"Library"**
2. Search for **"Google Identity"** or **"Google+ API"**
3. Click on **"Google Identity"** or **"Google+ API"**
4. Click **"Enable"**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** > **"OAuth client ID"**
3. If prompted, select **"Web application"** as the application type
4. Fill in the details:
   - **Name**: `FitSmart Web Client`
   - **Authorized JavaScript origins**:
     ```
     http://localhost:5000
     https://fitsmart.ca
     ```
     (Add your actual production domain if different)
   
   - **Authorized redirect URIs**:
     ```
     http://localhost:5000/login/google/callback
     https://fitsmart.ca/login/google/callback
     ```
     (Replace `fitsmart.ca` with your actual domain)
   
5. Click **"Create"**
6. **IMPORTANT**: Copy both:
   - **Client ID** (looks like: `123456789-abcdefghijklmnop.apps.googleusercontent.com`)
   - **Client Secret** (looks like: `GOCSPX-abcdefghijklmnopqrstuvwxyz`)

### Step 5: Configure Environment Variables

1. **On your CloudPanel server**, navigate to your project directory:
   ```bash
   cd /home/fitsmart/htdocs/www.fitsmart.ca
   ```

2. **Check if `.env` file exists**:
   ```bash
   ls -la .env
   ```

3. **If `.env` doesn't exist, create it**:
   ```bash
   touch .env
   ```

4. **Edit the `.env` file** (use `nano` or `vi`):
   ```bash
   nano .env
   ```

5. **Add these lines** (replace with your actual credentials):
   ```env
   GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

6. **Save and exit**:
   - In `nano`: Press `Ctrl+X`, then `Y`, then `Enter`
   - In `vi`: Press `Esc`, type `:wq`, then `Enter`

### Step 6: Run Database Migration

1. **Activate your virtual environment** (if not already active):
   ```bash
   source venv/bin/activate
   ```

2. **Run the migration script**:
   ```bash
   python migrations/add_google_oauth.py
   ```

3. **Expected output**:
   ```
   Added google_id column to user table
   Made username column nullable
   Made password_hash column nullable
   Migration completed successfully
   ```
   
   Or if already migrated:
   ```
   google_id column already exists
   Migration completed successfully
   ```

### Step 7: Restart Your Application

1. **If using Gunicorn**, stop the current process:
   - Press `Ctrl+C` if running in foreground
   - Or find and kill the process:
     ```bash
     pkill -f gunicorn
     ```

2. **Start the application again**:
   ```bash
   source venv/bin/activate
   venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
   ```

   Or if running in background:
   ```bash
   nohup venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app > gunicorn.log 2>&1 &
   ```

### Step 8: Test OAuth Login

1. **Open your website** in a browser:
   - Production: `https://fitsmart.ca/login`
   - Or your actual domain

2. **Check for "Sign in with Google" button**:
   - You should see a Google sign-in button below the regular login form
   - If you don't see it, check the next section

3. **Test the login**:
   - Click "Sign in with Google"
   - You should be redirected to Google's login page
   - After logging in, you'll be redirected back and logged in

---

## ✅ Verification Checklist

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] Google Identity API enabled
- [ ] OAuth 2.0 credentials created
- [ ] Client ID and Secret copied
- [ ] `.env` file updated with credentials
- [ ] Database migration run successfully
- [ ] Application restarted
- [ ] "Sign in with Google" button appears on login page
- [ ] OAuth login works end-to-end

---

## 🔧 Troubleshooting

### Issue: "Sign in with Google" button not showing

**Solution:**
1. Check that `.env` file has both `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
2. Verify no typos in the environment variable names
3. Restart the application
4. Check application logs for OAuth initialization errors:
   ```bash
   tail -f gunicorn.log
   ```
   Look for: `"Google OAuth initialized successfully"`

### Issue: "Invalid redirect URI" error

**Solution:**
1. Go to Google Cloud Console > Credentials
2. Edit your OAuth 2.0 Client ID
3. Verify the redirect URI matches exactly:
   - Must be: `https://fitsmart.ca/login/google/callback`
   - Check for trailing slashes, `http` vs `https`, etc.
4. Save and wait a few minutes for changes to propagate

### Issue: "Access blocked" or "App not verified"

**Solution:**
1. If app is in testing mode, add your email as a test user
2. Go to OAuth consent screen > Test users
3. Add your email address
4. For production, you'll need to submit for verification (can take days/weeks)

### Issue: Database migration errors

**Solution:**
1. Check database connection:
   ```bash
   python -c "from app import create_app; from database.models import db; app = create_app(); app.app_context().push(); print('DB OK')"
   ```

2. If using PostgreSQL, ensure you have proper permissions:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE your_db TO your_user;
   ```

3. Run migration again with verbose output:
   ```bash
   python migrations/add_google_oauth.py
   ```

### Issue: "Could not retrieve email from Google account"

**Solution:**
1. Verify scopes include `email` and `profile`
2. Check OAuth consent screen has these scopes
3. User must grant email permission when logging in

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** to Git
2. **Use different credentials** for development and production
3. **Rotate secrets** periodically (every 90 days recommended)
4. **Monitor OAuth usage** in Google Cloud Console
5. **Set up alerts** for unusual OAuth activity
6. **Keep Google Cloud Console access secure** (use 2FA)

---

## 📝 Quick Reference

### Environment Variables Needed:
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Redirect URIs to Configure:
- Development: `http://localhost:5000/login/google/callback`
- Production: `https://fitsmart.ca/login/google/callback`

### Required Scopes:
- `email`
- `profile`
- `openid`

---

## 🆘 Need Help?

If you encounter issues:
1. Check the application logs: `tail -f gunicorn.log`
2. Check Google Cloud Console for OAuth errors
3. Verify all environment variables are set correctly
4. Ensure database migration completed successfully

---

## ✨ Features Enabled

Once set up, users can:
- ✅ Sign in with their Google account
- ✅ Automatically create account on first Google login
- ✅ Link Google account to existing email-based account
- ✅ Skip email verification (Google accounts are pre-verified)
- ✅ Faster login experience

---

**Last Updated**: 2025-01-16
**Version**: 1.0

