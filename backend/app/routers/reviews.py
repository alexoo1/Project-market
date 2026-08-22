import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.social import CreateReviewRequest, ReviewPublic
from app.services.review_service import ReviewService

router = APIRouter(tags=["reviews"])


@router.post("/orders/{order_id}/reviews", response_model=ReviewPublic, status_code=status.HTTP_201_CREATED)
def create_review(
    order_id: uuid.UUID,
    payload: CreateReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ReviewService(db)
    return service.create_review(order_id, current_user.id, payload.rating, payload.comment)


@router.get("/users/{user_id}/reviews", response_model=list[ReviewPublic])
def list_user_reviews(user_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ReviewService(db)
    return service.list_for_user(user_id)
