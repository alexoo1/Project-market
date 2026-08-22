import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.boost import ListingBoost
from app.repositories.boost_repository import BoostRepository
from app.repositories.listing_repository import ListingRepository


class BoostService:
    def __init__(self, db: Session):
        self.db = db
        self.boosts = BoostRepository(db)
        self.listings = ListingRepository(db)

    def create_boost(self, listing_id: uuid.UUID, seller_id: uuid.UUID, duration_hours: int) -> ListingBoost:
        listing = self.listings.get_by_id(listing_id)
        if not listing:
            raise NotFoundError("Annonce introuvable.")
        if listing.seller_id != seller_id:
            raise ForbiddenError("Tu ne peux booster que tes propres annonces.")
        if duration_hours not in settings.BOOST_DURATIONS_HOURS:
            allowed = ", ".join(str(h) for h in settings.BOOST_DURATIONS_HOURS)
            raise ValidationError(f"Durée de boost invalide. Valeurs autorisées: {allowed} heures.")

        now = datetime.now(timezone.utc)
        boost = ListingBoost(
            listing_id=listing_id,
            duration_hours=duration_hours,
            starts_at=now,
            ends_at=now + timedelta(hours=duration_hours),
        )
        boost = self.boosts.create(boost)
        self.db.commit()
        self.db.refresh(boost)
        return boost

    def get_active_boost(self, listing_id: uuid.UUID) -> ListingBoost | None:
        return self.boosts.get_active_for_listing(listing_id)
