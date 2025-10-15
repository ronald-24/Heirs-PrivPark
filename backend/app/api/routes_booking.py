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
    get_driver_profile,
    get_booking_history,
    get_booking_with_parking_space,
    get_user_last_booking_for_parking_space,
)
from app.schemas.booking import (
    BookingCreate,
    BookingOut,
    DriverProfile,
    BookingHistoryResponse,
    BookingWithParkingSpace,
    RebookRequest
)
from app.db.models import ParkingSpace
from app.services.notification_service import NotificationService


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

    # Créer une notification de confirmation de réservation
    try:
        NotificationService.create_booking_confirmation_notification(
            db, booking, user)
    except Exception as e:
        # Log l'erreur mais ne pas faire échouer la création de réservation
        print(f"Erreur lors de la création de la notification: {e}")

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

    # Créer une notification d'annulation de réservation
    try:
        NotificationService.create_booking_cancelled_notification(
            db, booking, user)
    except Exception as e:
        # Log l'erreur mais ne pas faire échouer l'annulation
        print(
            f"Erreur lors de la création de la notification d'annulation: {e}")

    return booking


@router.get("/profile", response_model=DriverProfile)
def get_driver_profile_endpoint(
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """Get driver profile with booking statistics"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)

    profile_data = get_driver_profile(db, user.id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="User not found")

    return DriverProfile(**profile_data)


@router.get("/history", response_model=BookingHistoryResponse)
def get_booking_history_endpoint(
    limit: int = 50,
    offset: int = 0,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """Get booking history with upcoming and past bookings"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)

    upcoming_bookings, past_bookings = get_booking_history(
        db, user.id, limit=limit, offset=offset
    )

    # Convert to BookingWithParkingSpace format
    upcoming_with_details = []
    for booking in upcoming_bookings:
        booking_data = {
            "id": booking.id,
            "user_id": booking.user_id,
            "parking_space_id": booking.parking_space_id,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "total_amount": booking.total_amount,
            "currency": booking.currency,
            "status": booking.status.value,
            "stripe_checkout_session_id": booking.stripe_checkout_session_id,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
            "parking_space_title": booking.parking_space.title if booking.parking_space else None,
            "parking_space_address": booking.parking_space.address if booking.parking_space else None,
            "parking_space_latitude": booking.parking_space.latitude if booking.parking_space else None,
            "parking_space_longitude": booking.parking_space.longitude if booking.parking_space else None,
        }
        upcoming_with_details.append(BookingWithParkingSpace(**booking_data))

    past_with_details = []
    for booking in past_bookings:
        booking_data = {
            "id": booking.id,
            "user_id": booking.user_id,
            "parking_space_id": booking.parking_space_id,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "total_amount": booking.total_amount,
            "currency": booking.currency,
            "status": booking.status.value,
            "stripe_checkout_session_id": booking.stripe_checkout_session_id,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at,
            "parking_space_title": booking.parking_space.title if booking.parking_space else None,
            "parking_space_address": booking.parking_space.address if booking.parking_space else None,
            "parking_space_latitude": booking.parking_space.latitude if booking.parking_space else None,
            "parking_space_longitude": booking.parking_space.longitude if booking.parking_space else None,
        }
        past_with_details.append(BookingWithParkingSpace(**booking_data))

    return BookingHistoryResponse(
        upcoming_bookings=upcoming_with_details,
        past_bookings=past_with_details,
        total_upcoming=len(upcoming_with_details),
        total_past=len(past_with_details)
    )


@router.post("/rebook/{parking_space_id}", response_model=BookingOut)
def rebook_same_spot(
    parking_space_id: int,
    payload: RebookRequest,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Rebook the same parking space with new time slot"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)

    if payload.start_time >= payload.end_time:
        raise HTTPException(status_code=400, detail="Invalid time range")

    # Check if user has previously booked this parking space
    last_booking = get_user_last_booking_for_parking_space(
        db, user.id, parking_space_id
    )
    if not last_booking:
        raise HTTPException(
            status_code=400,
            detail="You have never booked this parking space before"
        )

    # Check availability
    if not is_available(
        db,
        parking_space_id=parking_space_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
    ):
        raise HTTPException(
            status_code=409,
            detail="Parking not available for requested interval"
        )

    # Get parking space details for pricing
    parking_space = db.get(ParkingSpace, parking_space_id)
    if not parking_space or not parking_space.price_per_hour:
        raise HTTPException(status_code=400, detail="Parking price not set")

    # Calculate total amount
    duration_hours = (payload.end_time -
                      payload.start_time).total_seconds() / 3600.0
    total_amount = round(
        duration_hours * float(parking_space.price_per_hour), 2)

    # Create new booking
    booking = create_booking(
        db,
        user_id=user.id,
        parking_space_id=parking_space_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
        total_amount=total_amount,
        currency="usd",
    )

    # Create notification
    try:
        NotificationService.create_booking_confirmation_notification(
            db, booking, user)
    except Exception as e:
        print(f"Erreur lors de la création de la notification: {e}")

    return booking
