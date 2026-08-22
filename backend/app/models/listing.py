import uuid

from sqlalchemy import (
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import ListingCondition, ListingStatus
from app.models.user import User  # noqa: F401  (nécessaire pour la relation seller)


class Listing(Base, UUIDMixin, TimestampMixin):
    """
    Annonce publiée par un vendeur. Le prix est stocké en FCFA (entier,
    pas de sous-unité) sous forme de Numeric pour éviter les erreurs
    d'arrondi flottant sur les calculs de frais.
    """
    __tablename__ = "listings"
    __table_args__ = (
        # Index composé pour les requêtes de feed filtrées les plus courantes.
        Index("ix_listings_status_category", "status", "category_id"),
        Index("ix_listings_status_city", "status", "city"),
    )

    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    size: Mapped[str | None] = mapped_column(String(30), nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    condition: Mapped[ListingCondition] = mapped_column(
        SAEnum(ListingCondition, name="listing_condition"), nullable=False
    )
    price: Mapped[int] = mapped_column(Numeric(12, 0), nullable=False)  # FCFA, sans décimales

    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)

    status: Mapped[ListingStatus] = mapped_column(
        SAEnum(ListingStatus, name="listing_status"),
        default=ListingStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    favorite_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    images: Mapped[list["ListingImage"]] = relationship(
        "ListingImage", back_populates="listing", cascade="all, delete-orphan",
        order_by="ListingImage.position",
    )
    seller: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Listing id={self.id} title={self.title!r} price={self.price}>"


class ListingImage(Base, UUIDMixin, TimestampMixin):
    """
    Une photo d'une annonce (1 à 8, cf. spec section 5).
    `position` détermine l'ordre d'affichage dans la galerie.
    """
    __tablename__ = "listing_images"
    __table_args__ = (Index("ix_listing_images_listing_position", "listing_id", "position"),)

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    listing: Mapped["Listing"] = relationship("Listing", back_populates="images")
