from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_bookings_payments'
down_revision = '0001_create_parking_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(),
                  sa.ForeignKey('users.id'), index=True),
        sa.Column('parking_space_id', sa.Integer(),
                  sa.ForeignKey('parking_spaces.id'), index=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10),
                  nullable=False, server_default='usd'),
        sa.Column('status', sa.Enum('pending', 'confirmed', 'cancelled', 'expired',
                  name='bookingstatus'), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text('now()')),
        sa.Column('stripe_checkout_session_id',
                  sa.String(length=128), nullable=True),
    )

    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(),
                  sa.ForeignKey('users.id'), index=True),
        sa.Column('parking_space_id', sa.Integer(),
                  sa.ForeignKey('parking_spaces.id'), index=True),
        sa.Column('booking_id', sa.Integer(),
                  sa.ForeignKey('bookings.id'), index=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10),
                  nullable=False, server_default='usd'),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Enum('complet', 'en_attente', 'echoue',
                  name='paymentstatus'), nullable=False, server_default='en_attente'),
        sa.Column('provider', sa.String(length=32),
                  nullable=False, server_default='stripe'),
        sa.Column('provider_payment_id', sa.String(length=128), nullable=True),
        sa.Column('receipt_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  nullable=False, server_default=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('payments')
    op.drop_table('bookings')
    op.execute('DROP TYPE IF EXISTS bookingstatus')
    op.execute('DROP TYPE IF EXISTS paymentstatus')
