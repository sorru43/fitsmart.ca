# Fix Migration Issues and Add stripe_customer_id Column

## Problem
- Migration system is out of sync
- Temporary table `_alembic_tmp_delivery` exists from failed migration
- Need to add `stripe_customer_id` column to `user` table

## Solution: Manual SQL (Simplest)

### Step 1: Clean Up Temporary Table

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Remove temporary table if it exists
sqlite3 instance/healthyrizz.db "DROP TABLE IF EXISTS _alembic_tmp_delivery;"
```

### Step 2: Add stripe_customer_id Column Manually

```bash
# Add the column
sqlite3 instance/healthyrizz.db "ALTER TABLE user ADD COLUMN stripe_customer_id VARCHAR(100);"

# Create index for better performance
sqlite3 instance/healthyrizz.db "CREATE INDEX IF NOT EXISTS ix_user_stripe_customer_id ON user(stripe_customer_id);"

# Verify it was added
sqlite3 instance/healthyrizz.db "PRAGMA table_info(user);" | grep stripe_customer_id
```

### Step 3: Stamp Database (Mark Migrations as Applied)

```bash
source venv/bin/activate
export FLASK_APP=app.py

# Check current migration state
flask db current

# Stamp database to current head (mark all migrations as applied)
flask db stamp head
```

### Step 4: Verify

```bash
# Check if column exists
sqlite3 instance/healthyrizz.db ".schema user" | grep stripe_customer_id

# Should show: stripe_customer_id VARCHAR(100)
```

### Step 5: Restart Server

```bash
pkill -f gunicorn; sleep 2; source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

## Complete Command Sequence

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Clean up
sqlite3 instance/healthyrizz.db "DROP TABLE IF EXISTS _alembic_tmp_delivery;"

# Add column
sqlite3 instance/healthyrizz.db "ALTER TABLE user ADD COLUMN stripe_customer_id VARCHAR(100);"

# Add index
sqlite3 instance/healthyrizz.db "CREATE INDEX IF NOT EXISTS ix_user_stripe_customer_id ON user(stripe_customer_id);"

# Stamp database
source venv/bin/activate
export FLASK_APP=app.py
flask db stamp head

# Verify
sqlite3 instance/healthyrizz.db "PRAGMA table_info(user);" | grep stripe_customer_id

# Restart
pkill -f gunicorn; sleep 2; source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

## Alternative: If Using MySQL/MariaDB

If your database is MySQL instead of SQLite:

```bash
mysql -u your_user -p your_database << EOF
DROP TABLE IF EXISTS _alembic_tmp_delivery;
ALTER TABLE user ADD COLUMN stripe_customer_id VARCHAR(100) NULL;
CREATE INDEX ix_user_stripe_customer_id ON user(stripe_customer_id);
EOF
```

## What This Does

1. **Drops temporary table** - Cleans up failed migration artifacts
2. **Adds column** - Adds `stripe_customer_id` to `user` table
3. **Creates index** - Improves query performance
4. **Stamps database** - Tells Flask-Migrate that migrations are up to date
5. **Restarts server** - Applies changes

## After This

The `stripe_customer_id` column will exist and the error should be resolved. The column will be `NULL` for existing users, which is fine - it will be populated when they create subscriptions.

