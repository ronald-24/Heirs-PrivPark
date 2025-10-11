"""create parking tables

Revision ID: 0001_create_parking_tables
Revises: 
Create Date: 2025-09-19 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_create_parking_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'parking_spaces',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('photos', sa.Text(), nullable=True),
        sa.Column('price_per_hour', sa.Float(), nullable=True),
        sa.Column('rules', sa.Text(), nullable=True),
        sa.Column('address', sa.String(length=512), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        'parking_availabilities',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('parking_space_id', sa.Integer(), nullable=False),
        sa.Column('start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('parking_availabilities')
    op.drop_table('parking_spaces')
