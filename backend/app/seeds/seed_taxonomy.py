"""
Seed des catégories (avec sous-catégories) et marques de base
(spec section 5 et section 22).

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

SUBCATEGORIES = {
    "Femme": ["Vêtements", "Chaussures", "Sacs", "Accessoires", "Beauté"],
    "Homme": ["Vêtements", "Chaussures", "Accessoires", "Soins"],
    "Enfant": ["Vêtements filles", "Vêtements garçons", "Chaussures", "Jouets", "Puériculture"],
    "Chaussures": ["Baskets", "Talons", "Bottes", "Sandales", "Mocassins"],
    "Sacs": ["Sacs à main", "Sacs à dos", "Pochettes", "Valises", "Sacs de sport"],
    "Accessoires": ["Bijoux", "Montres", "Ceintures", "Écharpes et foulards", "Lunettes"],
    "Streetwear": ["T-shirts et sweats", "Vestes", "Pantalons et joggers", "Casquettes"],
    "Sneakers": ["Running", "Basketball", "Lifestyle", "Skate", "Éditions limitées"],
}

BRAND_NAMES = [
    "Nike", "Adidas", "Zara", "H&M", "Levi's", "Fait main", "Lions", "Puma",
]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def run() -> None:
    db = SessionLocal()
    try:
        existing_categories = {c.slug: c for c in db.query(Category).all()}
        for order, name in enumerate(CATEGORY_NAMES):
            slug = slugify(name)
            if slug in existing_categories:
                continue
            category = Category(name=name, slug=slug, display_order=order)
            db.add(category)
            db.flush()
            existing_categories[slug] = category

        for parent_name, sub_names in SUBCATEGORIES.items():
            parent = existing_categories[slugify(parent_name)]
            for order, sub_name in enumerate(sub_names):
                slug = f"{parent.slug}-{slugify(sub_name)}"
                if slug in existing_categories:
                    continue
                sub = Category(name=sub_name, slug=slug, parent_id=parent.id, display_order=order)
                db.add(sub)
                existing_categories[slug] = sub

        existing_brands = {b.slug for b in db.query(Brand).all()}
        for name in BRAND_NAMES:
            slug = slugify(name)
            if slug in existing_brands:
                continue
            db.add(Brand(name=name, slug=slug))

        db.commit()
        total_sub = sum(len(v) for v in SUBCATEGORIES.values())
        print(
            f"Seed terminé: {len(CATEGORY_NAMES)} catégories, {total_sub} sous-catégories, "
            f"{len(BRAND_NAMES)} marques (idempotent)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
