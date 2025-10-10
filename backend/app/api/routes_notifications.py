from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import verify_bearer_token_and_get_user
from app.db.session import get_db
from app.db.repositories.notification_repo import (
    get_notifications_for_user,
    get_notification,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    get_notification_stats,
    delete_notification,
)
from app.schemas.notification import (
    NotificationOut,
    NotificationUpdate,
    NotificationStats,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationOut])
def get_my_notifications(
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
):
    """Retrieve notifications for the authenticated user"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db
    )

    notifications = get_notifications_for_user(
        db, user.id, limit=limit, offset=offset, unread_only=unread_only
    )

    # Convert JSON data fields to Python dict if present
    result = []
    for notification in notifications:
        notification_dict = {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "data": None,
            "booking_id": notification.booking_id,
            "payment_id": notification.payment_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "read_at": notification.read_at,
        }

        # Parse JSON data if it exists
        if notification.data:
            import json
            try:
                notification_dict["data"] = json.loads(notification.data)
            except json.JSONDecodeError:
                notification_dict["data"] = None

        result.append(NotificationOut(**notification_dict))

    return result


@router.get("/stats", response_model=NotificationStats)
def get_my_notification_stats(
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Get notification statistics for the authenticated user"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db
    )

    stats = get_notification_stats(db, user.id)
    return NotificationStats(**stats)


@router.get("/{notification_id}", response_model=NotificationOut)
def get_notification_by_id(
    notification_id: int,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Retrieve a specific notification by its ID"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db
    )

    notification = get_notification(db, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Convert JSON data field to Python dict
    data = None
    if notification.data:
        import json
        try:
            data = json.loads(notification.data)
        except json.JSONDecodeError:
            data = None

    return NotificationOut(
        id=notification.id,
        user_id=notification.user_id,
        type=notification.type,
        title=notification.title,
        message=notification.message,
        data=data,
        booking_id=notification.booking_id,
        payment_id=notification.payment_id,
        is_read=notification.is_read,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Mark a notification as read"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db
    )

    notification = mark_notification_as_read(db, notification_id, user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Convert JSON data field to Python dict
    data = None
    if notification.data:
        import json
        try:
            data = json.loads(notification.data)
        except json.JSONDecodeError:
            data = None

    return NotificationOut(
        id=notification.id,
        user_id=notification.user_id,
        type=notification.type,
        title=notification.title,
        message=notification.message,
        data=data,
        booking_id=notification.booking_id,
        payment_id=notification.payment_id,
        is_read=notification.is_read,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )


@router.post("/mark-all-read")
def mark_all_as_read(
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Mark all notifications as read for the authenticated user"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db
    )

    count = mark_all_notifications_as_read(db, user.id)
    return {"message": f"Marked {count} notifications as read"}


@router.delete("/{notification_id}")
def delete_my_notification(
    notification_id: int,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Delete a notification"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db
    )

    success = delete_notification(db, notification_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"message": "Notification deleted successfully"}
