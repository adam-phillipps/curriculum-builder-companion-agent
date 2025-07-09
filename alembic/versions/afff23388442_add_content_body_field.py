"""add_content_body_field

Revision ID: afff23388442
Revises: 40f206619e35
Create Date: 2025-07-09 02:41:48.686885

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afff23388442'
down_revision = '40f206619e35'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add content_body column to learning_content table
    op.add_column('learning_content', sa.Column('content_body', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove content_body column from learning_content table
    op.drop_column('learning_content', 'content_body')