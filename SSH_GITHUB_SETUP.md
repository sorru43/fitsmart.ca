# SSH Key Setup for GitHub on CloudPanel

This guide will help you set up SSH keys for GitHub authentication, which is more secure than HTTPS tokens.

## Step-by-Step Instructions

### Step 1: Generate SSH Key on Server

Run this command on your CloudPanel server:

```bash
ssh-keygen -t ed25519 -C "fitsmart-cloudpanel"
```

**When prompted:**
- **File location:** Press `Enter` to accept default (`~/.ssh/id_ed25519`)
- **Passphrase:** You can press `Enter` for no passphrase, or set one for extra security

**Example output:**
```
Generating public/private ed25519 key pair.
Enter file in which to save the key (/root/.ssh/id_ed25519): [Press Enter]
Enter passphrase (empty for no passphrase): [Press Enter or type passphrase]
Enter same passphrase again: [Press Enter or type passphrase again]
Your identification has been saved in /root/.ssh/id_ed25519
Your public key has been saved in /root/.ssh/id_ed25519.pub
```

### Step 2: Copy Your Public Key

Display your public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

**Copy the entire output** - it will look something like:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIG...fitsmart-cloudpanel
```

### Step 3: Add SSH Key to GitHub

1. **Go to GitHub:**
   - Visit: https://github.com/settings/keys
   - Or: GitHub → Settings → SSH and GPG keys

2. **Click "New SSH key"**

3. **Fill in the form:**
   - **Title:** `CloudPanel Server` (or any name you prefer)
   - **Key type:** `Authentication Key` (default)
   - **Key:** Paste the public key you copied in Step 2

4. **Click "Add SSH key"**

5. **Confirm with your GitHub password** (if prompted)

### Step 4: Test SSH Connection

Test if the SSH key works:

```bash
ssh -T git@github.com
```

**Expected output:**
```
Hi sorru43! You've successfully authenticated, but GitHub does not provide shell access.
```

If you see this message, your SSH key is working! ✅

### Step 5: Update Git Remote to Use SSH

Change your remote URL from HTTPS to SSH:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca
git remote set-url origin git@github.com:sorru43/fitsmart.ca.git
```

Verify the change:

```bash
git remote -v
```

You should see:
```
origin  git@github.com:sorru43/fitsmart.ca.git (fetch)
origin  git@github.com:sorru43/fitsmart.ca.git (push)
```

### Step 6: Test Git Operations

Now try pulling from GitHub:

```bash
git pull origin main --allow-unrelated-histories
```

Or if you need to push:

```bash
git push -u origin main
```

**No password prompt needed!** SSH keys authenticate automatically. 🎉

## Complete Setup Script

Here's a complete script you can run:

```bash
#!/bin/bash

# Navigate to project
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Fix ownership issue (if running as root)
git config --global --add safe.directory /home/fitsmart/htdocs/www.fitsmart.ca

# Generate SSH key (if not exists)
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "Generating SSH key..."
    ssh-keygen -t ed25519 -C "fitsmart-cloudpanel" -f ~/.ssh/id_ed25519 -N ""
    echo ""
    echo "=== YOUR PUBLIC KEY (copy this to GitHub) ==="
    cat ~/.ssh/id_ed25519.pub
    echo ""
    echo "=== Add this key to: https://github.com/settings/keys ==="
    read -p "Press Enter after adding the key to GitHub..."
fi

# Test SSH connection
echo "Testing SSH connection..."
ssh -T git@github.com

# Configure git
git config user.name "FitSmart"
git config user.email "122971823+sorru43@users.noreply.github.com"

# Set remote to SSH
git remote set-url origin git@github.com:sorru43/fitsmart.ca.git

# Rename branch if needed
git branch -m master main 2>/dev/null || true

echo ""
echo "Setup complete! You can now use git commands without passwords."
```

## Troubleshooting

### If SSH key generation fails:
```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

### If "Permission denied (publickey)" error:
1. Verify the key was added to GitHub correctly
2. Check the key is in the right format (should start with `ssh-ed25519`)
3. Try testing again: `ssh -T git@github.com`

### If you need to use a different SSH key:
```bash
# Generate with custom name
ssh-keygen -t ed25519 -C "fitsmart-cloudpanel" -f ~/.ssh/id_ed25519_fitsmart

# Add to SSH config
cat >> ~/.ssh/config << EOF
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_fitsmart
EOF
chmod 600 ~/.ssh/config
```

### If you have multiple GitHub accounts:
You can use SSH config to manage multiple keys. See the "different SSH key" section above.

## Advantages of SSH over HTTPS

✅ **More secure** - No tokens to manage  
✅ **No expiration** - Keys don't expire like tokens  
✅ **Automatic** - No password prompts  
✅ **Better for automation** - Works great with CI/CD  

## Quick Reference

```bash
# View your public key
cat ~/.ssh/id_ed25519.pub

# Test GitHub connection
ssh -T git@github.com

# Check remote URL
git remote -v

# Change to SSH (if using HTTPS)
git remote set-url origin git@github.com:sorru43/fitsmart.ca.git

# Change back to HTTPS (if needed)
git remote set-url origin https://github.com/sorru43/fitsmart.ca.git
```

