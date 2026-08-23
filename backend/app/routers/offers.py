import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.offer import Offer
from app.models.user import User
from app.repositories.listing_repository import ListingRepository
from app.routers.listings import _to_card
from app.schemas.offer import CounterOfferRequest, CreateOfferRequest, OfferPublic
from app.services.offer_service import OfferService

router = APIRouter(tags=["offers"])


def _to_offer_public(offer: Offer, listings_repo: ListingRepository) -> OfferPublic:
    listing = listings_repo.get_by_id(offer.listing_id)
    return OfferPublic(
        id=offer.id,
        listing_id=offer.listing_id,
        buyer_id=offer.buyer_id,
        seller_id=offer.seller_id,
        parent_offer_id=offer.parent_offer_id,
        amount=int(offer.amount),
        status=offer.status,
        proposed_by=offer.proposed_by,
        created_at=offer.created_at,
        listing=_to_card(listing) if listing else None,
    )


@router.post("/listings/{listing_id}/offers", response_model=OfferPublic, status_code=status.HTTP_201_CREATED)
def create_offer(
    listing_id: uuid.UUID,
    payload: CreateOfferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    offer = service.create_offer(current_user.id, listing_id, payload.amount)
    return _to_offer_public(offer, service.listings)


@router.get("/listings/{listing_id}/offers", response_model=list[OfferPublic])
def list_offers_for_listing(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    offers = service.list_for_listing(listing_id)
    return [_to_offer_public(o, service.listings) for o in offers]


@router.get("/offers/mine", response_model=list[OfferPublic])
def list_my_offers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = OfferService(db)
    offers = service.list_for_user(current_user.id)
    return [_to_offer_public(o, service.listings) for o in offers]


@router.patch("/offers/{offer_id}/accept", response_model=OfferPublic)
def accept_offer(
    offer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    offer = service.accept_offer(offer_id, current_user.id)
    return _to_offer_public(offer, service.listings)


@router.patch("/offers/{offer_id}/reject", response_model=OfferPublic)
def reject_offer(
    offer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    offer = service.reject_offer(offer_id, current_user.id)
    return _to_offer_public(offer, service.listings)


@router.post("/offers/{offer_id}/counter", response_model=OfferPublic, status_code=status.HTTP_201_CREATED)
def counter_offer(
    offer_id: uuid.UUID,
    payload: CounterOfferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    offer = service.counter_offer(offer_id, current_user.id, payload.amount)
    return _to_offer_public(offer, service.listings)
