import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_order_and_reviewer(self, order_id: uuid.UUID, reviewer_id: uuid.UUID) -> Review | None:
        return self.db.scalar(
            select(Review).where(Review.order_id == order_id, Review.reviewer_id == reviewer_id)
        )

    def create(self, review: Review) -> Review:
        self.db.add(review)
        self.db.flush()
        return review

    def list_for_user(self, user_id: uuid.UUID) -> list[Review]:
        stmt = select(Review).where(Review.reviewee_id == user_id).order_by(Review.created_at.desc())
        return list(self.db.scalars(stmt))

    def stats_for_user(self, user_id: uuid.UUID) -> tuple[float, int]:
        row = self.db.execute(
            select(func.avg(Review.rating), func.count(Review.id)).where(Review.reviewee_id == user_id)
        ).one()
        avg_rating, count = row
        return (round(float(avg_rating), 2) if avg_rating else 0.0, count or 0)
