import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.boost import ListingBoost
from app.models.enums import ListingStatus
from app.models.listing import Listing
from app.schemas.listing import ListingSearchParams


class ListingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, listing: Listing) -> Listing:
        self.db.add(listing)
        self.db.flush()
        return listing

    def get_by_id(self, listing_id: uuid.UUID, with_relations: bool = False) -> Listing | None:
        stmt = select(Listing).where(Listing.id == listing_id)
        if with_relations:
            stmt = stmt.options(selectinload(Listing.images), joinedload(Listing.seller))
        return self.db.scalar(stmt)

    def save(self, listing: Listing) -> Listing:
        self.db.add(listing)
        self.db.flush()
        return listing

    def delete(self, listing: Listing) -> None:
        self.db.delete(listing)

    def _base_query(self, params: ListingSearchParams):
        stmt = select(Listing).where(Listing.status == ListingStatus.ACTIVE)

        if params.q:
            like = f"%{params.q.lower()}%"
            stmt = stmt.where(func.lower(Listing.title).like(like))
        if params.category_id:
            stmt = stmt.where(Listing.category_id == params.category_id)
        if params.brand_id:
            stmt = stmt.where(Listing.brand_id == params.brand_id)
        if params.size:
            stmt = stmt.where(Listing.size == params.size)
        if params.condition:
            stmt = stmt.where(Listing.condition == params.condition)
        if params.color:
            stmt = stmt.where(func.lower(Listing.color) == params.color.lower())
        if params.city:
            stmt = stmt.where(func.lower(Listing.city) == params.city.lower())
        if params.price_min is not None:
            stmt = stmt.where(Listing.price >= params.price_min)
        if params.price_max is not None:
            stmt = stmt.where(Listing.price <= params.price_max)

        return stmt

    def search(self, params: ListingSearchParams) -> tuple[list[Listing], int]:
        base_stmt = self._base_query(params)

        total = self.db.scalar(select(func.count()).select_from(base_stmt.subquery())) or 0

        if params.sort == "price_asc":
            base_stmt = base_stmt.order_by(Listing.price.asc())
        elif params.sort == "price_desc":
            base_stmt = base_stmt.order_by(Listing.price.desc())
        else:
            # Tri par défaut: annonces boostées actives en premier, puis nouveauté
            # (spec section 13: "Un produit boosté peut apparaître plus haut dans le feed").
            is_boosted = (
                select(func.count())
                .select_from(ListingBoost)
                .where(ListingBoost.listing_id == Listing.id, ListingBoost.ends_at > func.now())
                .correlate(Listing)
                .scalar_subquery()
            )
            base_stmt = base_stmt.order_by(is_boosted.desc(), Listing.created_at.desc())

        offset = (params.page - 1) * params.page_size
        base_stmt = base_stmt.options(selectinload(Listing.images)).offset(offset).limit(params.page_size)

        items = list(self.db.scalars(base_stmt))
        return items, total

    def list_by_seller(self, seller_id: uuid.UUID) -> list[Listing]:
        stmt = (
            select(Listing)
            .where(Listing.seller_id == seller_id)
            .options(selectinload(Listing.images))
            .order_by(Listing.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def increment_view_count(self, listing: Listing) -> None:
        listing.view_count += 1
        self.db.add(listing)
        self.db.flush()
