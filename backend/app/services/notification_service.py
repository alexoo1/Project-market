import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import NotificationType
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationRepository(db)

    def notify(
        self,
        user_id: uuid.UUID,
        notif_type: NotificationType,
        title: str,
        body: str | None = None,
        related_entity_id: uuid.UUID | None = None,
        auto_commit: bool = True,
    ) -> Notification:
        """
        Crée une notification. `auto_commit=False` permet de l'appeler
        depuis un autre service qui gère déjà sa propre transaction,
        pour éviter des commits partiels imbriqués.
        """
        notification = Notification(
            user_id=user_id, type=notif_type, title=title, body=body, related_entity_id=related_entity_id
        )
        self.notifications.create(notification)
        if auto_commit:
            self.db.commit()
        return notification

    def list_for_user(self, user_id: uuid.UUID) -> list[Notification]:
        return self.notifications.list_for_user(user_id)

    def unread_count(self, user_id: uuid.UUID) -> int:
        return self.notifications.unread_count(user_id)

    def mark_all_read(self, user_id: uuid.UUID) -> None:
        self.notifications.mark_all_read(user_id)
        self.db.commit()

    def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        notification = self.notifications.get_by_id(notification_id)
        if not notification:
            raise NotFoundError("Notification introuvable.")
        if notification.user_id != user_id:
            raise ForbiddenError("Cette notification ne t'appartient pas.")
        notification.is_read = True
        self.notifications.save(notification)
        self.db.commit()
        return notification
