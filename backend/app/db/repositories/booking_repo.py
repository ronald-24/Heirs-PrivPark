from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select, exists
from sqlalchemy.orm import Session

from app.db.models import Booking, BookingStatus, Payment, PaymentStatus, ParkingSpace, Availability


def is_available(
    db: Session,
    *,
    parking_space_id: int,
    start_time: datetime,
    end_time: datetime,
) -> bool:
    # Availability rule: there exists an Availability fully covering the interval,
    # and no overlapping confirmed bookings.
    has_availability = db.execute(
        select(Availability.id).where(
            and_(
                Availability.parking_space_id == parking_space_id,
                Availability.start <= start_time,
                Availability.end >= end_time,
            )
        )
    ).first() is not None

    if not has_availability:
        return False

    overlapping_confirmed = db.execute(
        select(Booking.id).where(
            and_(
                Booking.parking_space_id == parking_space_id,
                Booking.status == BookingStatus.confirmed,
                Booking.start_time < end_time,
                Booking.end_time > start_time,
            )
        )
    ).first() is not None

    return not overlapping_confirmed


def create_booking(
    db: Session,
    *,
    user_id: int,
    parking_space_id: int,
    start_time: datetime,
    end_time: datetime,
    total_amount: float,
    currency: str = "usd",
) -> Booking:
    booking = Booking(
        user_id=user_id,
        parking_space_id=parking_space_id,
        start_time=start_time,
        end_time=end_time,
        total_amount=total_amount,
        currency=currency,
        status=BookingStatus.pending,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def get_booking(db: Session, booking_id: int) -> Optional[Booking]:
    return db.execute(select(Booking).where(Booking.id == booking_id)).scalar_one_or_none()


def list_bookings_for_user(db: Session, user_id: int) -> List[Booking]:
    return db.execute(select(Booking).where(Booking.user_id == user_id).order_by(Booking.created_at.desc())).scalars().all()


def cancel_booking(db: Session, booking_id: int, *, user_id: int) -> Booking | None:
    booking = get_booking(db, booking_id)
    if not booking or booking.user_id != user_id:
        return None
    if booking.status == BookingStatus.confirmed:
        # Business rule: do not allow cancel of confirmed here (refund flow via payments)
        return None
    booking.status = BookingStatus.cancelled
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def attach_checkout_session(db: Session, booking_id: int, session_id: str) -> None:
    booking = get_booking(db, booking_id)
    if not booking:
        return
    booking.stripe_checkout_session_id = session_id
    db.add(booking)
    db.commit()


def mark_booking_confirmed(db: Session, booking_id: int) -> None:
    booking = get_booking(db, booking_id)
    if not booking:
        return
    booking.status = BookingStatus.confirmed
    db.add(booking)
    db.commit()


def create_payment(
    db: Session,
    *,
    user_id: int,
    parking_space_id: int,
    booking_id: int,
    amount: float,
    currency: str,
    payment_date: datetime,
    provider_payment_id: str | None,
    status: PaymentStatus,
    receipt_url: str | None = None,
) -> Payment:
    payment = Payment(
        user_id=user_id,
        parking_space_id=parking_space_id,
        booking_id=booking_id,
        amount=amount,
        currency=currency,
        payment_date=payment_date,
        provider_payment_id=provider_payment_id,
        status=status,
        receipt_url=receipt_url,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
