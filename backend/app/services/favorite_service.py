import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.favorite import Favorite
from app.models.listing import Listing
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.listing_repository import ListingRepository


class FavoriteService:
    def __init__(self, db: Session):
        self.db = db
        self.favorites = FavoriteRepository(db)
        self.listings = ListingRepository(db)

    def add_favorite(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> Favorite:
        listing = self.listings.get_by_id(listing_id)
        if not listing:
            raise NotFoundError("Annonce introuvable.")

        existing = self.favorites.get(user_id, listing_id)
        if existing:
            return existing  # idempotent: ajouter deux fois ne duplique pas

        favorite = self.favorites.add(Favorite(user_id=user_id, listing_id=listing_id))
        listing.favorite_count += 1
        self.listings.save(listing)
        self.db.commit()
        return favorite

    def remove_favorite(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> None:
        existing = self.favorites.get(user_id, listing_id)
        if not existing:
            return  # idempotent: retirer un favori déjà absent ne casse rien
        self.favorites.remove(existing)

        listing = self.listings.get_by_id(listing_id)
        if listing and listing.favorite_count > 0:
            listing.favorite_count -= 1
            self.listings.save(listing)
        self.db.commit()

    def list_favorites(self, user_id: uuid.UUID) -> list[Listing]:
        return self.favorites.list_for_user(user_id)
