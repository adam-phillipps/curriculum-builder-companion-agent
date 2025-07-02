"""Add career_role field to users table

Revision ID: 005_add_career_role
Revises: 004_add_user_system
Create Date: 2025-01-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '005_add_career_role'
down_revision = '004_add_user_system'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add career_role column to users table
    op.add_column('users', sa.Column('career_role', sa.String(length=50), nullable=True))

def downgrade() -> None:
    # Remove career_role column from users table
    op.drop_column('users', 'career_role')