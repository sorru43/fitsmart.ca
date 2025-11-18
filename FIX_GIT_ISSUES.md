# Fix Git Issues - Step by Step Guide

## Problem
You're getting errors when trying to pull from Git:
1. Database file `instance/healthyrizz.db` has local changes
2. Git authentication issues

## Solution

### Step 1: Remove Database File from Git Tracking

The database file shouldn't be in version control. Run these commands:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Remove the database file from git tracking (but keep the local file)
git rm --cached instance/healthyrizz.db

# If the file doesn't need to be tracked at all, you can delete it
# (it will be recreated when the app runs)
rm -f instance/healthyrizz.db
```

### Step 2: Commit the .gitignore Changes

```bash
# Add the new .gitignore file
git add .gitignore

# Commit the changes
git commit -m "Add .gitignore and remove database files from tracking"
```

### Step 3: Stash or Discard Local Changes

If you have other local changes you want to keep:

```bash
# Stash local changes (saves them for later)
git stash

# Or if you want to discard all local changes:
git reset --hard HEAD
```

### Step 4: Fix Git Remote (if needed)

Check your remote configuration:

```bash
# Check current remote
git remote -v

# If the remote is wrong or missing, set it:
git remote set-url origin https://github.com/sorru43/fitsmart.ca.git

# Or if using SSH:
git remote set-url origin git@github.com:sorru43/fitsmart.ca.git
```

### Step 5: Pull Latest Changes

Now try pulling again:

```bash
git pull origin main
```

### Step 6: If Authentication Fails

If you still get authentication errors:

**Option A: Use Personal Access Token (Recommended)**
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` permissions
3. Use it as password when Git asks:

```bash
git pull origin main
# Username: sorru43
# Password: [paste your personal access token]
```

**Option B: Use SSH Key**
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add to GitHub: Settings → SSH and GPG keys
3. Change remote to SSH: `git remote set-url origin git@github.com:sorru43/fitsmart.ca.git`

## Quick Fix Script

Run this all at once:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Remove database from tracking
git rm --cached instance/healthyrizz.db 2>/dev/null || true

# Add .gitignore
git add .gitignore

# Stash any other changes
git stash

# Pull latest
git pull origin main

# If you stashed changes and want them back:
# git stash pop
```

## After Fixing

1. Make sure `.env` file is NOT in git (it should be in .gitignore)
2. Add your Stripe keys to `.env` file (see QUICK_STRIPE_FIX.md)
3. Restart your application

## Important Notes

- **Never commit** `.env` files (they contain secrets)
- **Never commit** database files (they're too large and change frequently)
- The `.gitignore` file I created will prevent these issues in the future

