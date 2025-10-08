from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import verify_bearer_token_and_get_user
from app.db.session import get_db
from app.db.repositories.booking_repo import (
    is_available,
    create_booking,
    get_booking,
    list_bookings_for_user,
    cancel_booking,
)
from app.schemas.booking import BookingCreate, BookingOut


router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingOut)
def create_new_booking(
    payload: BookingCreate,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)

    if payload.start_time >= payload.end_time:
        raise HTTPException(status_code=400, detail="Invalid time range")

    if not is_available(
        db,
        parking_space_id=payload.parking_space_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
    ):
        raise HTTPException(
            status_code=409, detail="Parking not available for requested interval")

    # Simple total: hours * price_per_hour (computed in SQL would require join; do here)
    # placeholder to satisfy type checker; replaced below
    ps = db.get(type("PS", (), {}), None)
    from app.db.models import ParkingSpace
    parking_space = db.get(ParkingSpace, payload.parking_space_id)
    if not parking_space or not parking_space.price_per_hour:
        raise HTTPException(status_code=400, detail="Parking price not set")
    duration_hours = (payload.end_time -
                      payload.start_time).total_seconds() / 3600.0
    total_amount = round(
        duration_hours * float(parking_space.price_per_hour), 2)

    booking = create_booking(
        db,
        user_id=user.id,
        parking_space_id=payload.parking_space_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        total_amount=total_amount,
        currency="usd",
    )
    return booking


@router.get("/", response_model=list[BookingOut])
def my_bookings(
    Authorization: str | None = Header(default=None), db: Session = Depends(get_db)
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    return list_bookings_for_user(db, user.id)


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking_by_id(
    booking_id: int, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    booking = get_booking(db, booking_id)
    if not booking or booking.user_id != user.id:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.delete("/{booking_id}", response_model=BookingOut)
def cancel_my_booking(
    booking_id: int, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    booking = cancel_booking(db, booking_id, user_id=user.id)
    if not booking:
        raise HTTPException(status_code=400, detail="Cannot cancel booking")
    return booking
