import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.boost import ListingBoost


class BoostRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, boost: ListingBoost) -> ListingBoost:
        self.db.add(boost)
        self.db.flush()
        return boost

    def get_active_for_listing(self, listing_id: uuid.UUID) -> ListingBoost | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(ListingBoost)
            .where(ListingBoost.listing_id == listing_id, ListingBoost.ends_at > now)
            .order_by(ListingBoost.ends_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def active_listing_ids(self) -> set[uuid.UUID]:
        now = datetime.now(timezone.utc)
        stmt = select(ListingBoost.listing_id).where(ListingBoost.ends_at > now).distinct()
        return set(self.db.scalars(stmt))
