import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.brand import Brand


class BrandRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Brand]:
        return list(self.db.scalars(select(Brand).order_by(Brand.name)))

    def get_by_id(self, brand_id: uuid.UUID) -> Brand | None:
        return self.db.get(Brand, brand_id)

    def get_by_slug(self, slug: str) -> Brand | None:
        return self.db.scalar(select(Brand).where(Brand.slug == slug))

    def create(self, brand: Brand) -> Brand:
        self.db.add(brand)
        self.db.flush()
        return brand
