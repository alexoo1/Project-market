import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.offer import CounterOfferRequest, CreateOfferRequest, OfferPublic
from app.services.offer_service import OfferService

router = APIRouter(tags=["offers"])


@router.post("/listings/{listing_id}/offers", response_model=OfferPublic, status_code=status.HTTP_201_CREATED)
def create_offer(
    listing_id: uuid.UUID,
    payload: CreateOfferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    return service.create_offer(current_user.id, listing_id, payload.amount)


@router.get("/listings/{listing_id}/offers", response_model=list[OfferPublic])
def list_offers_for_listing(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    return service.list_for_listing(listing_id)


@router.get("/offers/mine", response_model=list[OfferPublic])
def list_my_offers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = OfferService(db)
    return service.list_for_user(current_user.id)


@router.patch("/offers/{offer_id}/accept", response_model=OfferPublic)
def accept_offer(
    offer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    return service.accept_offer(offer_id, current_user.id)


@router.patch("/offers/{offer_id}/reject", response_model=OfferPublic)
def reject_offer(
    offer_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    return service.reject_offer(offer_id, current_user.id)


@router.post("/offers/{offer_id}/counter", response_model=OfferPublic, status_code=status.HTTP_201_CREATED)
def counter_offer(
    offer_id: uuid.UUID,
    payload: CounterOfferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = OfferService(db)
    return service.counter_offer(offer_id, current_user.id, payload.amount)
