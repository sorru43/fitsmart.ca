# Fix Server Issues - Step by Step Guide

## Issues Found:
1. ✅ Git merge conflict (divergent branches)
2. ✅ AdditionalService error (already fixed in code, need to pull)
3. ⚠️ Stripe API key missing (needs .env configuration)
4. ⚠️ Circular import warning (non-critical, but can be fixed)

## Step 1: Fix Git Merge Issue

Run these commands on your server:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Remove database file from tracking
git rm --cached instance/healthyrizz.db

# Commit the removal
git commit -m "Remove database file from git tracking"

# Pull with merge strategy (use theirs for database file, ours for code)
git pull origin main --no-edit

# If that doesn't work, try:
git pull origin main --strategy-option=theirs instance/healthyrizz.db

# Or force pull (if you don't need local changes):
git fetch origin
git reset --hard origin/main
```

## Step 2: Verify AdditionalService Fix is Pulled

The AdditionalService error should be fixed in the latest code. After pulling, verify the fix is there:

```bash
# Check if the fix is in the file
grep -A 5 "get_additional_services" routes/main_routes.py | grep "ImportError"
```

You should see the ImportError handling code.

## Step 3: Configure Stripe API Key

The Stripe API key error means you need to add it to your `.env` file:

```bash
# Edit .env file
nano .env

# Add these lines (get your keys from https://dashboard.stripe.com/apikeys):
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Save and exit (Ctrl+X, then Y, then Enter)
```

**Important**: 
- Replace `sk_test_...` with your actual Stripe secret key
- Replace `pk_test_...` with your actual Stripe publishable key  
- Use `sk_test_` and `pk_test_` for testing, `sk_live_` and `pk_live_` for production

## Step 4: Restart Server

After making changes:

```bash
# Restart gunicorn
pkill -f gunicorn; sleep 2; source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

## Step 5: Verify Everything Works

Check the logs for:
- ✅ No AdditionalService errors
- ✅ No Stripe API key errors (after adding keys)
- ⚠️ Circular import warning is non-critical (blueprint still registers)

## Quick Fix Script

Run this all at once:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Fix git
git rm --cached instance/healthyrizz.db 2>/dev/null
git commit -m "Remove database from tracking" 2>/dev/null || true
git pull origin main --no-edit || git fetch origin && git reset --hard origin/main

# Restart server
pkill -f gunicorn; sleep 2; source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

## Notes:

- **Circular Import Warning**: This is non-critical. The blueprint still registers successfully. It's a warning, not an error.
- **AdditionalService**: Already fixed in code - just need to pull latest changes
- **Stripe Keys**: Must be added to `.env` file for Stripe to work
- **Database File**: Should not be in git - already in `.gitignore`

