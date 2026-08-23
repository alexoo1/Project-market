import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.social import FollowStatus
from app.schemas.user import UserPublic
from app.services.follow_service import FollowService

router = APIRouter(prefix="/users", tags=["follows"])


@router.get("/{user_id}", response_model=UserPublic)
def get_user_profile(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise NotFoundError("Utilisateur introuvable.")
    return user


@router.put("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    FollowService(db).follow(current_user.id, user_id)
    return None


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    FollowService(db).unfollow(current_user.id, user_id)
    return None


@router.get("/{user_id}/follow-status", response_model=FollowStatus)
def get_follow_status(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FollowService(db)
    return FollowStatus(
        following=service.is_following(current_user.id, user_id),
        followers_count=service.followers_count(user_id),
    )
