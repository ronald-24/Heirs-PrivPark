from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class BookingCreate(BaseModel):
    parking_space_id: int
    start_time: datetime
    end_time: datetime


class BookingOut(BaseModel):
    id: int
    user_id: int
    parking_space_id: int
    start_time: datetime
    end_time: datetime
    total_amount: float
    currency: str
    status: str
    stripe_checkout_session_id: Optional[str] = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class PaymentCreateSession(BaseModel):
    booking_id: int
    success_url: str
    cancel_url: str


class CheckoutSessionOut(BaseModel):
    checkout_url: str = Field(...,
                              description="Stripe Checkout URL to redirect client")


class PaymentOut(BaseModel):
    id: int
    user_id: int
    parking_space_id: int
    booking_id: int
    amount: float
    currency: str
    payment_date: datetime
    status: str
    provider: str
    provider_payment_id: Optional[str]
    receipt_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BookingWithParkingSpace(BookingOut):
    """Booking with parking space details included"""
    parking_space_title: Optional[str] = None
    parking_space_address: Optional[str] = None
    parking_space_latitude: Optional[float] = None
    parking_space_longitude: Optional[float] = None


class DriverProfile(BaseModel):
    """Driver profile with booking statistics"""
    user_id: int
    display_name: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None
    total_bookings: int = 0
    upcoming_bookings: int = 0
    past_bookings: int = 0
    total_spent: float = 0.0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookingHistoryResponse(BaseModel):
    """Response for booking history with upcoming and past bookings"""
    upcoming_bookings: List[BookingWithParkingSpace] = []
    past_bookings: List[BookingWithParkingSpace] = []
    total_upcoming: int = 0
    total_past: int = 0


class RebookRequest(BaseModel):
    """Request to rebook the same parking space"""
    start_time: datetime
    end_time: datetime
