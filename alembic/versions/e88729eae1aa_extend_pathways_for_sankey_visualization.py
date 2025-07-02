"""extend_pathways_for_sankey_visualization

Revision ID: e88729eae1aa
Revises: 4f7bc6eba635
Create Date: 2025-07-02 02:08:24.063741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e88729eae1aa'
down_revision = '4f7bc6eba635'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to learning_pathways for user connection and progress tracking
    op.add_column('learning_pathways', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('learning_pathways', sa.Column('completion_percentage', sa.Float(), server_default='0.0'))
    op.create_foreign_key('fk_pathways_user_id', 'learning_pathways', 'users', ['user_id'], ['id'])
    
    # Add missing columns to pathway_items for Sankey weights and progress
    op.add_column('pathway_items', sa.Column('weight', sa.Float(), server_default='1.0'))
    op.add_column('pathway_items', sa.Column('prerequisite_ids', sa.Text(), server_default='[]'))
    op.add_column('pathway_items', sa.Column('completion_status', sa.String(50), server_default='not_started'))
    op.add_column('pathway_items', sa.Column('completion_percentage', sa.Float(), server_default='0.0'))
    op.add_column('pathway_items', sa.Column('time_spent_minutes', sa.Integer(), server_default='0'))
    op.add_column('pathway_items', sa.Column('success_score', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('pathway_items', 'success_score')
    op.drop_column('pathway_items', 'time_spent_minutes')
    op.drop_column('pathway_items', 'completion_percentage')
    op.drop_column('pathway_items', 'completion_status')
    op.drop_column('pathway_items', 'prerequisite_ids')
    op.drop_column('pathway_items', 'weight')
    op.drop_constraint('fk_pathways_user_id', 'learning_pathways', type_='foreignkey')
    op.drop_column('learning_pathways', 'completion_percentage')
    op.drop_column('learning_pathways', 'user_id')