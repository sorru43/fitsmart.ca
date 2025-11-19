# Quick Fix: Stripe API Key Error

## The Problem
You're seeing this error:
```
ERROR:root:Error creating Stripe customer: No API key provided.
```

This means your `STRIPE_SECRET_KEY` is not set in your `.env` file.

## Quick Fix (3 Steps)

### Step 1: Add Stripe Keys to .env File

SSH into your server and edit the `.env` file:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca
nano .env
```

### Step 2: Add These Lines

Add these lines to your `.env` file (get your keys from https://dashboard.stripe.com/apikeys):

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Important:**
- Replace `sk_test_...` with your actual Stripe secret key
- Replace `pk_test_...` with your actual Stripe publishable key
- The webhook secret is optional (you'll get it when setting up webhooks)
- Use **test keys** (`sk_test_` and `pk_test_`) for development
- Use **live keys** (`sk_live_` and `pk_live_`) for production

### Step 3: Restart Your Application

After adding the keys, restart your Gunicorn server:

```bash
# Stop current server
pkill -f gunicorn

# Wait a moment
sleep 2

# Start server again
cd /home/fitsmart/htdocs/www.fitsmart.ca
source venv/bin/activate
venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

Or use your existing restart command from the `commands` file.

## Alternative: Use the Setup Script

I've created a helper script. Run:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca
bash setup_stripe_keys.sh
```

This will guide you through adding the keys interactively.

## Verify It's Working

After restarting, try the checkout process again. The error should be gone.

## Where to Get Your Stripe Keys

1. Go to https://dashboard.stripe.com/
2. Click **Developers** → **API keys**
3. Copy:
   - **Secret key** (starts with `sk_test_` or `sk_live_`)
   - **Publishable key** (starts with `pk_test_` or `pk_live_`)

## Need Help?

If you still see errors after adding the keys:
1. Make sure there are **no quotes** around the keys in `.env`
2. Make sure there are **no extra spaces**
3. Make sure you **restarted** the application
4. Check the logs to see if the key is being loaded

