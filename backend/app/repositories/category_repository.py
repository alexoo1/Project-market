import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Category]:
        return list(self.db.scalars(select(Category).order_by(Category.display_order, Category.name)))

    def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        return self.db.get(Category, category_id)

    def get_by_slug(self, slug: str) -> Category | None:
        return self.db.scalar(select(Category).where(Category.slug == slug))

    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.flush()
        return category
