"""modify_learner_profiles_for_learning_outcomes

Revision ID: ac601e95c0d1
Revises: 971526241a06
Create Date: 2025-07-09 21:03:35.610970

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac601e95c0d1'
down_revision = '971526241a06'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add primary_learning_outcome_id column to learner_profiles
    op.add_column('learner_profiles', sa.Column('primary_learning_outcome_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_learner_profiles_primary_outcome', 'learner_profiles', 'learning_outcomes', ['primary_learning_outcome_id'], ['id'])
    
    # Note: keeping learning_goals as JSON for backward compatibility during transition
    # Will be deprecated once all users migrate to new outcome system


def downgrade() -> None:
    # Remove foreign key and column
    op.drop_constraint('fk_learner_profiles_primary_outcome', 'learner_profiles', type_='foreignkey')
    op.drop_column('learner_profiles', 'primary_learning_outcome_id')