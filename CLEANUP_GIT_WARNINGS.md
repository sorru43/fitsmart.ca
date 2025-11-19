# Clean Up Git Warnings

## Warnings to Fix

1. Git garbage collection log file
2. Too many unreachable loose objects

## Commands to Run on Server

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Step 1: Remove the gc.log file
rm -f .git/gc.log

# Step 2: Clean up unreachable objects
git prune

# Step 3: Run garbage collection
git gc

# Step 4: Verify .gitignore includes database files
cat .gitignore | grep -i "\.db\|instance"

# Step 5: Verify database is not tracked
git status
# Should NOT show instance/healthyrizz.db
```

## Verify Everything is Working

```bash
# Check git status - should be clean
git status

# Check that database is ignored
git check-ignore instance/healthyrizz.db
# Should output: instance/healthyrizz.db

# Verify you have latest code
git log --oneline -5
```

## If Warnings Persist

The warnings are not critical, but you can clean them up:

```bash
# Force garbage collection
git gc --aggressive --prune=now

# Clean up reflog (optional, be careful)
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

## Important

- Your database file is safe and will remain on the server
- The warnings don't affect functionality
- Future git pulls won't conflict with the database

