"""add_skill_assessments_for_sankey

Revision ID: 4f7bc6eba635
Revises: 004_add_user_system
Create Date: 2025-07-02 01:51:30.938480

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f7bc6eba635'
down_revision = '004_add_user_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_skill_assessments table
    op.create_table('user_skill_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('skill_category', sa.String(length=100), nullable=False),
        sa.Column('proficiency_level', sa.Float(), nullable=False),
        sa.Column('assessment_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for better query performance
    op.create_index('ix_skill_assessments_user_id', 'user_skill_assessments', ['user_id'])
    op.create_index('ix_skill_assessments_category', 'user_skill_assessments', ['skill_category'])


def downgrade() -> None:
    op.drop_index('ix_skill_assessments_category', table_name='user_skill_assessments')
    op.drop_index('ix_skill_assessments_user_id', table_name='user_skill_assessments')
    op.drop_table('user_skill_assessments')