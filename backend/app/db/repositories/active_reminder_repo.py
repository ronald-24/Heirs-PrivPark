from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.db.models import ActiveReminder, BookingStatus


def create_active_reminder(
    db: Session,
    *,
    user_id: int,
    booking_id: int,
    start_time: datetime,
    end_time: datetime,
    reminder_interval_minutes: int = 30,
) -> ActiveReminder:
    """Create an active reminder for a booking"""
    active_reminder = ActiveReminder(
        user_id=user_id,
        booking_id=booking_id,
        start_time=start_time,
        end_time=end_time,
        reminder_interval_minutes=reminder_interval_minutes,
    )
    db.add(active_reminder)
    db.commit()
    db.refresh(active_reminder)
    return active_reminder


def get_active_reminders_for_booking(
    db: Session,
    booking_id: int
) -> Optional[ActiveReminder]:
    """Get the active reminder for a booking"""
    return db.execute(
        select(ActiveReminder).where(
            and_(
                ActiveReminder.booking_id == booking_id,
                ActiveReminder.is_active == True
            )
        )
    ).scalar_one_or_none()


def get_active_reminders_ready_for_notification(
    db: Session,
    current_time: Optional[datetime] = None
) -> List[ActiveReminder]:
    """Get all active reminders ready for notification sending"""
    if current_time is None:
        current_time = datetime.utcnow()

    # Get active reminders where:
    # 1. The booking is in progress (start_time <= current_time < end_time)
    # 2. It's time to send a reminder (last reminder + interval <= current_time)
    # 3. The reminder is still active
    query = select(ActiveReminder).where(
        and_(
            ActiveReminder.is_active == True,
            ActiveReminder.start_time <= current_time,
            ActiveReminder.end_time > current_time,
            # Either no reminder has been sent, or last reminder + interval <= now
            (
                ActiveReminder.last_reminder_sent.is_(None) |
                (
                    ActiveReminder.last_reminder_sent +
                    timedelta(minutes=ActiveReminder.reminder_interval_minutes)
                ) <= current_time
            )
        )
    )

    return db.execute(query).scalars().all()


def update_last_reminder_sent(
    db: Session,
    active_reminder_id: int
) -> Optional[ActiveReminder]:
    """Update the date of the last reminder sent"""
    active_reminder = db.execute(
        select(ActiveReminder).where(ActiveReminder.id == active_reminder_id)
    ).scalar_one_or_none()

    if not active_reminder:
        return None

    active_reminder.last_reminder_sent = datetime.utcnow()
    active_reminder.updated_at = datetime.utcnow()
    db.add(active_reminder)
    db.commit()
    db.refresh(active_reminder)
    return active_reminder


def deactivate_reminder(
    db: Session,
    booking_id: int
) -> bool:
    """Deactivate a reminder for a booking"""
    active_reminder = get_active_reminders_for_booking(db, booking_id)
    if not active_reminder:
        return False

    active_reminder.is_active = False
    active_reminder.updated_at = datetime.utcnow()
    db.add(active_reminder)
    db.commit()
    return True


def cleanup_expired_reminders(db: Session) -> int:
    """Clean up expired reminders (completed bookings)"""
    current_time = datetime.utcnow()

    # Deactivate all reminders where the booking is finished
    expired_reminders = db.execute(
        select(ActiveReminder).where(
            and_(
                ActiveReminder.is_active == True,
                ActiveReminder.end_time <= current_time
            )
        )
    ).scalars().all()

    count = 0
    for reminder in expired_reminders:
        reminder.is_active = False
        reminder.updated_at = current_time
        db.add(reminder)
        count += 1

    db.commit()
    return count


def get_user_active_reminders(
    db: Session,
    user_id: int
) -> List[ActiveReminder]:
    """Get all active reminders for a user"""
    return db.execute(
        select(ActiveReminder).where(
            and_(
                ActiveReminder.user_id == user_id,
                ActiveReminder.is_active == True
            )
        ).order_by(ActiveReminder.end_time.asc())
    ).scalars().all()
