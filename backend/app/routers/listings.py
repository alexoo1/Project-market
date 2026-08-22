import math
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.listing import Listing
from app.models.user import User
from app.schemas.listing import (
    ListingCardPublic,
    ListingCreateRequest,
    ListingDetailPublic,
    ListingSearchParams,
    ListingUpdateRequest,
    PaginatedListings,
)
from app.models.enums import ListingCondition
from app.services.listing_service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


def _to_card(listing: Listing) -> ListingCardPublic:
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


def _to_detail(listing: Listing) -> ListingDetailPublic:
    return ListingDetailPublic(
        id=listing.id,
        title=listing.title,
        description=listing.description,
        price=int(listing.price),
        size=listing.size,
        color=listing.color,
        condition=listing.condition,
        city=listing.city,
        district=listing.district,
        status=listing.status,
        view_count=listing.view_count,
        favorite_count=listing.favorite_count,
        created_at=listing.created_at,
        images=listing.images,
        seller=listing.seller,
    )


@router.post("", response_model=ListingDetailPublic, status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: ListingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ListingService(db)
    listing = service.create_listing(current_user, payload)
    listing = service.listings.get_by_id(listing.id, with_relations=True)
    return _to_detail(listing)


@router.get("", response_model=PaginatedListings)
def search_listings(
    q: str | None = None,
    category_id: uuid.UUID | None = None,
    brand_id: uuid.UUID | None = None,
    size: str | None = None,
    condition: ListingCondition | None = None,
    color: str | None = None,
    city: str | None = None,
    price_min: int | None = None,
    price_max: int | None = None,
    sort: str = Query(default="recent", pattern="^(recent|price_asc|price_desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Feed + recherche + filtres, tout en un seul endpoint (spec sections 6 et 7).
    Sans filtre, retourne le feed par défaut trié par nouveauté.
    """
    params = ListingSearchParams(
        q=q, category_id=category_id, brand_id=brand_id, size=size, condition=condition,
        color=color, city=city, price_min=price_min, price_max=price_max,
        sort=sort, page=page, page_size=page_size,
    )
    service = ListingService(db)
    items, total = service.search(params)
    return PaginatedListings(
        items=[_to_card(i) for i in items],
        page=page,
        page_size=page_size,
        total=total,
        has_next=(page * page_size) < total,
    )


@router.get("/mine", response_model=list[ListingCardPublic])
def list_my_listings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = ListingService(db)
    listings = service.list_my_listings(current_user.id)
    return [_to_card(l) for l in listings]


@router.get("/{listing_id}", response_model=ListingDetailPublic)
def get_listing(listing_id: uuid.UUID, db: Session = Depends(get_db)):
    service = ListingService(db)
    listing = service.get_listing_detail(listing_id)
    return _to_detail(listing)


@router.patch("/{listing_id}", response_model=ListingDetailPublic)
def update_listing(
    listing_id: uuid.UUID,
    payload: ListingUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ListingService(db)
    listing = service.update_listing(listing_id, current_user, payload)
    listing = service.listings.get_by_id(listing.id, with_relations=True)
    return _to_detail(listing)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ListingService(db)
    service.delete_listing(listing_id, current_user)
    return None
