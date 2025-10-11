from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime, Enum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class NotificationType(str, enum.Enum):
    booking_confirmation = "booking_confirmation"  # Booking created
    payment_confirmation = "payment_confirmation"  # Payment successful
    booking_reminder = "booking_reminder"  # Reminder before booking start
    # Booking end reminder (every 30min)
    booking_end_reminder = "booking_end_reminder"
    booking_cancelled = "booking_cancelled"  # Booking cancelled
    payment_failed = "payment_failed"  # Payment failed


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Notification type
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType))

    # Notification content
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)

    # Additional data (JSON serializable)
    data: Mapped[str | None] = mapped_column(
        Text, nullable=True)  # JSON string

    # Optional references
    booking_id: Mapped[int | None] = mapped_column(
        ForeignKey("bookings.id"), nullable=True)
    payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("payments.id"), nullable=True)

    # Notification state
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relations
    user = relationship("User")
    booking = relationship("Booking")
    payment = relationship("Payment")
