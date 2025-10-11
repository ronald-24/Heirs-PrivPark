from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import verify_bearer_token_and_get_user
from app.db.session import get_db
from app.services.notification_service import NotificationService
from app.db.repositories.active_reminder_repo import get_user_active_reminders, deactivate_reminder
from app.db.repositories.booking_repo import get_booking

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/schedule-reminders")
def schedule_booking_reminders(db: Session = Depends(get_db)):
    """Endpoint to schedule booking reminders (to be called periodically)"""
    try:
        NotificationService.schedule_booking_reminders(db)
        return {"message": "Booking reminders scheduled successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error scheduling reminders: {str(e)}")


@router.post("/process-periodic-reminders")
def process_periodic_reminders(db: Session = Depends(get_db)):
    """Endpoint to process periodic reminders (to be called every 30 minutes)"""
    try:
        notifications_sent = NotificationService.process_periodic_reminders(db)
        return {
            "message": f"Processed periodic reminders successfully",
            "notifications_sent": notifications_sent
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing periodic reminders: {str(e)}")


@router.post("/schedule-start-reminders")
def schedule_booking_start_reminders(db: Session = Depends(get_db)):
    """Endpoint to start periodic reminders for bookings that are starting"""
    try:
        NotificationService.schedule_booking_start_reminders(db)
        return {"message": "Booking start reminders scheduled successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error scheduling start reminders: {str(e)}")


@router.get("/my-active-reminders")
def get_my_active_reminders(
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """Get active reminders for the logged-in user"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db
    )

    active_reminders = get_user_active_reminders(db, user.id)

    result = []
    for reminder in active_reminders:
        result.append({
            "id": reminder.id,
            "booking_id": reminder.booking_id,
            "start_time": reminder.start_time,
            "end_time": reminder.end_time,
            "last_reminder_sent": reminder.last_reminder_sent,
            "reminder_interval_minutes": reminder.reminder_interval_minutes,
            "is_active": reminder.is_active,
            "created_at": reminder.created_at
        })

    return {"active_reminders": result}


@router.post("/stop-reminder/{booking_id}")
def stop_booking_reminder(
    booking_id: int,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    """Stop reminders for a specific booking"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db
    )

    # Check that the booking belongs to the user
    booking = get_booking(db, booking_id)
    if not booking or booking.user_id != user.id:
        raise HTTPException(status_code=404, detail="Booking not found")

    success = deactivate_reminder(db, booking_id)
    if not success:
        raise HTTPException(
            status_code=400, detail="No active reminder found for this booking")

    return {"message": "Reminder stopped successfully"}
