#!/bin/bash

# Complete SSH Setup Script for CloudPanel
# Run this after generating your SSH key

set -e

PROJECT_DIR="/home/fitsmart/htdocs/www.fitsmart.ca"

echo "=== Fixing Git Ownership Issue ==="
git config --global --add safe.directory "$PROJECT_DIR"

# Verify it was added
echo ""
echo "=== Verifying safe directory ==="
git config --global --get-all safe.directory | grep "$PROJECT_DIR" && echo "✓ Safe directory configured" || echo "⚠ Warning: Could not verify"

echo ""
echo "=== Your SSH Public Key ==="
echo "Copy this key and add it to GitHub:"
echo ""
cat ~/.ssh/id_ed25519.pub
echo ""
echo "=== Next Steps ==="
echo "1. Go to: https://github.com/settings/keys"
echo "2. Click 'New SSH key'"
echo "3. Paste the key above"
echo "4. Save"
echo ""
echo "Then run: ssh -T git@github.com"
echo ""

