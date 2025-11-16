# CloudPanel GitHub Connection Guide

This guide will help you connect your CloudPanel project to GitHub.

## Prerequisites
- GitHub repository: `https://github.com/sorru43/fitsmart.ca.git`
- Access to CloudPanel server via SSH
- Git installed on the server

## Step 1: Check Git Status on Server

First, check if git is already initialized in your project directory:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca
git status
```

## Step 2: Initialize Git (if needed)

If git is not initialized, run:

```bash
git init
```

## Step 3: Add GitHub Remote

Add your GitHub repository as the remote origin:

```bash
git remote add origin https://github.com/sorru43/fitsmart.ca.git
```

Or if it already exists, update it:

```bash
git remote set-url origin https://github.com/sorru43/fitsmart.ca.git
```

Check the remote:

```bash
git remote -v
```

## Step 4: Authentication Setup

You have two options for authentication:

### Option A: HTTPS with Personal Access Token (Recommended for CloudPanel)

1. **Create a GitHub Personal Access Token:**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic)
   - Select scopes: `repo` (full control of private repositories)
   - Copy the token

2. **Configure Git Credentials:**
   ```bash
   git config --global credential.helper store
   ```

3. **When you push/pull, use the token as password:**
   - Username: `sorru43` (or your GitHub username)
   - Password: `[your-personal-access-token]`

### Option B: SSH Keys (More Secure)

1. **Generate SSH Key on Server:**
   ```bash
   ssh-keygen -t ed25519 -C "fitsmart-cloudpanel"
   # Press Enter to accept default location
   # Optionally set a passphrase
   ```

2. **Copy Public Key:**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

3. **Add to GitHub:**
   - Go to GitHub → Settings → SSH and GPG keys
   - Click "New SSH key"
   - Paste the public key
   - Save

4. **Update Remote to Use SSH:**
   ```bash
   git remote set-url origin git@github.com:sorru43/fitsmart.ca.git
   ```

5. **Test Connection:**
   ```bash
   ssh -T git@github.com
   ```

## Step 5: Configure Git User (if needed)

```bash
git config user.name "FitSmart"
git config user.email "122971823+sorru43@users.noreply.github.com"
```

## Step 6: Pull from GitHub

If the repository already exists on GitHub, pull the code:

```bash
git pull origin main
# or
git pull origin master
```

If there are conflicts, you may need to:

```bash
git fetch origin
git branch -a  # Check available branches
git checkout -b main origin/main  # or master
```

## Step 7: Push to GitHub

After making changes, push to GitHub:

```bash
git add .
git commit -m "Initial commit from CloudPanel"
git push -u origin main  # or master
```

## Common Commands

```bash
# Check status
git status

# Check remote
git remote -v

# Pull latest changes
git pull origin main

# Push changes
git push origin main

# View branches
git branch -a

# Switch branch
git checkout main
```

## Troubleshooting

### If you get "permission denied" errors:
- Check your GitHub token/SSH key is set up correctly
- Verify you have write access to the repository

### If you get "refusing to merge unrelated histories":
```bash
git pull origin main --allow-unrelated-histories
```

### If you need to force push (use with caution):
```bash
git push -f origin main
```

## Automated Setup Script

See `setup_github_connection.sh` for an automated setup script.

