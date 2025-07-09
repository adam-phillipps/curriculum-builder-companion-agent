"""create_learning_outcomes_table

Revision ID: 971526241a06
Revises: ce93d66aa6e0
Create Date: 2025-07-09 21:01:52.892453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '971526241a06'
down_revision = 'ce93d66aa6e0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create learning_outcomes table
    op.create_table('learning_outcomes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain', sa.String(100), nullable=False),
        sa.Column('difficulty_level', sa.String(20), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='approved'),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('embedding_vector', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.Index('ix_learning_outcomes_domain', 'domain'),
        sa.Index('ix_learning_outcomes_status', 'status')
    )


def downgrade() -> None:
    # Drop learning_outcomes table
    op.drop_table('learning_outcomes')