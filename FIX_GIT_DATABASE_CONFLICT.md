# Fix Git Database File Conflict

## Problem
Git merge conflict with `instance/healthyrizz.db` - this is a binary database file that shouldn't be tracked in git.

## Solution: Remove Database from Git and Keep Local Version

Run these commands on your server:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Remove the database file from git tracking (keeps local file)
git rm --cached instance/healthyrizz.db

# Add to .gitignore to prevent future conflicts
echo "instance/*.db" >> .gitignore
echo "instance/healthyrizz.db" >> .gitignore

# Resolve the conflict by accepting local version
git checkout --ours instance/healthyrizz.db

# Add .gitignore if it was modified
git add .gitignore

# Complete the merge
git commit -m "Remove database file from git tracking"

# Pull again to get latest changes
git pull origin main
```

## Alternative: If Above Doesn't Work

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Abort current merge
git merge --abort

# Remove database from git
git rm --cached instance/healthyrizz.db

# Add to .gitignore
echo "instance/*.db" >> .gitignore
echo "instance/healthyrizz.db" >> .gitignore

# Commit the removal
git add .gitignore
git commit -m "Remove database file from git tracking"

# Pull again
git pull origin main
```

## Verify

After resolving, verify the database file is ignored:

```bash
git status
# Should NOT show instance/healthyrizz.db
```

## Important Notes

- The database file will remain on your server (not deleted)
- Future git pulls won't conflict with the database
- Make sure to backup your database before making changes
- The database should be managed separately, not through git

