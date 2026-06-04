"""add slamtec marker fields

Revision ID: 20260604_slamtec_marker
Revises: c2e967457f05
Create Date: 2026-06-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20260604_slamtec_marker'
down_revision = 'c2e967457f05'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('marker_config', schema=None) as batch_op:
        batch_op.add_column(sa.Column('poi_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('poi_name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('building', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('floor', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('map_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('pose_x', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('pose_y', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('pose_yaw', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('marker_config', schema=None) as batch_op:
        batch_op.drop_column('pose_yaw')
        batch_op.drop_column('pose_y')
        batch_op.drop_column('pose_x')
        batch_op.drop_column('map_id')
        batch_op.drop_column('floor')
        batch_op.drop_column('building')
        batch_op.drop_column('poi_name')
        batch_op.drop_column('poi_id')
