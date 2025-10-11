from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_admin_issue_reports'
down_revision = '0002_add_bookings_payments'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users: add is_active
    op.add_column('users', sa.Column('is_active', sa.Boolean(),
                  nullable=False, server_default=sa.true()))

    # Parking: add is_active and status enum
    op.add_column('parking_spaces', sa.Column(
        'is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.execute(
        "CREATE TYPE listingstatus AS ENUM ('pending', 'approved', 'rejected')")
    op.add_column('parking_spaces', sa.Column('status', sa.Enum(
        name='listingstatus'), nullable=False, server_default='pending'))

    # Issue Reports table
    op.execute(
        "CREATE TYPE issuestatus AS ENUM ('open', 'in_review', 'resolved', 'dismissed')")
    op.create_table(
        'issue_reports',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('created_by_user_id', sa.Integer(), sa.ForeignKey(
            'users.id'), index=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), sa.ForeignKey(
            'bookings.id'), index=True, nullable=True),
        sa.Column('parking_space_id', sa.Integer(), sa.ForeignKey(
            'parking_spaces.id'), index=True, nullable=True),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum(name='issuestatus'),
                  nullable=False, server_default='open'),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('issue_reports')
    op.execute('DROP TYPE IF EXISTS issuestatus')

    op.drop_column('parking_spaces', 'status')
    op.drop_column('parking_spaces', 'is_active')
    op.execute('DROP TYPE IF EXISTS listingstatus')

    op.drop_column('users', 'is_active')
