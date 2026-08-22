import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.social import BoostPublic, CreateBoostRequest
from app.services.boost_service import BoostService

router = APIRouter(tags=["boosts"])


@router.post(
    "/listings/{listing_id}/boosts", response_model=BoostPublic, status_code=status.HTTP_201_CREATED
)
def create_boost(
    listing_id: uuid.UUID,
    payload: CreateBoostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BoostService(db)
    return service.create_boost(listing_id, current_user.id, payload.duration_hours)
