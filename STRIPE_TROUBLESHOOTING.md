# Stripe Customer Creation Error - Troubleshooting Guide

## Common Causes & Solutions

### 1. **Stripe API Key Not Configured**

**Error:** "Stripe API key not configured"

**Solution:**
- Check your `.env` file has `STRIPE_SECRET_KEY` set
- Make sure the key starts with `sk_test_` (test) or `sk_live_` (production)
- Restart your Flask application after adding the key

**Verify:**
```bash
# Check if key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key exists:', bool(os.getenv('STRIPE_SECRET_KEY')))"
```

### 2. **Invalid API Key Format**

**Error:** Stripe API errors with authentication

**Solution:**
- Ensure you copied the **entire** key (they're long strings)
- No extra spaces or quotes around the key
- Use test keys for development: `sk_test_...`
- Use live keys only in production: `sk_live_...`

**Example `.env` format:**
```env
STRIPE_SECRET_KEY=sk_test_51AbC123xyz789...
STRIPE_PUBLISHABLE_KEY=pk_test_51AbC123xyz789...
```

### 3. **Address Format Issues**

**Error:** Stripe API errors related to address

**Solution:**
- Ensure `customer_address` is not empty
- Address should be in `line1` format (not `line_1`)
- All address fields should be strings

**Check your form:**
- Make sure the address field is being submitted correctly
- Verify the form field name matches: `customer_address`

### 4. **Network/Connection Issues**

**Error:** Timeout or connection errors

**Solution:**
- Check your internet connection
- Verify Stripe API is accessible: https://status.stripe.com/
- Check firewall/proxy settings

### 5. **Check Application Logs**

The improved error handling now logs detailed information. Check your application logs for:

```python
# Look for these log messages:
"Stripe API error creating customer: [error message] (Code: [code])"
"Error creating Stripe customer: [error] (Type: [type])"
```

## Quick Diagnostic Steps

1. **Verify API Key is Loaded:**
   ```python
   # In Python shell or add to a test route
   from utils.stripe_utils import get_stripe_api_key
   key = get_stripe_api_key()
   print(f"Key loaded: {bool(key)}")
   print(f"Key starts with sk_: {key.startswith('sk_') if key else False}")
   ```

2. **Test Stripe Connection:**
   ```python
   import stripe
   stripe.api_key = "your_test_key_here"
   try:
       customer = stripe.Customer.create(
           name="Test User",
           email="test@example.com"
       )
       print(f"Success! Customer ID: {customer.id}")
   except Exception as e:
       print(f"Error: {e}")
   ```

3. **Check Form Data:**
   - Open browser developer tools (F12)
   - Go to Network tab
   - Submit the checkout form
   - Check the request payload to see what data is being sent

## Most Likely Issue

Based on the error "Error creating customer. Please try again.", the most common cause is:

**Missing or incorrect `STRIPE_SECRET_KEY` in `.env` file**

### Fix:
1. Open your `.env` file
2. Add or update:
   ```env
   STRIPE_SECRET_KEY=sk_test_your_actual_key_here
   ```
3. Make sure there are no quotes around the key
4. Restart your Flask application
5. Try again

## Need More Help?

Check the application logs for the detailed error message. The improved error handling will show:
- The exact Stripe error code
- The error message from Stripe
- Whether it's an API key issue or a data validation issue

