"""Add user system tables

Revision ID: 004_add_user_system
Revises: 003_add_learning_pathways
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004_add_user_system'
down_revision = 'acf408ade49f'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('current_role', sa.String(length=50), nullable=False, server_default='learner'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create learner_profiles table
    op.create_table('learner_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('learning_goals', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('target_outcomes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('current_pathway_id', sa.Integer(), nullable=True),
        sa.Column('skill_assessment', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('skill_levels', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_content_completed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_learning_hours', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['current_pathway_id'], ['learning_pathways.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_content_progress table
    op.create_table('user_content_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='not_started'),
        sa.Column('progress_percentage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.Column('outcome_score', sa.Integer(), nullable=True),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['learning_content.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('user_content_progress')
    op.drop_table('learner_profiles')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')