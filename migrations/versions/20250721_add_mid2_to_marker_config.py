"""add mid2 column to marker_config

Revision ID: 20250721_add_mid2
Revises: 97e8f9af0b79
Create Date: 2025-07-21

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250721_add_mid2'
down_revision = '97e8f9af0b79'
branch_labels = None
depends_on = None

def upgrade():
    # 1. 新增字段
    op.add_column('marker_config',
        sa.Column('mid2', sa.String(length=255), nullable=False, server_default='00000000000')
    )
    # 2. 更新已有记录
    op.execute("UPDATE marker_config SET mid2 = '00000000000' WHERE mid2 IS NULL")

def downgrade():
    op.drop_column('marker_config', 'mid2')
