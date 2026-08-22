import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.follow import Follow


class FollowRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, follower_id: uuid.UUID, followee_id: uuid.UUID) -> Follow | None:
        return self.db.scalar(
            select(Follow).where(Follow.follower_id == follower_id, Follow.followee_id == followee_id)
        )

    def create(self, follow: Follow) -> Follow:
        self.db.add(follow)
        self.db.flush()
        return follow

    def remove(self, follow: Follow) -> None:
        self.db.delete(follow)

    def count_followers(self, user_id: uuid.UUID) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Follow).where(Follow.followee_id == user_id)
        ) or 0

    def count_following(self, user_id: uuid.UUID) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
        ) or 0
