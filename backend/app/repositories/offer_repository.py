import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.offer import Offer


class OfferRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, offer_id: uuid.UUID) -> Offer | None:
        return self.db.get(Offer, offer_id)

    def create(self, offer: Offer) -> Offer:
        self.db.add(offer)
        self.db.flush()
        return offer

    def save(self, offer: Offer) -> Offer:
        self.db.add(offer)
        self.db.flush()
        return offer

    def list_for_listing(self, listing_id: uuid.UUID) -> list[Offer]:
        stmt = select(Offer).where(Offer.listing_id == listing_id).order_by(Offer.created_at.desc())
        return list(self.db.scalars(stmt))

    def list_for_user(self, user_id: uuid.UUID) -> list[Offer]:
        stmt = (
            select(Offer)
            .where(or_(Offer.buyer_id == user_id, Offer.seller_id == user_id))
            .order_by(Offer.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def get_active_offer_for(self, listing_id: uuid.UUID, buyer_id: uuid.UUID) -> Offer | None:
        """Retourne l'offre pending/countered la plus récente entre cet acheteur et cette annonce."""
        stmt = (
            select(Offer)
            .where(
                Offer.listing_id == listing_id,
                Offer.buyer_id == buyer_id,
                Offer.status.in_(["pending", "countered"]),
            )
            .order_by(Offer.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
