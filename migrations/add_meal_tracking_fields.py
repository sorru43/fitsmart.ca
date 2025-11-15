#!/usr/bin/env python3
"""
Migration: Add meal tracking fields to Subscription model
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    """Add meal tracking fields to subscriptions table"""
    
    # Add meal tracking columns
    op.add_column('subscriptions', sa.Column('meals_delivered_this_period', sa.Integer(), nullable=True, default=0))
    op.add_column('subscriptions', sa.Column('meals_remaining_this_period', sa.Integer(), nullable=True, default=0))
    op.add_column('subscriptions', sa.Column('total_meals_promised_this_period', sa.Integer(), nullable=True, default=0))
    op.add_column('subscriptions', sa.Column('next_payment_date', sa.DateTime(), nullable=True))
    op.add_column('subscriptions', sa.Column('payment_reminder_sent', sa.Boolean(), nullable=True, default=False))
    op.add_column('subscriptions', sa.Column('last_payment_reminder_date', sa.DateTime(), nullable=True))
    
    # Create index for performance
    op.create_index('idx_subscriptions_meal_tracking', 'subscriptions', ['meals_remaining_this_period', 'payment_reminder_sent'])

def downgrade():
    """Remove meal tracking fields from subscriptions table"""
    
    # Drop index
    op.drop_index('idx_subscriptions_meal_tracking', 'subscriptions')
    
    # Drop columns
    op.drop_column('subscriptions', 'last_payment_reminder_date')
    op.drop_column('subscriptions', 'payment_reminder_sent')
    op.drop_column('subscriptions', 'next_payment_date')
    op.drop_column('subscriptions', 'total_meals_promised_this_period')
    op.drop_column('subscriptions', 'meals_remaining_this_period')
    op.drop_column('subscriptions', 'meals_delivered_this_period')
