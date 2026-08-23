import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.enums import ListingStatus
from app.models.listing import Listing, ListingImage
from app.models.user import User
from app.repositories.brand_repository import BrandRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.listing_repository import ListingRepository
from app.schemas.listing import ListingCreateRequest, ListingSearchParams, ListingUpdateRequest


class ListingService:
    def __init__(self, db: Session):
        self.db = db
        self.listings = ListingRepository(db)
        self.categories = CategoryRepository(db)
        self.brands = BrandRepository(db)

    def _validate_references(self, category_id: uuid.UUID, brand_id: uuid.UUID | None) -> None:
        if not self.categories.get_by_id(category_id):
            raise ValidationError("Catégorie invalide.")
        if brand_id and not self.brands.get_by_id(brand_id):
            raise ValidationError("Marque invalide.")

    def create_listing(self, seller: User, data: ListingCreateRequest) -> Listing:
        self._validate_references(data.category_id, data.brand_id)

        listing = Listing(
            seller_id=seller.id,
            category_id=data.category_id,
            brand_id=data.brand_id,
            title=data.title,
            description=data.description,
            size=data.size,
            color=data.color,
            condition=data.condition,
            price=data.price,
            city=data.city,
            district=data.district,
            status=ListingStatus.ACTIVE,
        )
        listing.images = [
            ListingImage(url=img.url, position=img.position) for img in data.images
        ]
        listing = self.listings.create(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def get_listing_detail(self, listing_id: uuid.UUID, increment_view: bool = True) -> Listing:
        listing = self.listings.get_by_id(listing_id, with_relations=True)
        if not listing:
            raise NotFoundError("Annonce introuvable.")
        if increment_view:
            self.listings.increment_view_count(listing)
            self.db.commit()
        return listing

    def update_listing(self, listing_id: uuid.UUID, current_user: User, data: ListingUpdateRequest) -> Listing:
        listing = self.listings.get_by_id(listing_id)
        if not listing:
            raise NotFoundError("Annonce introuvable.")
        # Règle de sécurité: un utilisateur ne peut modifier que ses propres annonces (spec section 20).
        if listing.seller_id != current_user.id:
            raise ForbiddenError("Tu ne peux modifier que tes propres annonces.")

        if data.category_id or data.brand_id:
            self._validate_references(
                data.category_id or listing.category_id, data.brand_id
            )

        update_fields = data.model_dump(exclude_unset=True)
        new_images = update_fields.pop("images", None)
        for field, value in update_fields.items():
            setattr(listing, field, value)

        if new_images is not None:
            listing.images = [
                ListingImage(url=img["url"], position=img["position"]) for img in new_images
            ]

        listing = self.listings.save(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def delete_listing(self, listing_id: uuid.UUID, current_user: User) -> None:
        listing = self.listings.get_by_id(listing_id)
        if not listing:
            raise NotFoundError("Annonce introuvable.")
        if listing.seller_id != current_user.id:
            raise ForbiddenError("Tu ne peux supprimer que tes propres annonces.")
        self.listings.delete(listing)
        self.db.commit()

    def search(self, params: ListingSearchParams) -> tuple[list[Listing], int]:
        return self.listings.search(params)

    def list_my_listings(self, seller_id: uuid.UUID) -> list[Listing]:
        return self.listings.list_by_seller(seller_id)
