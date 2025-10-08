from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class BookingStatus(str, enum.Enum):
    pending = "pending"  # created but not yet paid/confirmed
    confirmed = "confirmed"  # payment succeeded
    cancelled = "cancelled"  # user or system cancelled
    expired = "expired"  # payment not completed in time


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    parking_space_id: Mapped[int] = mapped_column(
        ForeignKey("parking_spaces.id"), index=True
    )

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    total_amount: Mapped[float] = mapped_column(
        Float)  # in major currency units
    currency: Mapped[str] = mapped_column(String(10), default="usd")

    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), default=BookingStatus.pending)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Stripe checkout metadata
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True)

    user = relationship("User")
    parking_space = relationship("ParkingSpace")


class PaymentStatus(str, enum.Enum):
    complet = "complet"  # Paiement réussi
    en_attente = "en_attente"  # Paiement en cours
    echoue = "echoue"  # Paiement échoué


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    parking_space_id: Mapped[int] = mapped_column(
        ForeignKey("parking_spaces.id"), index=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="usd")
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.en_attente)

    # Champs optionnels pour Stripe
    provider: Mapped[str] = mapped_column(String(32), default="stripe")
    provider_payment_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True)
    receipt_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
    parking_space = relationship("ParkingSpace")
    booking = relationship("Booking")
