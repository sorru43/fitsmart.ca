#!/bin/bash

# Quick OAuth Setup Script for FitSmart
# This script helps you set up Google OAuth step by step

echo "=========================================="
echo "  FitSmart OAuth Setup Assistant"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating one..."
    touch .env
    echo "✅ Created .env file"
    echo ""
fi

# Check if Google OAuth variables are set
if grep -q "GOOGLE_CLIENT_ID" .env && grep -q "GOOGLE_CLIENT_SECRET" .env; then
    CLIENT_ID=$(grep "GOOGLE_CLIENT_ID" .env | cut -d '=' -f2)
    CLIENT_SECRET=$(grep "GOOGLE_CLIENT_SECRET" .env | cut -d '=' -f2)
    
    if [ -n "$CLIENT_ID" ] && [ "$CLIENT_ID" != "your-client-id-here.apps.googleusercontent.com" ] && \
       [ -n "$CLIENT_SECRET" ] && [ "$CLIENT_SECRET" != "your-client-secret-here" ]; then
        echo "✅ Google OAuth credentials found in .env"
        echo "   Client ID: ${CLIENT_ID:0:30}..."
        echo ""
    else
        echo "⚠️  Google OAuth credentials found but appear to be placeholders"
        echo "   Please update .env with your actual credentials"
        echo ""
    fi
else
    echo "⚠️  Google OAuth credentials not found in .env"
    echo ""
    echo "Please add these lines to your .env file:"
    echo "  GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com"
    echo "  GOOGLE_CLIENT_SECRET=your-client-secret-here"
    echo ""
    read -p "Would you like to add them now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Google Client ID: " CLIENT_ID
        read -p "Enter your Google Client Secret: " CLIENT_SECRET
        
        echo "" >> .env
        echo "# Google OAuth Configuration" >> .env
        echo "GOOGLE_CLIENT_ID=$CLIENT_ID" >> .env
        echo "GOOGLE_CLIENT_SECRET=$CLIENT_SECRET" >> .env
        
        echo "✅ Added credentials to .env"
        echo ""
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found"
    echo "   Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if migration script exists
if [ -f "migrations/add_google_oauth.py" ]; then
    echo ""
    echo "🔄 Running database migration..."
    python migrations/add_google_oauth.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Database migration completed"
    else
        echo "❌ Database migration failed. Please check the error above."
        exit 1
    fi
else
    echo "⚠️  Migration script not found: migrations/add_google_oauth.py"
    echo "   Skipping database migration"
fi

echo ""
echo "=========================================="
echo "  Setup Summary"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Make sure your Google OAuth credentials are correct in .env"
echo "2. Verify redirect URIs in Google Cloud Console:"
echo "   - https://fitsmart.ca/login/google/callback"
echo "3. Restart your application:"
echo "   source venv/bin/activate"
echo "   venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app"
echo ""
echo "For detailed instructions, see: OAUTH_SETUP_COMPLETE.md"
echo ""
echo "✅ Setup script completed!"

