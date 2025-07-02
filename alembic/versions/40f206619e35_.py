"""empty message

Revision ID: 40f206619e35
Revises: 005_add_career_role, e88729eae1aa
Create Date: 2025-07-02 13:11:34.379392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40f206619e35'
down_revision = ('005_add_career_role', 'e88729eae1aa')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass