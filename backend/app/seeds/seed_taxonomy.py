"""
Seed des catégories et marques de base (spec section 5 et section 22).

Usage:
    python -m app.seeds.seed_taxonomy
"""
import re

from app.database.session import SessionLocal
from app.models.brand import Brand
from app.models.category import Category

CATEGORY_NAMES = [
    "Femme", "Homme", "Enfant", "Chaussures", "Sacs",
    "Accessoires", "Streetwear", "Sneakers",
]

BRAND_NAMES = [
    "Nike", "Adidas", "Zara", "H&M", "Levi's", "Fait main", "Lions", "Puma",
]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def run() -> None:
    db = SessionLocal()
    try:
        existing_categories = {c.slug for c in db.query(Category).all()}
        for order, name in enumerate(CATEGORY_NAMES):
            slug = slugify(name)
            if slug in existing_categories:
                continue
            db.add(Category(name=name, slug=slug, display_order=order))

        existing_brands = {b.slug for b in db.query(Brand).all()}
        for name in BRAND_NAMES:
            slug = slugify(name)
            if slug in existing_brands:
                continue
            db.add(Brand(name=name, slug=slug))

        db.commit()
        print(f"Seed terminé: {len(CATEGORY_NAMES)} catégories, {len(BRAND_NAMES)} marques (idempotent).")
    finally:
        db.close()


if __name__ == "__main__":
    run()
