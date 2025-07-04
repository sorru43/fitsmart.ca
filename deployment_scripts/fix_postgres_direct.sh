#!/bin/bash
# Direct PostgreSQL fix script for HealthyRizz database schema
# This script uses the postgres superuser to apply schema changes

echo "This script will use the postgres superuser to fix the database schema."
echo "This requires sudo access to run commands as the postgres user."
echo ""

# Get the database name
read -p "Enter the database name (e.g., healthyrizz_db): " dbname

# Prepare the SQL commands
cat > /tmp/fix_schema.sql << EOF
-- Add username column if it doesn't exist
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'user' AND column_name = 'username'
    ) THEN
        ALTER TABLE "user" ADD COLUMN username VARCHAR(64);
        UPDATE "user" SET username = email;
        ALTER TABLE "user" ALTER COLUMN username SET NOT NULL;
        RAISE NOTICE 'Username column added successfully.';
    ELSE
        RAISE NOTICE 'Username column already exists.';
    END IF;
    
    -- Add created_at column if it doesn't exist
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'user' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE "user" ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'created_at column added successfully.';
    ELSE
        RAISE NOTICE 'created_at column already exists.';
    END IF;
END
\$\$;
EOF

# Execute the SQL as postgres user
echo "Attempting to fix database schema as postgres superuser..."
sudo -u postgres psql "$dbname" -f /tmp/fix_schema.sql

# Clean up
rm /tmp/fix_schema.sql

echo ""
echo "Schema fix attempt complete. Check the output above for results."
echo "Now you can restart your application:"
echo "gunicorn main:app -b 127.0.0.1:8090"
