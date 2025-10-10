"""Add notifications table

Revision ID: 0004_add_notifications
Revises: 0003_admin_issue_reports
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0004_add_notifications'
down_revision = '0003_admin_issue_reports'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notification_type enum
    notification_type_enum = postgresql.ENUM(
        'booking_confirmation',
        'payment_confirmation',
        'booking_reminder',
        'booking_cancelled',
        'payment_failed',
        name='notificationtype',
        create_type=False
    )
    notification_type_enum.create(op.get_bind())

    # Create notifications table
    op.create_table('notifications',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('type', notification_type_enum, nullable=False),
                    sa.Column('title', sa.String(length=255), nullable=False),
                    sa.Column('message', sa.Text(), nullable=False),
                    sa.Column('data', sa.Text(), nullable=True),
                    sa.Column('booking_id', sa.Integer(), nullable=True),
                    sa.Column('payment_id', sa.Integer(), nullable=True),
                    sa.Column('is_read', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(
                        timezone=True), nullable=False),
                    sa.Column('read_at', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
                    sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_notifications_id'),
                    'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_user_id'),
                    'notifications', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop notifications table
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')

    # Drop notification_type enum
    op.execute('DROP TYPE notificationtype')
