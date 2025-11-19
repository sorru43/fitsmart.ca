# Automatic Recurring Payments Setup Guide

## Overview
FitSmart now supports automatic recurring payments for weekly and monthly subscriptions with email and SMS notifications.

## How It Works

### 1. Initial Subscription
- Customer subscribes and completes first payment via Stripe Checkout
- Subscription is created with Stripe subscription ID
- Customer receives confirmation email/SMS

### 2. Automatic Recurring Payments
- Stripe automatically charges the customer's saved payment method
- Payments occur based on subscription frequency (weekly or monthly)
- System receives webhook events and processes them automatically

### 3. Notifications Sent

#### Before Payment (Reminder)
- **Event**: `invoice.upcoming`
- **When**: 3 days before payment is due
- **Notification**: Email + SMS reminder to update payment method if needed

#### After Successful Payment
- **Event**: `invoice.payment_succeeded`
- **When**: Payment is successfully processed
- **Notification**: Email + SMS confirmation with next billing date
- **Action**: Subscription period updated, new order created

#### After Failed Payment
- **Event**: `invoice.payment_failed`
- **When**: Payment attempt fails
- **Notification**: Email + SMS alert with instructions to update payment
- **Action**: After 3 failed attempts, subscription is cancelled

## Stripe Webhook Setup

### Step 1: Configure Webhook Endpoint in Stripe Dashboard

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/) → **Developers** → **Webhooks**
2. Click **"Add endpoint"**
3. Enter your webhook URL:
   ```
   https://fitsmart.ca/stripe-webhook
   ```
   (For local testing: use Stripe CLI with `stripe listen --forward-to localhost:5000/stripe-webhook`)

### Step 2: Select Events to Listen For

Select these events in Stripe Dashboard:

**Required Events:**
- ✅ `checkout.session.completed` - Initial subscription creation
- ✅ `customer.subscription.updated` - Subscription status changes
- ✅ `customer.subscription.deleted` - Subscription cancellation
- ✅ `invoice.payment_succeeded` - **Recurring payment success**
- ✅ `invoice.payment_failed` - **Recurring payment failure**
- ✅ `invoice.upcoming` - **Payment reminder (3 days before)**

### Step 3: Get Webhook Signing Secret

1. After creating the webhook, click on it
2. Copy the **"Signing secret"** (starts with `whsec_`)
3. Add it to your `.env` file:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

### Step 4: Test Webhook

1. In Stripe Dashboard → Webhooks → Your endpoint
2. Click **"Send test webhook"**
3. Select event type (e.g., `invoice.payment_succeeded`)
4. Verify your application receives and processes it correctly

## Environment Variables Required

```env
# Stripe API Keys
STRIPE_SECRET_KEY=sk_live_... (or sk_test_... for testing)
STRIPE_PUBLISHABLE_KEY=pk_live_... (or pk_test_... for testing)
STRIPE_WEBHOOK_SECRET=whsec_...

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=no-reply@fitsmart.ca

# SMS Configuration (optional, for SMS notifications)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Payment Flow

### Weekly Subscription
1. Customer subscribes → First payment processed
2. Every 7 days → Stripe charges automatically
3. Webhook received → Order created, notification sent
4. Customer receives meals for the week

### Monthly Subscription
1. Customer subscribes → First payment processed
2. Every 30 days → Stripe charges automatically
3. Webhook received → Order created, notification sent
4. Customer receives meals for the month

## Notification Schedule

### Payment Reminder (3 Days Before)
- **Email**: Sent to customer's email
- **SMS**: Sent to customer's phone (if available)
- **Content**: Reminder about upcoming payment, amount, and due date
- **Action**: Customer can update payment method if needed

### Payment Success
- **Email**: Confirmation with payment details
- **SMS**: Short confirmation message
- **Content**: Amount paid, next billing date, subscription details
- **Action**: None required - subscription continues automatically

### Payment Failure
- **Email**: Alert with instructions
- **SMS**: Alert with link to update payment
- **Content**: Amount due, attempt number, instructions to fix
- **Action**: Customer must update payment method
- **After 3 failures**: Subscription automatically cancelled

## Testing

### Test with Stripe CLI (Local Development)

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:5000/stripe-webhook

# Trigger test events
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
stripe trigger invoice.upcoming
```

### Test in Stripe Dashboard

1. Go to **Developers** → **Webhooks**
2. Click on your webhook endpoint
3. Click **"Send test webhook"**
4. Select event type and send
5. Check your application logs for processing

## Monitoring

### Check Webhook Logs in Stripe
1. Go to **Developers** → **Webhooks** → Your endpoint
2. View **"Recent events"** to see all webhook attempts
3. Check for any failed deliveries

### Check Application Logs
```bash
# View webhook processing logs
tail -f /path/to/your/logs | grep "webhook"
```

## Troubleshooting

### Webhook Not Received
- ✅ Verify webhook URL is correct in Stripe Dashboard
- ✅ Check that `STRIPE_WEBHOOK_SECRET` is set correctly
- ✅ Ensure your server is accessible from the internet
- ✅ Check firewall settings

### Payments Not Processing
- ✅ Verify Stripe subscription is active in Stripe Dashboard
- ✅ Check customer's payment method is valid
- ✅ Verify webhook events are being received
- ✅ Check application logs for errors

### Notifications Not Sending
- ✅ Verify email/SMS credentials are configured
- ✅ Check email server settings
- ✅ Verify Twilio credentials (for SMS)
- ✅ Check application logs for email/SMS errors

## Security Notes

1. **Webhook Secret**: Never commit `STRIPE_WEBHOOK_SECRET` to version control
2. **Signature Verification**: Always verify webhook signatures (already implemented)
3. **HTTPS**: Use HTTPS in production for webhook endpoint
4. **Idempotency**: Webhook handler is idempotent (safe to retry)

## Customer Experience

### What Customers See

1. **Initial Subscription**: 
   - Complete checkout
   - Receive confirmation email/SMS
   - Subscription active

2. **Before Each Payment**:
   - Receive reminder 3 days before
   - Can update payment method if needed

3. **After Successful Payment**:
   - Receive confirmation email/SMS
   - See updated subscription period in account
   - Meals continue as scheduled

4. **If Payment Fails**:
   - Receive alert email/SMS
   - Instructions to update payment method
   - After 3 failures: Subscription cancelled

## Support

For issues or questions:
- Check Stripe Dashboard → Webhooks for delivery status
- Review application logs for processing errors
- Contact support: fitsmart.ca@gmail.com

---

**Last Updated**: 2025-11-19
**Version**: 1.0

