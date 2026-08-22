import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.favorite import Favorite
from app.models.listing import Listing


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> Favorite | None:
        return self.db.scalar(
            select(Favorite).where(Favorite.user_id == user_id, Favorite.listing_id == listing_id)
        )

    def add(self, favorite: Favorite) -> Favorite:
        self.db.add(favorite)
        self.db.flush()
        return favorite

    def remove(self, favorite: Favorite) -> None:
        self.db.delete(favorite)

    def list_for_user(self, user_id: uuid.UUID) -> list[Listing]:
        stmt = (
            select(Listing)
            .join(Favorite, Favorite.listing_id == Listing.id)
            .where(Favorite.user_id == user_id)
            .options(selectinload(Listing.images))
            .order_by(Favorite.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def count_for_listing(self, listing_id: uuid.UUID) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Favorite).where(Favorite.listing_id == listing_id)
        ) or 0
