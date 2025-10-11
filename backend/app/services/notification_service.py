from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models import NotificationType, Booking, Payment, User, BookingStatus
from app.db.repositories.notification_repo import create_notification
from app.db.repositories.active_reminder_repo import (
    create_active_reminder,
    get_active_reminders_ready_for_notification,
    update_last_reminder_sent,
    cleanup_expired_reminders,
    deactivate_reminder,
)


class NotificationService:
    """Service for managing automatic notification creation"""

    @staticmethod
    def create_booking_confirmation_notification(
        db: Session,
        booking: Booking,
        user: User
    ) -> None:
        """Create a booking confirmation notification"""
        title = "Booking Confirmed"
        message = f"Your booking for parking #{booking.parking_space_id} has been created successfully. Start: {booking.start_time.strftime('%d/%m/%Y at %H:%M')}"

        data = {
            "booking_id": booking.id,
            "parking_space_id": booking.parking_space_id,
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "total_amount": booking.total_amount,
            "currency": booking.currency
        }

        create_notification(
            db=db,
            user_id=user.id,
            type=NotificationType.booking_confirmation,
            title=title,
            message=message,
            data=data,
            booking_id=booking.id
        )

    @staticmethod
    def create_payment_confirmation_notification(
        db: Session,
        payment: Payment,
        user: User
    ) -> None:
        """Create a payment confirmation notification"""
        title = "Payment Confirmed"
        message = f"Your payment of {payment.amount} {payment.currency.upper()} has been processed successfully. Your booking is now confirmed."

        data = {
            "payment_id": payment.id,
            "booking_id": payment.booking_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "payment_date": payment.payment_date.isoformat(),
            "receipt_url": payment.receipt_url
        }

        create_notification(
            db=db,
            user_id=user.id,
            type=NotificationType.payment_confirmation,
            title=title,
            message=message,
            data=data,
            booking_id=payment.booking_id,
            payment_id=payment.id
        )

    @staticmethod
    def create_booking_reminder_notification(
        db: Session,
        booking: Booking,
        user: User
    ) -> None:
        """Create a notification reminder before booking start"""
        title = "Booking Reminder"
        message = f"Your booking for parking #{booking.parking_space_id} starts in 1 hour. Start: {booking.start_time.strftime('%d/%m/%Y at %H:%M')}"

        data = {
            "booking_id": booking.id,
            "parking_space_id": booking.parking_space_id,
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "reminder_type": "1_hour_before"
        }

        create_notification(
            db=db,
            user_id=user.id,
            type=NotificationType.booking_reminder,
            title=title,
            message=message,
            data=data,
            booking_id=booking.id
        )

    @staticmethod
    def create_booking_cancelled_notification(
        db: Session,
        booking: Booking,
        user: User
    ) -> None:
        """Create a booking cancellation notification"""
        title = "Booking Cancelled"
        message = f"Your booking for parking #{booking.parking_space_id} has been cancelled."

        data = {
            "booking_id": booking.id,
            "parking_space_id": booking.parking_space_id,
            "start_time": booking.start_time.isoformat(),
            "end_time": booking.end_time.isoformat(),
            "cancelled_at": datetime.utcnow().isoformat()
        }

        create_notification(
            db=db,
            user_id=user.id,
            type=NotificationType.booking_cancelled,
            title=title,
            message=message,
            data=data,
            booking_id=booking.id
        )

    @staticmethod
    def create_payment_failed_notification(
        db: Session,
        booking: Booking,
        user: User,
        error_message: Optional[str] = None
    ) -> None:
        """Create a payment failure notification"""
        title = "Payment Failed"
        message = f"Payment for your booking at parking #{booking.parking_space_id} has failed."
        if error_message:
            message += f" Reason: {error_message}"

        data = {
            "booking_id": booking.id,
            "parking_space_id": booking.parking_space_id,
            "amount": booking.total_amount,
            "currency": booking.currency,
            "error_message": error_message,
            "failed_at": datetime.utcnow().isoformat()
        }

        create_notification(
            db=db,
            user_id=user.id,
            type=NotificationType.payment_failed,
            title=title,
            message=message,
            data=data,
            booking_id=booking.id
        )

    @staticmethod
    def create_booking_end_reminder_notification(
        db: Session,
        booking: Booking,
        user: User,
        minutes_remaining: int
    ) -> None:
        """Create a booking end reminder notification"""
        title = "Booking End Reminder"
        message = f"Your booking for parking #{booking.parking_space_id} ends in {minutes_remaining} minutes. Expected end: {booking.end_time.strftime('%d/%m/%Y at %H:%M')}"

        data = {
            "booking_id": booking.id,
            "parking_space_id": booking.parking_space_id,
            "end_time": booking.end_time.isoformat(),
            "minutes_remaining": minutes_remaining,
            "reminder_type": "end_reminder"
        }

        create_notification(
            db=db,
            user_id=user.id,
            type=NotificationType.booking_end_reminder,
            title=title,
            message=message,
            data=data,
            booking_id=booking.id
        )

    @staticmethod
    def start_booking_end_reminders(
        db: Session,
        booking: Booking,
        user: User,
        reminder_interval_minutes: int = 30
    ) -> None:
        """Start periodic reminders for a booking"""
        # Create an active reminder
        create_active_reminder(
            db=db,
            user_id=user.id,
            booking_id=booking.id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            reminder_interval_minutes=reminder_interval_minutes
        )

    @staticmethod
    def stop_booking_end_reminders(
        db: Session,
        booking: Booking
    ) -> None:
        """Stop periodic reminders for a booking"""
        deactivate_reminder(db, booking.id)

    @staticmethod
    def process_periodic_reminders(db: Session) -> int:
        """Process all pending periodic reminders"""
        # First clean up expired reminders
        cleanup_expired_reminders(db)

        # Get reminders ready for notification
        active_reminders = get_active_reminders_ready_for_notification(db)

        notifications_sent = 0
        for reminder in active_reminders:
            try:
                # Calculate remaining time
                current_time = datetime.utcnow()
                time_remaining = reminder.end_time - current_time
                minutes_remaining = int(time_remaining.total_seconds() / 60)

                # Create the notification
                NotificationService.create_booking_end_reminder_notification(
                    db, reminder.booking, reminder.user, minutes_remaining
                )

                # Update last reminder sent date
                update_last_reminder_sent(db, reminder.id)

                notifications_sent += 1

            except Exception as e:
                print(
                    f"Error sending reminder for booking {reminder.booking_id}: {e}")
                continue

        return notifications_sent

    @staticmethod
    def schedule_booking_reminders(db: Session) -> None:
        """Schedule reminders for bookings starting in 1 hour"""
        from sqlalchemy import select

        # Find confirmed bookings starting in 1 hour
        one_hour_from_now = datetime.utcnow() + timedelta(hours=1)
        one_hour_window = timedelta(minutes=30)  # 30-minute window

        bookings = db.execute(
            select(Booking).where(
                Booking.status == BookingStatus.confirmed,
                Booking.start_time >= one_hour_from_now - one_hour_window,
                Booking.start_time <= one_hour_from_now + one_hour_window
            )
        ).scalars().all()

        for booking in bookings:
            # Check if a reminder hasn't already been sent
            from app.db.repositories.notification_repo import get_notifications_for_user
            notifications = get_notifications_for_user(
                db, booking.user_id, limit=100)
            existing_reminder = any(
                n.type == NotificationType.booking_reminder and n.booking_id == booking.id
                for n in notifications
            )

            if not existing_reminder:
                NotificationService.create_booking_reminder_notification(
                    db, booking, booking.user
                )

    @staticmethod
    def schedule_booking_start_reminders(db: Session) -> None:
        """Schedule reminders for bookings starting now"""
        from sqlalchemy import select

        current_time = datetime.utcnow()
        time_window = timedelta(minutes=5)  # 5-minute window

        # Find confirmed bookings starting now
        bookings = db.execute(
            select(Booking).where(
                Booking.status == BookingStatus.confirmed,
                Booking.start_time >= current_time - time_window,
                Booking.start_time <= current_time + time_window
            )
        ).scalars().all()

        for booking in bookings:
            # Start periodic end reminders
            NotificationService.start_booking_end_reminders(
                db, booking, booking.user)
