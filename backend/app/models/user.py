from datetime import datetime

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """
    Utilisateur de la plateforme (acheteur et/ou vendeur).

    Champs prévus par la spec produit : identité, contact, localisation,
    réputation (note moyenne / nombre d'avis calculés plus tard depuis Review).
    """
    __tablename__ = "users"

    # --- Identité ---
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)  # nom ou pseudo

    # --- Contact ---
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # --- Profil ---
    profile_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)  # commune/quartier
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Réputation (dénormalisée pour lecture rapide, recalculée depuis Review) ---
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # --- État du compte ---
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # --- OTP (structure prête, non utilisée tant que OTP_ENABLED=False) ---
    phone_verified_at: Mapped[datetime | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<User id={self.id} display_name={self.display_name!r}>"
