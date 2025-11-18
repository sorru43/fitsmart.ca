# Stripe Integration Setup Guide

This guide will help you set up Stripe payment processing for your FitSmart application.

## ✅ What's Already Configured

1. **Stripe Package**: Already installed in `requirements.txt` (stripe==7.11.0)
2. **Stripe Routes**: Blueprint created at `routes/stripe_routes.py`
3. **Stripe Utilities**: Helper functions in `utils/stripe_utils.py`
4. **Configuration**: Stripe config already in `config.py`
5. **Templates**: Stripe JS already integrated in checkout templates

## 🔧 Setup Steps

### 1. Get Your Stripe API Keys

1. Sign up or log in to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Go to **Developers** → **API keys**
3. Copy your **Publishable key** and **Secret key**
   - For testing, use **Test mode** keys
   - For production, use **Live mode** keys

### 2. Configure Environment Variables

Create a `.env` file in your project root (if it doesn't exist) and add:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Important Notes:**
- Replace `sk_test_...` with your actual Stripe secret key
- Replace `pk_test_...` with your actual Stripe publishable key
- The webhook secret will be generated when you set up webhooks (see step 4)

### 3. Set Up Stripe Webhooks

Webhooks allow Stripe to notify your application about payment events.

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/) → **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Enter your webhook URL:
   - **Local development**: Use [Stripe CLI](https://stripe.com/docs/stripe-cli) or [ngrok](https://ngrok.com/)
   - **Production**: `https://yourdomain.com/stripe-webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Copy the **Signing secret** (starts with `whsec_`) and add it to your `.env` file

### 4. Test the Integration

#### Test Mode
1. Use Stripe test cards:
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - Use any future expiry date, any CVC, any ZIP
2. Test the checkout flow on your site
3. Check Stripe Dashboard → **Payments** to see test transactions

#### Production Mode
1. Switch to live keys in your `.env` file
2. Update webhook endpoint to production URL
3. Test with real payment methods

## 📋 Available Stripe Routes

The following routes are available after setup:

- **POST** `/stripe-create-checkout-session/<plan_id>` - Create checkout session
- **GET** `/stripe-checkout-success` - Success page after payment
- **GET** `/stripe-checkout-cancel` - Cancel page if user cancels
- **GET** `/customer-portal` - Redirect to Stripe customer portal
- **POST** `/stripe-webhook` - Webhook endpoint (CSRF exempt)

## 🔍 Verification Checklist

- [ ] Stripe keys added to `.env` file
- [ ] Webhook endpoint configured in Stripe Dashboard
- [ ] Webhook secret added to `.env` file
- [ ] Test payment successful
- [ ] Webhook events received and processed
- [ ] Customer portal accessible
- [ ] Subscription management working

## 🐛 Troubleshooting

### "Stripe API key not configured" error
- Check that `STRIPE_SECRET_KEY` is set in `.env`
- Restart your Flask application after adding environment variables

### Webhook not receiving events
- Verify webhook URL is correct in Stripe Dashboard
- Check that `STRIPE_WEBHOOK_SECRET` matches the signing secret
- Ensure webhook endpoint is publicly accessible (use ngrok for local testing)
- Check application logs for webhook errors

### Checkout session not creating
- Verify both `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` are set
- Check that the meal plan exists and has valid pricing
- Review application logs for detailed error messages

### CSRF errors
- The webhook route is already exempt from CSRF protection
- If other routes have CSRF issues, ensure CSRF token is included in forms

## 📚 Additional Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Checkout Guide](https://stripe.com/docs/payments/checkout)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Testing Guide](https://stripe.com/docs/testing)

## 🔐 Security Notes

- **Never commit** your `.env` file to version control
- Use test keys for development, live keys only in production
- Keep your secret keys secure and rotate them periodically
- The webhook endpoint verifies signatures to ensure requests are from Stripe

