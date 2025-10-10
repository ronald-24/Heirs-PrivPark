from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.db.models import Notification, NotificationType


def create_notification(
    db: Session,
    *,
    user_id: int,
    type: NotificationType,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    booking_id: Optional[int] = None,
    payment_id: Optional[int] = None,
) -> Notification:
    """Create a new notification"""
    import json

    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        data=json.dumps(data) if data else None,
        booking_id=booking_id,
        payment_id=payment_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notifications_for_user(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False
) -> List[Notification]:
    """Retrieve all notifications for a user"""
    query = select(Notification).where(Notification.user_id == user_id)

    if unread_only:
        query = query.where(Notification.is_read == False)

    query = query.order_by(Notification.created_at.desc()
                           ).offset(offset).limit(limit)

    return db.execute(query).scalars().all()


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """Retrieve a notification by its ID"""
    return db.execute(select(Notification).where(Notification.id == notification_id)).scalar_one_or_none()


def mark_notification_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
    """Mark a notification as read"""
    notification = db.execute(
        select(Notification).where(
            and_(Notification.id == notification_id,
                 Notification.user_id == user_id)
        )
    ).scalar_one_or_none()

    if not notification:
        return None

    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_notifications_as_read(db: Session, user_id: int) -> int:
    """Mark all notifications for a user as read"""
    notifications = db.execute(
        select(Notification).where(
            and_(Notification.user_id == user_id,
                 Notification.is_read == False)
        )
    ).scalars().all()

    count = 0
    for notification in notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.add(notification)
        count += 1

    db.commit()
    return count


def get_notification_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Get notification statistics for a user"""
    # Total number of notifications
    total = db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id)
    ).scalar()

    # Number of unread notifications
    unread = db.execute(
        select(func.count(Notification.id)).where(
            and_(Notification.user_id == user_id,
                 Notification.is_read == False)
        )
    ).scalar()

    # Group by notification type
    by_type_result = db.execute(
        select(Notification.type, func.count(Notification.id))
        .where(Notification.user_id == user_id)
        .group_by(Notification.type)
    ).all()

    by_type = {str(row[0]): row[1] for row in by_type_result}

    return {
        "total": total,
        "unread": unread,
        "by_type": by_type
    }


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    """Delete a notification"""
    notification = db.execute(
        select(Notification).where(
            and_(Notification.id == notification_id,
                 Notification.user_id == user_id)
        )
    ).scalar_one_or_none()

    if not notification:
        return False

    db.delete(notification)
    db.commit()
    return True
