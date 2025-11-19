# Add stripe_customer_id Column to User Table

## Problem
The database doesn't have the `stripe_customer_id` column in the `user` table, even though it's in the model.

Error: `sqlalchemy.exc.OperationalError: no such column: user.stripe_customer_id`

## Solution: Create and Run Migration

### Step 1: Create Migration

Run these commands on your server:

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca

# Activate virtual environment
source venv/bin/activate

# Set Flask app (if not already set)
export FLASK_APP=app.py

# Create migration
flask db migrate -m "Add stripe_customer_id to User model"
```

### Step 2: Review Migration

The migration file will be created in `migrations/versions/`. Check it to make sure it looks correct:

```bash
# View the latest migration file
ls -lt migrations/versions/ | head -1
```

The migration should add a column like:
```python
op.add_column('user', sa.Column('stripe_customer_id', sa.String(length=100), nullable=True))
```

### Step 3: Apply Migration

```bash
# Apply the migration to your database
flask db upgrade
```

### Step 4: Verify

```bash
# Check if column was added (SQLite)
sqlite3 instance/healthyrizz.db "PRAGMA table_info(user);" | grep stripe_customer_id

# Or check via Python
python
>>> from app import create_app
>>> from database.models import User
>>> app = create_app()
>>> with app.app_context():
...     print(User.__table__.columns.keys())  # Should include 'stripe_customer_id'
```

### Step 5: Restart Server

```bash
pkill -f gunicorn; sleep 2; source venv/bin/activate && venv/bin/gunicorn -w 4 -b 0.0.0.0:9000 --timeout 120 wsgi:app
```

## Alternative: Manual SQL (If Migration Fails)

If Flask-Migrate doesn't work, you can add the column manually:

```bash
# For SQLite
sqlite3 instance/healthyrizz.db "ALTER TABLE user ADD COLUMN stripe_customer_id VARCHAR(100);"

# For MySQL/MariaDB
mysql -u your_user -p your_database
ALTER TABLE user ADD COLUMN stripe_customer_id VARCHAR(100) NULL;
CREATE INDEX ix_user_stripe_customer_id ON user(stripe_customer_id);
```

## Quick One-Liner

```bash
cd /home/fitsmart/htdocs/www.fitsmart.ca && source venv/bin/activate && export FLASK_APP=app.py && flask db migrate -m "Add stripe_customer_id to User" && flask db upgrade
```

## Troubleshooting

### If migration says "Target database is not up to date"

```bash
# Check current migration status
flask db current

# If needed, stamp the database
flask db stamp head

# Then create and apply migration
flask db migrate -m "Add stripe_customer_id to User"
flask db upgrade
```

### If migration file is empty

The migration might not detect the change. You can manually edit the migration file to add:

```python
def upgrade():
    op.add_column('user', sa.Column('stripe_customer_id', sa.String(length=100), nullable=True, unique=True))
    op.create_index(op.f('ix_user_stripe_customer_id'), 'user', ['stripe_customer_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_user_stripe_customer_id'), table_name='user')
    op.drop_column('user', 'stripe_customer_id')
```

