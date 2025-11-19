# Fix Git Database File Issue

## Problem
Git is trying to merge changes to `instance/healthyrizz.db`, which is a database file that shouldn't be tracked in git.

## Solution

Run these commands on your server:

```bash
# 1. Remove the database file from git tracking (but keep the local file)
git rm --cached instance/healthyrizz.db

# 2. Make sure .gitignore includes database files (it already does - line 34-38)
# Verify: instance/*.db is already in .gitignore

# 3. Commit the removal
git commit -m "Remove database file from git tracking"

# 4. Now you can pull
git pull origin main

# 5. Restart your server
pkill -f gunicorn; sleep 2; source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

## Alternative: If you want to stash your local changes first

```bash
# Stash local changes
git stash

# Pull
git pull origin main

# Apply stashed changes (if needed)
git stash pop
```

## Note
The `.gitignore` file already includes:
- `*.db` (line 34)
- `instance/*.db` (line 38)

So database files should be ignored. The issue is that the file was committed before it was added to `.gitignore`. The `git rm --cached` command removes it from git tracking without deleting the actual file.

