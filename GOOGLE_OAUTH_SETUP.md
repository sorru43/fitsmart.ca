# Google OAuth Authentication Setup Guide

This guide will help you set up Google OAuth authentication for FitSmart.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. Access to Google Cloud Console

## Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google+ API" or "Google Identity"
   - Click "Enable"

4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - If prompted, configure the OAuth consent screen first:
     - Choose "External" (unless you have a Google Workspace)
     - Fill in the required information:
       - App name: FitSmart
       - User support email: info@fitsmart.ca
       - Developer contact: info@fitsmart.ca
     - Add scopes: `email`, `profile`, `openid`
     - Add test users (for testing)
     - Save and continue

5. Create OAuth Client ID:
   - Application type: "Web application"
   - Name: "FitSmart Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:5000` (for local development)
     - `https://fitsmart.ca` (for production)
   - Authorized redirect URIs:
     - `http://localhost:5000/login/google/callback` (for local development)
     - `https://fitsmart.ca/login/google/callback` (for production)
   - Click "Create"
   - Copy the **Client ID** and **Client Secret**

## Step 2: Configure Environment Variables

Add the following to your `.env` file:

```env
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
```

## Step 3: Run Database Migration

Run the migration script to add the `google_id` column to the user table:

```bash
python migrations/add_google_oauth.py
```

Or if using the virtual environment:

```bash
.\venv\Scripts\python.exe migrations\add_google_oauth.py
```

## Step 4: Restart the Application

Restart your Flask application to load the new configuration.

## Step 5: Test Google Authentication

1. Go to the login page: http://localhost:5000/login
2. Click "Sign in with Google"
3. You should be redirected to Google's login page
4. After authentication, you'll be redirected back and logged in

## Features

- **Automatic Account Creation**: New users are automatically created when they sign in with Google
- **Account Linking**: If a user with the same email exists, the Google account is linked
- **Email Verification**: Google-authenticated users have their email automatically verified
- **Secure**: Uses OAuth 2.0 with state parameter for CSRF protection

## Troubleshooting

### Google login button not showing
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in `.env`
- Restart the Flask application

### "Invalid redirect URI" error
- Make sure the redirect URI in Google Console matches exactly:
  - `http://localhost:5000/login/google/callback` (local)
  - `https://fitsmart.ca/login/google/callback` (production)

### "Access blocked" error
- Make sure the OAuth consent screen is configured
- Add your email as a test user if the app is in testing mode
- Wait for Google to verify your app (can take a few days for production)

### Database errors
- Run the migration script: `python migrations/add_google_oauth.py`
- Make sure the database is accessible and writable

## Security Notes

- Never commit `.env` file with real credentials
- Use different OAuth credentials for development and production
- Regularly rotate your OAuth client secret
- Monitor OAuth usage in Google Cloud Console

