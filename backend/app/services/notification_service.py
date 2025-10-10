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
    """Service pour gérer la création automatique des notifications"""

    @staticmethod
    def create_booking_confirmation_notification(
        db: Session,
        booking: Booking,
        user: User
    ) -> None:
        """Créer une notification de confirmation de réservation"""
        title = "Réservation confirmée"
        message = f"Votre réservation pour le parking #{booking.parking_space_id} a été créée avec succès. Début: {booking.start_time.strftime('%d/%m/%Y à %H:%M')}"

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
        """Créer une notification de confirmation de paiement"""
        title = "Paiement confirmé"
        message = f"Votre paiement de {payment.amount} {payment.currency.upper()} a été traité avec succès. Votre réservation est maintenant confirmée."

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
        """Créer une notification de rappel avant le début de la réservation"""
        title = "Rappel de réservation"
        message = f"Votre réservation pour le parking #{booking.parking_space_id} commence dans 1 heure. Début: {booking.start_time.strftime('%d/%m/%Y à %H:%M')}"

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
        """Créer une notification d'annulation de réservation"""
        title = "Réservation annulée"
        message = f"Votre réservation pour le parking #{booking.parking_space_id} a été annulée."

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
        """Créer une notification d'échec de paiement"""
        title = "Paiement échoué"
        message = f"Le paiement pour votre réservation du parking #{booking.parking_space_id} a échoué."
        if error_message:
            message += f" Raison: {error_message}"

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
        """Créer une notification de rappel de fin de réservation"""
        title = "Rappel de fin de réservation"
        message = f"Votre réservation pour le parking #{booking.parking_space_id} se termine dans {minutes_remaining} minutes. Fin prévue: {booking.end_time.strftime('%d/%m/%Y à %H:%M')}"

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
        """Démarrer les rappels périodiques pour une réservation"""
        # Créer un rappel actif
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
        """Arrêter les rappels périodiques pour une réservation"""
        deactivate_reminder(db, booking.id)

    @staticmethod
    def process_periodic_reminders(db: Session) -> int:
        """Traiter tous les rappels périodiques en attente"""
        # Nettoyer d'abord les rappels expirés
        cleanup_expired_reminders(db)

        # Récupérer les rappels prêts pour notification
        active_reminders = get_active_reminders_ready_for_notification(db)

        notifications_sent = 0
        for reminder in active_reminders:
            try:
                # Calculer le temps restant
                current_time = datetime.utcnow()
                time_remaining = reminder.end_time - current_time
                minutes_remaining = int(time_remaining.total_seconds() / 60)

                # Créer la notification
                NotificationService.create_booking_end_reminder_notification(
                    db, reminder.booking, reminder.user, minutes_remaining
                )

                # Mettre à jour la date du dernier rappel
                update_last_reminder_sent(db, reminder.id)

                notifications_sent += 1

            except Exception as e:
                print(
                    f"Erreur lors de l'envoi du rappel pour la réservation {reminder.booking_id}: {e}")
                continue

        return notifications_sent

    @staticmethod
    def schedule_booking_reminders(db: Session) -> None:
        """Programmer les rappels pour les réservations qui commencent dans 1 heure"""
        from sqlalchemy import select

        # Trouver les réservations confirmées qui commencent dans 1 heure
        one_hour_from_now = datetime.utcnow() + timedelta(hours=1)
        one_hour_window = timedelta(minutes=30)  # Fenêtre de 30 minutes

        bookings = db.execute(
            select(Booking).where(
                Booking.status == BookingStatus.confirmed,
                Booking.start_time >= one_hour_from_now - one_hour_window,
                Booking.start_time <= one_hour_from_now + one_hour_window
            )
        ).scalars().all()

        for booking in bookings:
            # Vérifier si un rappel n'a pas déjà été envoyé
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
        """Programmer les rappels pour les réservations qui commencent maintenant"""
        from sqlalchemy import select

        current_time = datetime.utcnow()
        time_window = timedelta(minutes=5)  # Fenêtre de 5 minutes

        # Trouver les réservations confirmées qui commencent maintenant
        bookings = db.execute(
            select(Booking).where(
                Booking.status == BookingStatus.confirmed,
                Booking.start_time >= current_time - time_window,
                Booking.start_time <= current_time + time_window
            )
        ).scalars().all()

        for booking in bookings:
            # Démarrer les rappels périodiques de fin
            NotificationService.start_booking_end_reminders(
                db, booking, booking.user)
