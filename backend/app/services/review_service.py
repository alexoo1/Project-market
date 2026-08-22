import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, ValidationError
from app.models.enums import NotificationType, OrderStatus
from app.models.review import Review
from app.repositories.order_repository import OrderRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.reviews = ReviewRepository(db)
        self.orders = OrderRepository(db)
        self.users = UserRepository(db)
        self.notifications = NotificationService(db)

    def create_review(
        self, order_id: uuid.UUID, reviewer_id: uuid.UUID, rating: int, comment: str | None
    ) -> Review:
        order = self.orders.get_by_id(order_id)
        if not order:
            raise ValidationError("Commande introuvable.")
        if order.status != OrderStatus.COMPLETED:
            raise ValidationError("Tu ne peux laisser un avis que sur une transaction terminée.")
        if reviewer_id not in (order.buyer_id, order.seller_id):
            raise ForbiddenError("Tu ne fais pas partie de cette transaction.")

        existing = self.reviews.get_by_order_and_reviewer(order_id, reviewer_id)
        if existing:
            raise ConflictError("Tu as déjà laissé un avis pour cette transaction.")

        reviewee_id = order.seller_id if reviewer_id == order.buyer_id else order.buyer_id

        review = Review(
            order_id=order_id, reviewer_id=reviewer_id, reviewee_id=reviewee_id,
            rating=rating, comment=comment,
        )
        review = self.reviews.create(review)

        # Recalcule et dénormalise la note moyenne sur le profil (lecture rapide)
        avg_rating, count = self.reviews.stats_for_user(reviewee_id)
        reviewee = self.users.get_by_id(reviewee_id)
        if reviewee:
            reviewee.average_rating = avg_rating
            reviewee.review_count = count
            self.users.save(reviewee)

        self.notifications.notify(
            reviewee_id, NotificationType.NEW_REVIEW, "Nouvel avis reçu",
            f"{rating}/5" + (f" — {comment}" if comment else ""),
            related_entity_id=review.id, auto_commit=False,
        )

        self.db.commit()
        self.db.refresh(review)
        return review

    def list_for_user(self, user_id: uuid.UUID) -> list[Review]:
        return self.reviews.list_for_user(user_id)
