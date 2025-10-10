from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class NotificationType(str, Enum):
    booking_confirmation = "booking_confirmation"
    payment_confirmation = "payment_confirmation"
    booking_reminder = "booking_reminder"
    booking_end_reminder = "booking_end_reminder"
    booking_cancelled = "booking_cancelled"
    payment_failed = "payment_failed"


class NotificationOut(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    booking_id: Optional[int] = None
    payment_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    user_id: int
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    booking_id: Optional[int] = None
    payment_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class NotificationStats(BaseModel):
    total: int
    unread: int
    by_type: Dict[str, int]
