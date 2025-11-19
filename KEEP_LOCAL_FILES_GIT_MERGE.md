# Keep Local Files - Git Merge Strategy

## Goal: Keep your local server files and merge with remote

## Step-by-Step Instructions

### Step 1: Check what's different
```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# See what files are different
git status

# See your local commits
git log --oneline -5

# See remote commits
git fetch origin
git log --oneline origin/main -5
```

### Step 2: Merge with strategy to keep local files
```bash
# Set merge strategy to merge (not rebase)
git config pull.rebase false

# Pull and merge - this will try to merge both
git pull origin main
```

### Step 3: If there are conflicts, keep your local version

If Git shows conflicts, you can keep your local version for all files:

```bash
# Keep your local version for all conflicted files
git checkout --ours .

# Or keep local for specific files:
# git checkout --ours path/to/file

# Then add and commit
git add .
git commit -m "Merge: Keep local server files"
```

### Alternative: Use merge strategy to prefer local

```bash
# Pull with strategy to prefer local changes
git pull origin main -X ours

# This automatically keeps your local version when there are conflicts
```

## Complete Command Sequence

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Set merge strategy
git config pull.rebase false

# Pull with strategy to keep local files on conflicts
git pull origin main -X ours

# If successful, you're done!
# If there are still issues, check status:
git status
```

## What This Does

- `-X ours`: When there are conflicts, automatically keep your local (server) version
- Your local files will be preserved
- Remote changes that don't conflict will be merged in
- You keep all your server-specific configurations

## After Merging

```bash
# Restart server
pkill -f gunicorn; sleep 2; source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

