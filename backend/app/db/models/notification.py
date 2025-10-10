from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime, Enum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class NotificationType(str, enum.Enum):
    booking_confirmation = "booking_confirmation"  # Réservation créée
    payment_confirmation = "payment_confirmation"  # Paiement réussi
    booking_reminder = "booking_reminder"  # Rappel avant début de réservation
    # Rappel de fin de réservation (toutes les 30min)
    booking_end_reminder = "booking_end_reminder"
    booking_cancelled = "booking_cancelled"  # Réservation annulée
    payment_failed = "payment_failed"  # Paiement échoué


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Type de notification
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType))

    # Contenu de la notification
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)

    # Données supplémentaires (JSON serializable)
    data: Mapped[str | None] = mapped_column(
        Text, nullable=True)  # JSON string

    # Références optionnelles
    booking_id: Mapped[int | None] = mapped_column(
        ForeignKey("bookings.id"), nullable=True)
    payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("payments.id"), nullable=True)

    # État de la notification
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
