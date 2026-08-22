import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.enums import NotificationType
from app.models.follow import Follow
from app.repositories.follow_repository import FollowRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService


class FollowService:
    def __init__(self, db: Session):
        self.db = db
        self.follows = FollowRepository(db)
        self.users = UserRepository(db)
        self.notifications = NotificationService(db)

    def follow(self, follower_id: uuid.UUID, followee_id: uuid.UUID) -> Follow:
        if follower_id == followee_id:
            raise ValidationError("Tu ne peux pas te suivre toi-même.")
        if not self.users.get_by_id(followee_id):
            raise NotFoundError("Utilisateur introuvable.")

        existing = self.follows.get(follower_id, followee_id)
        if existing:
            return existing  # idempotent

        follow = self.follows.create(Follow(follower_id=follower_id, followee_id=followee_id))
        self.notifications.notify(
            followee_id, NotificationType.NEW_FOLLOWER, "Nouvel abonné",
            related_entity_id=follower_id, auto_commit=False,
        )
        self.db.commit()
        return follow

    def unfollow(self, follower_id: uuid.UUID, followee_id: uuid.UUID) -> None:
        existing = self.follows.get(follower_id, followee_id)
        if not existing:
            return  # idempotent
        self.follows.remove(existing)
        self.db.commit()

    def is_following(self, follower_id: uuid.UUID, followee_id: uuid.UUID) -> bool:
        return self.follows.get(follower_id, followee_id) is not None

    def followers_count(self, user_id: uuid.UUID) -> int:
        return self.follows.count_followers(user_id)

    def following_count(self, user_id: uuid.UUID) -> int:
        return self.follows.count_following(user_id)
