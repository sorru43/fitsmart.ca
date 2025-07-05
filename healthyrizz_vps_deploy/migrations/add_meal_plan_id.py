"""Add meal_plan_id to subscriptions table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'add_meal_plan_id'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add meal_plan_id column to subscriptions table
    op.add_column('subscriptions', sa.Column('meal_plan_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_subscription_meal_plan',
        'subscriptions', 'meal_plan',
        ['meal_plan_id'], ['id']
    )

def downgrade():
    # Remove foreign key constraint
    op.drop_constraint('fk_subscription_meal_plan', 'subscriptions', type_='foreignkey')
    
    # Remove meal_plan_id column
    op.drop_column('subscriptions', 'meal_plan_id') 