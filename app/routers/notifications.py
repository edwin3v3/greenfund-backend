from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, desc
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models import Notification, User
from app.security import get_current_user
from app.schemas import NotificationRead  # Assuming you'll create this schema

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationRead])
def get_my_notifications(
    skip: int = 0,
    limit: int = 20,  # Paginate notifications
    include_read: bool = False,  # Option to include read ones
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications for the current user, newest first.
    By default, only fetches unread notifications.
    """
    statement = select(Notification).where(
        Notification.user_id == current_user.id)

    if not include_read:
        statement = statement.where(Notification.is_read == False)

    statement = statement.order_by(
        desc(Notification.created_at)).offset(skip).limit(limit)

    notifications = db.exec(statement).all()
    return notifications


@router.get("/unread-count", response_model=dict)
def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the count of unread notifications for the current user.
    """
    # Use scalar_one() to get the integer result rather than a Row/tuple
    # SQLModel's Session.exec may return a ScalarResult depending on SQLAlchemy
    # version; call .one() to retrieve the scalar count value when appropriate.
    count = db.exec(
        select(func.count(Notification.id))
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)
    ).one()

    return {"unread_count": int(count)}


@router.post("/{notification_id}/mark-read", status_code=status.HTTP_204_NO_CONTENT)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a specific notification as read.
    """
    notification = db.get(Notification, notification_id)

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to modify this notification")

    if not notification.is_read:
        notification.is_read = True
        db.add(notification)
        db.commit()

    return  # Return 204 No Content


@router.post("/mark-all-read", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all unread notifications for the current user as read.
    """
    # Fetch all unread notifications for the user
    unread_notifications = db.exec(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)
    ).all()

    if not unread_notifications:
        return  # Nothing to mark

    updated_count = 0
    try:
        for notification in unread_notifications:
            notification.is_read = True
            db.add(notification)
            updated_count += 1

        db.commit()
        print(
            f"Marked {updated_count} notifications as read for user {current_user.id}")
    except Exception as e:
        db.rollback()
        print(
            f"Error marking all notifications read for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500, detail="Could not mark all notifications as read")

    return  # Return 204 No Content
