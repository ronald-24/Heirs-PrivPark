from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import and_, select, exists, func, desc
from sqlalchemy.orm import Session, joinedload

from app.db.models import Booking, BookingStatus, Payment, PaymentStatus, ParkingSpace, Availability, User


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


def get_driver_profile(db: Session, user_id: int) -> dict:
    """Get driver profile with booking statistics"""
    user = db.execute(select(User).where(
        User.id == user_id)).scalar_one_or_none()
    if not user:
        return {}

    # Get booking statistics
    now = datetime.now(timezone.utc)

    # Total bookings
    total_bookings = db.execute(
        select(func.count(Booking.id)).where(Booking.user_id == user_id)
    ).scalar() or 0

    # Upcoming bookings (confirmed and start_time > now)
    upcoming_bookings = db.execute(
        select(func.count(Booking.id)).where(
            and_(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.confirmed,
                Booking.start_time > now
            )
        )
    ).scalar() or 0

    # Past bookings (confirmed and end_time < now)
    past_bookings = db.execute(
        select(func.count(Booking.id)).where(
            and_(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.confirmed,
                Booking.end_time < now
            )
        )
    ).scalar() or 0

    # Total spent (sum of confirmed bookings)
    total_spent = db.execute(
        select(func.coalesce(func.sum(Booking.total_amount), 0)).where(
            and_(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.confirmed
            )
        )
    ).scalar() or 0.0

    return {
        "user_id": user.id,
        "display_name": user.display_name,
        "email": user.email,
        "photo_url": user.photo_url,
        "total_bookings": total_bookings,
        "upcoming_bookings": upcoming_bookings,
        "past_bookings": past_bookings,
        "total_spent": float(total_spent),
        "created_at": user.created_at
    }


def get_booking_history(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Booking], List[Booking]]:
    """Get upcoming and past bookings for a user"""
    now = datetime.now(timezone.utc)

    # Get upcoming bookings (confirmed and start_time > now)
    upcoming_query = (
        select(Booking)
        .options(joinedload(Booking.parking_space))
        .where(
            and_(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.confirmed,
                Booking.start_time > now
            )
        )
        .order_by(Booking.start_time.asc())
        .limit(limit)
        .offset(offset)
    )
    upcoming_bookings = db.execute(upcoming_query).scalars().all()

    # Get past bookings (confirmed and end_time < now)
    past_query = (
        select(Booking)
        .options(joinedload(Booking.parking_space))
        .where(
            and_(
                Booking.user_id == user_id,
                Booking.status == BookingStatus.confirmed,
                Booking.end_time < now
            )
        )
        .order_by(Booking.end_time.desc())
        .limit(limit)
        .offset(offset)
    )
    past_bookings = db.execute(past_query).scalars().all()

    return list(upcoming_bookings), list(past_bookings)


def get_booking_with_parking_space(db: Session, booking_id: int) -> Optional[Booking]:
    """Get booking with parking space details"""
    return db.execute(
        select(Booking)
        .options(joinedload(Booking.parking_space))
        .where(Booking.id == booking_id)
    ).scalar_one_or_none()


def get_user_last_booking_for_parking_space(
    db: Session,
    user_id: int,
    parking_space_id: int
) -> Optional[Booking]:
    """Get user's last booking for a specific parking space"""
    return db.execute(
        select(Booking)
        .where(
            and_(
                Booking.user_id == user_id,
                Booking.parking_space_id == parking_space_id,
                Booking.status == BookingStatus.confirmed
            )
        )
        .order_by(Booking.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
