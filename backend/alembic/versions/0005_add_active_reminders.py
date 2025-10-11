"""Add active reminders table and update notification types

Revision ID: 0005_add_active_reminders
Revises: 0004_add_notifications
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005_add_active_reminders'
down_revision = '0004_add_notifications'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new notification type to existing enum
    op.execute("ALTER TYPE notificationtype ADD VALUE 'booking_end_reminder'")

    # Create active_reminders table
    op.create_table('active_reminders',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('booking_id', sa.Integer(), nullable=False),
                    sa.Column('start_time', sa.DateTime(
                        timezone=True), nullable=False),
                    sa.Column('end_time', sa.DateTime(
                        timezone=True), nullable=False),
                    sa.Column('last_reminder_sent', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.Column('reminder_interval_minutes',
                              sa.Integer(), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(
                        timezone=True), nullable=False),
                    sa.Column('updated_at', sa.DateTime(
                        timezone=True), nullable=False),
                    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_active_reminders_id'),
                    'active_reminders', ['id'], unique=False)
    op.create_index(op.f('ix_active_reminders_user_id'),
                    'active_reminders', ['user_id'], unique=False)
    op.create_index(op.f('ix_active_reminders_booking_id'),
                    'active_reminders', ['booking_id'], unique=False)


def downgrade() -> None:
    # Drop active_reminders table
    op.drop_index(op.f('ix_active_reminders_booking_id'),
                  table_name='active_reminders')
    op.drop_index(op.f('ix_active_reminders_user_id'),
                  table_name='active_reminders')
    op.drop_index(op.f('ix_active_reminders_id'),
                  table_name='active_reminders')
    op.drop_table('active_reminders')

    # Note: PostgreSQL doesn't support removing enum values, so we leave the enum as is
