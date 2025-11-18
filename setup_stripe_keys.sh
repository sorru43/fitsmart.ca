#!/bin/bash

# Quick script to add Stripe keys to .env file
# Run this script to add or update Stripe configuration

PROJECT_DIR="/home/fitsmart/htdocs/www.fitsmart.ca"
ENV_FILE="$PROJECT_DIR/.env"

echo "=========================================="
echo "Stripe API Keys Setup"
echo "=========================================="
echo ""

cd "$PROJECT_DIR"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  .env file not found. Creating it..."
    touch "$ENV_FILE"
    echo "# Flask Configuration" >> "$ENV_FILE"
    echo "SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")" >> "$ENV_FILE"
    echo "" >> "$ENV_FILE"
fi

# Check if Stripe keys already exist
if grep -q "STRIPE_SECRET_KEY" "$ENV_FILE"; then
    echo "⚠️  STRIPE_SECRET_KEY already exists in .env"
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove old Stripe keys
        sed -i '/STRIPE_SECRET_KEY/d' "$ENV_FILE"
        sed -i '/STRIPE_PUBLISHABLE_KEY/d' "$ENV_FILE"
        sed -i '/STRIPE_WEBHOOK_SECRET/d' "$ENV_FILE"
    else
        echo "Keeping existing keys."
        exit 0
    fi
fi

echo ""
echo "Please enter your Stripe API keys:"
echo "(You can find these at https://dashboard.stripe.com/apikeys)"
echo ""

# Get Stripe Secret Key
read -p "Enter your Stripe SECRET KEY (starts with sk_test_ or sk_live_): " STRIPE_SECRET
if [ -z "$STRIPE_SECRET" ]; then
    echo "❌ Secret key is required. Exiting."
    exit 1
fi

# Get Stripe Publishable Key
read -p "Enter your Stripe PUBLISHABLE KEY (starts with pk_test_ or pk_live_): " STRIPE_PUBLISHABLE
if [ -z "$STRIPE_PUBLISHABLE" ]; then
    echo "❌ Publishable key is required. Exiting."
    exit 1
fi

# Get Webhook Secret (optional)
read -p "Enter your Stripe WEBHOOK SECRET (starts with whsec_, optional - press Enter to skip): " STRIPE_WEBHOOK

# Add keys to .env
echo "" >> "$ENV_FILE"
echo "# Stripe Configuration" >> "$ENV_FILE"
echo "STRIPE_SECRET_KEY=$STRIPE_SECRET" >> "$ENV_FILE"
echo "STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE" >> "$ENV_FILE"
if [ ! -z "$STRIPE_WEBHOOK" ]; then
    echo "STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK" >> "$ENV_FILE"
fi

echo ""
echo "✅ Stripe keys added to .env file!"
echo ""
echo "⚠️  IMPORTANT: Restart your application for changes to take effect:"
echo "   pkill -f gunicorn"
echo "   source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app"
echo ""

