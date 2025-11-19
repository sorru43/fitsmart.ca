# Stripe Checkout Session Error - Troubleshooting Guide

## Error Message
"Error creating checkout session. Please try again."

## Common Causes & Solutions

### 1. **Stripe API Key Not Configured** ⚠️ MOST COMMON

**Symptoms:**
- Error in logs: "Stripe API key not configured"
- Error: "No API key provided"

**Solution:**
```bash
# Edit .env file
nano .env

# Add these lines:
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Restart server
pkill -f gunicorn; sleep 2; source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

**Get your keys from:** https://dashboard.stripe.com/apikeys

### 2. **Invalid API Key Format**

**Symptoms:**
- Stripe errors about authentication
- API key doesn't start with `sk_test_` or `sk_live_`

**Solution:**
- Ensure the key starts with `sk_test_` (test) or `sk_live_` (production)
- No extra spaces or quotes around the key
- Copy the entire key (they're long strings)

### 3. **Customer Creation Failed**

**Symptoms:**
- Error: "Failed to create Stripe customer"
- Checkout fails before creating session

**Check:**
- Customer email is valid
- Customer address is properly formatted
- Phone number is valid

### 4. **Invalid Price Amount**

**Symptoms:**
- Stripe errors about price validation
- Price is 0 or negative

**Check:**
- Meal plan has price set for weekly/monthly
- Price is greater than 0
- Coupon discount doesn't exceed total

### 5. **Invalid URLs**

**Symptoms:**
- Stripe errors about success_url or cancel_url

**Check:**
- URLs are absolute (start with http:// or https://)
- URLs are accessible
- No typos in URL paths

### 6. **Stripe Account Issues**

**Symptoms:**
- Account not activated
- Test mode vs Live mode mismatch

**Solution:**
- Ensure test keys for test mode, live keys for production
- Activate your Stripe account if needed
- Check Stripe dashboard for account status

## How to Debug

### Check Server Logs

```bash
# View recent logs
tail -f /var/log/gunicorn/error.log

# Or if using systemd
journalctl -u gunicorn -f

# Or check application logs
tail -f /home/fitsmart/htdocs/www.fitsmart.ca/logs/app.log
```

### Look for These Error Messages:

1. **"Stripe API key not configured"** → Add API key to .env
2. **"No API key provided"** → API key missing or invalid
3. **"Invalid API Key"** → Wrong key format or wrong key
4. **"Failed to create Stripe customer"** → Customer creation issue
5. **"Error creating Stripe checkout session"** → Check detailed error in logs

### Test Stripe Connection

```python
# Test in Python shell
python
>>> import stripe
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>> stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
>>> stripe.Customer.list(limit=1)  # Should work if key is valid
```

## Quick Fix Checklist

- [ ] STRIPE_SECRET_KEY is set in .env file
- [ ] STRIPE_PUBLISHABLE_KEY is set in .env file
- [ ] API key starts with `sk_test_` or `sk_live_`
- [ ] No extra spaces/quotes around API key
- [ ] Server restarted after adding keys
- [ ] Stripe account is active
- [ ] Using test keys in test mode, live keys in production

## Most Likely Issue

Based on your earlier error logs showing "No API key provided", the most likely issue is:

**Missing or incorrectly configured STRIPE_SECRET_KEY in .env file**

Fix it by:
1. Adding the key to .env
2. Restarting the server
3. Testing checkout again

## After Fixing

The improved error handling will now show more specific error messages in the server logs. Check the logs to see the exact Stripe error for better debugging.

