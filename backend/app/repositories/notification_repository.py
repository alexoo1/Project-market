import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        return notification

    def list_for_user(self, user_id: uuid.UUID) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def unread_count(self, user_id: uuid.UUID) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Notification).where(
                Notification.user_id == user_id, Notification.is_read.is_(False)
            )
        ) or 0

    def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        return self.db.get(Notification, notification_id)

    def save(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        return notification

    def mark_all_read(self, user_id: uuid.UUID) -> None:
        notifications = self.db.scalars(
            select(Notification).where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        for n in notifications:
            n.is_read = True
            self.db.add(n)
        self.db.flush()
