import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import DeliveryMethod, OrderStatus, PaymentMethod


class Order(Base, UUIDMixin, TimestampMixin):
    """
    Commande (spec section 11). Tous les montants sont recalculés côté
    serveur au moment de la création — jamais reçus tels quels du client
    (spec section 20: "Les prix reçus depuis l'application frontend ne
    doivent jamais être considérés comme source de vérité").
    """
    __tablename__ = "orders"

    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("offers.id", ondelete="SET NULL"), nullable=True
    )

    item_price: Mapped[int] = mapped_column(Numeric(12, 0), nullable=False)
    platform_fee: Mapped[int] = mapped_column(Numeric(12, 0), nullable=False)
    delivery_fee: Mapped[int] = mapped_column(Numeric(12, 0), nullable=False)
    total: Mapped[int] = mapped_column(Numeric(12, 0), nullable=False)

    payment_method: Mapped[PaymentMethod] = mapped_column(
        SAEnum(PaymentMethod, name="payment_method"), nullable=False
    )
    delivery_method: Mapped[DeliveryMethod] = mapped_column(
        SAEnum(DeliveryMethod, name="delivery_method"), nullable=False
    )
    delivery_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING_PAYMENT,
        nullable=False,
        index=True,
    )

    payment: Mapped["Payment | None"] = relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
    delivery: Mapped["Delivery | None"] = relationship(
        "Delivery", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} status={self.status} total={self.total}>"


class Payment(Base, UUIDMixin, TimestampMixin):
    """Trace du paiement d'une commande (spec section 12)."""
    __tablename__ = "payments"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="mock")
    provider_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    amount: Mapped[int] = mapped_column(Numeric(12, 0), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")

    order: Mapped["Order"] = relationship("Order", back_populates="payment")


class Delivery(Base, UUIDMixin, TimestampMixin):
    """Trace de la livraison d'une commande (spec section 14)."""
    __tablename__ = "deliveries"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="mock")
    cost: Mapped[int] = mapped_column(Numeric(12, 0), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    tracking_number: Mapped[str | None] = mapped_column(String(60), nullable=True)
    carrier: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="delivery")
