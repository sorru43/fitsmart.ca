# Fix Branch Mismatch (master vs main)

Your local branch is `master` but GitHub uses `main`. Here's how to fix it:

## Option 1: Switch to main branch (Recommended)

```bash
# Checkout the main branch from remote
git checkout -b main origin/main

# Or if main already exists locally:
git checkout main
```

## Option 2: Rename master to main

```bash
# Rename your local master branch to main
git branch -m master main

# Set upstream to track origin/main
git branch --set-upstream-to=origin/main main
```

## After fixing, verify:

```bash
# Check current branch
git branch

# Should show: * main

# Check status
git status
```

## Then you can push:

```bash
# If you have changes to commit
git add .
git commit -m "Your commit message"
git push origin main

# Or just push if already committed
git push origin main
```

