"""add_comprehension_percentage_to_user_content_progress

Revision ID: ce93d66aa6e0
Revises: afff23388442
Create Date: 2025-07-09 16:34:01.247348

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce93d66aa6e0'
down_revision = 'afff23388442'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add comprehension_percentage column to user_content_progress table
    op.add_column('user_content_progress', sa.Column('comprehension_percentage', sa.Float(), nullable=True, default=0.0))


def downgrade() -> None:
    # Remove comprehension_percentage column from user_content_progress table
    op.drop_column('user_content_progress', 'comprehension_percentage')