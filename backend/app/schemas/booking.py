from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


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
