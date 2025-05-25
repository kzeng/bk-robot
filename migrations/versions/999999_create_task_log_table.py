"""Create TaskLog table

Revision ID: 999999
Revises: fa4773f088dc
Create Date: 2025-05-25 19:47:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '999999'
down_revision = 'fa4773f088dc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('task_logs',
        sa.Column('log_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('marker', sa.String(length=255), nullable=False),
        sa.Column('action', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('file_count', sa.Integer(), nullable=False),
        sa.Column('file_paths', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], ),
        sa.PrimaryKeyConstraint('log_id')
    )


def downgrade():
    op.drop_table('task_logs')
