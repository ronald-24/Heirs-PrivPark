from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class IssueStatus(str, enum.Enum):
    open = "open"
    in_review = "in_review"
    resolved = "resolved"
    dismissed = "dismissed"


class IssueReport(Base):
    __tablename__ = "issue_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    booking_id: Mapped[int | None] = mapped_column(
        ForeignKey("bookings.id"), index=True, nullable=True
    )
    parking_space_id: Mapped[int | None] = mapped_column(
        ForeignKey("parking_spaces.id"), index=True, nullable=True
    )

    subject: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus), default=IssueStatus.open
    )
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    created_by_user = relationship("User")
    booking = relationship("Booking")
    parking_space = relationship("ParkingSpace")
