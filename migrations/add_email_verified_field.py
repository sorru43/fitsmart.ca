"""Add email_verified field to User model

Revision ID: add_email_verified_field
Revises: 
Create Date: 2025-01-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_email_verified_field'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Add email_verified column to user table"""
    # Add email_verified column with default value False
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    """Remove email_verified column from user table"""
    op.drop_column('user', 'email_verified')
