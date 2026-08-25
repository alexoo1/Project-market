"""
Seed des catégories (avec sous-catégories) et marques de base
(spec section 5 et section 22).

Usage:
    python -m app.seeds.seed_taxonomy
"""
import re
import unicodedata

from app.database.session import SessionLocal
from app.models.brand import Brand
from app.models.category import Category

CATEGORY_NAMES = [
    "Femmes", "Hommes", "Articles de créateurs", "Enfants", "Maison",
    "Électronique", "Livres et médias", "Loisirs et collections", "Sport",
]

SUBCATEGORIES = {
    "Femmes": ["Vêtements", "Chaussures", "Sacs", "Accessoires", "Beauté"],
    "Hommes": ["Vêtements", "Chaussures", "Accessoires", "Soins"],
    "Articles de créateurs": ["Vêtements", "Chaussures", "Sacs", "Bijoux et montres", "Accessoires"],
    "Enfants": ["Vêtements filles", "Vêtements garçons", "Chaussures", "Jouets", "Puériculture"],
    "Maison": ["Décoration", "Cuisine et arts de la table", "Linge de maison", "Rangement", "Jardin et extérieur"],
    "Électronique": ["Téléphones et accessoires", "Ordinateurs et tablettes", "Audio et casques", "Consoles et jeux vidéo", "Photo et caméras"],
    "Livres et médias": ["Livres", "BD et mangas", "Films et séries", "Musique", "Jeux de société"],
    "Loisirs et collections": ["Instruments de musique", "Art et collection", "Loisirs créatifs", "Jouets et jeux", "Vintage"],
    "Sport": ["Vêtements de sport", "Chaussures de sport", "Fitness et musculation", "Vélo", "Sports de raquette"],
}

BRAND_NAMES = [
    "Nike", "Adidas", "Zara", "H&M", "Levi's", "Fait main", "Lions", "Puma",
]


def slugify(name: str) -> str:
    ascii_only = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")


def run() -> None:
    db = SessionLocal()
    try:
        # Les catégories qui ne correspondent plus à la taxonomie actuelle
        # (ex: anciens "Streetwear"/"Sneakers" en catégories principales)
        # sont supprimées. Le FK category_id des annonces est en RESTRICT,
        # donc cette purge échoue explicitement s'il existe déjà des annonces
        # rattachées à une catégorie obsolète — jamais de suppression silencieuse.
        valid_slugs = {slugify(name) for name in CATEGORY_NAMES}
        for parent_name, sub_names in SUBCATEGORIES.items():
            parent_slug = slugify(parent_name)
            valid_slugs.update(f"{parent_slug}-{slugify(sub_name)}" for sub_name in sub_names)

        existing_categories = {c.slug: c for c in db.query(Category).all()}
        obsolete = [c for slug, c in existing_categories.items() if slug not in valid_slugs]
        for c in obsolete:
            db.delete(c)
        if obsolete:
            db.flush()
        existing_categories = {slug: c for slug, c in existing_categories.items() if slug in valid_slugs}

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
