import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import OfferProposedBy, OfferStatus


class Offer(Base, UUIDMixin, TimestampMixin):
    """
    Offre sur une annonce (spec section 9). La négociation est modélisée
    comme une chaîne: une contre-offre crée une nouvelle ligne `Offer`
    avec `parent_offer_id` pointant vers l'offre précédente, et marque
    celle-ci comme `countered`. `proposed_by` indique qui a fait la
    proposition courante, ce qui détermine qui a le droit d'accepter/
    refuser/contrer (toujours l'autre partie).
    """
    __tablename__ = "offers"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("offers.id", ondelete="SET NULL"), nullable=True
    )

    amount: Mapped[int] = mapped_column(Numeric(12, 0), nullable=False)  # FCFA
    status: Mapped[OfferStatus] = mapped_column(
        SAEnum(OfferStatus, name="offer_status"), default=OfferStatus.PENDING, nullable=False, index=True
    )
    proposed_by: Mapped[OfferProposedBy] = mapped_column(
        SAEnum(OfferProposedBy, name="offer_proposed_by"), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Offer id={self.id} listing={self.listing_id} amount={self.amount} status={self.status}>"
