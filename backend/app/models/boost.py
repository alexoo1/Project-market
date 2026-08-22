import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDMixin


class ListingBoost(Base, UUIDMixin, TimestampMixin):
    """
    Mise en avant temporaire d'une annonce (spec section 13). Un boost
    est actif tant que `ends_at` n'est pas dépassé — pas de champ de
    statut à maintenir manuellement, on compare simplement à `now()`.
    """
    __tablename__ = "listing_boosts"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(nullable=False)
    ends_at: Mapped[datetime] = mapped_column(nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<ListingBoost id={self.id} listing={self.listing_id} ends_at={self.ends_at}>"
