import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.listing import ListingCardPublic
from app.services.favorite_service import FavoriteService

router = APIRouter(prefix="/favorites", tags=["favorites"])


def _to_card(listing) -> ListingCardPublic:
    cover = listing.images[0].url if listing.images else None
    return ListingCardPublic(
        id=listing.id,
        title=listing.title,
        price=int(listing.price),
        condition=listing.condition,
        city=listing.city,
        status=listing.status,
        cover_image_url=cover,
        created_at=listing.created_at,
    )


@router.get("", response_model=list[ListingCardPublic])
def list_favorites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = FavoriteService(db)
    listings = service.list_favorites(current_user.id)
    return [_to_card(l) for l in listings]


@router.put("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_favorite(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    FavoriteService(db).add_favorite(current_user.id, listing_id)
    return None


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    FavoriteService(db).remove_favorite(current_user.id, listing_id)
    return None
