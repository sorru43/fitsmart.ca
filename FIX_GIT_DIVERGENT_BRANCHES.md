# Fix Git Divergent Branches

## Problem
Git has divergent branches - your local branch and remote branch have different commits.

## Solution Options

### Option 1: Merge (Recommended - Keeps Both Local and Remote Changes)

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Set merge strategy
git config pull.rebase false

# Pull with merge
git pull origin main

# If there are conflicts, resolve them, then:
git add .
git commit -m "Merge remote changes"
```

### Option 2: Rebase (Cleaner History - Applies Your Changes on Top)

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Set rebase strategy
git config pull.rebase true

# Pull with rebase
git pull origin main

# If there are conflicts, resolve them, then:
git add .
git rebase --continue
```

### Option 3: Reset to Match Remote (⚠️ Loses Local Changes)

**WARNING: This will discard any local commits not pushed to remote!**

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# See what will be lost
git log HEAD..origin/main

# If you're sure, reset to match remote exactly
git fetch origin
git reset --hard origin/main
```

### Option 4: Stash Local Changes First (Safest)

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Save your local changes
git stash

# Pull remote changes
git pull origin main

# Apply your local changes back
git stash pop

# If there are conflicts, resolve them, then:
git add .
git commit -m "Merge stashed changes with remote"
```

## Recommended: Option 1 (Merge)

For a production server, I recommend Option 1 (merge) as it's the safest:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca
git config pull.rebase false
git pull origin main
```

If you get conflicts, you'll need to resolve them manually.

## After Resolving

Once the pull is successful:

```bash
# Restart your server
pkill -f gunicorn; sleep 2; source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

