import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OfferProposedBy, OfferStatus
from app.schemas.listing import ListingCardPublic


class CreateOfferRequest(BaseModel):
    amount: int = Field(gt=0, le=50_000_000, description="Montant de l'offre en FCFA")


class CounterOfferRequest(BaseModel):
    amount: int = Field(gt=0, le=50_000_000, description="Montant de la contre-offre en FCFA")


class OfferPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    listing_id: uuid.UUID
    buyer_id: uuid.UUID
    seller_id: uuid.UUID
    parent_offer_id: uuid.UUID | None
    amount: int
    status: OfferStatus
    proposed_by: OfferProposedBy
    created_at: datetime
    listing: ListingCardPublic | None = None
