from __future__ import annotations

from sqlalchemy import String, Float, Text, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from app.db.base import Base
import enum


class ListingStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ParkingSpace(Base):
    __tablename__ = "parking_spaces"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # store comma-separated photo URLs for simplicity
    photos: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_per_hour: Mapped[float | None] = mapped_column(Float, nullable=True)
    rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Moderation fields
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped["ListingStatus"] = mapped_column(
        Enum(ListingStatus), default=ListingStatus.pending
    )

    owner = relationship("User", backref="parking_spaces")
    availabilities = relationship(
        "Availability", back_populates="parking_space", cascade="all, delete-orphan")


class Availability(Base):
    __tablename__ = "parking_availabilities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    parking_space_id: Mapped[int] = mapped_column(
        ForeignKey("parking_spaces.id"), index=True)
    start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    parking_space = relationship(
        "ParkingSpace", back_populates="availabilities")
