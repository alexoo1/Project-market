import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import PaymentMethod, WalletTransactionStatus, WalletTransactionType


class Wallet(Base, UUIDMixin, TimestampMixin):
    """
    Portefeuille d'un vendeur. Le solde ne bouge jamais directement — il est
    toujours dérivé des WalletTransaction (crédit à la confirmation de
    réception d'une vente, débit lors d'un retrait), pour garder une trace
    auditable de chaque mouvement (même principe que Payment/Delivery).
    """
    __tablename__ = "wallets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    balance: Mapped[int] = mapped_column(Numeric(12, 0), default=0, nullable=False)

    transactions: Mapped[list["WalletTransaction"]] = relationship(
        "WalletTransaction", back_populates="wallet", cascade="all, delete-orphan",
        order_by="WalletTransaction.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<Wallet user_id={self.user_id} balance={self.balance}>"


class WalletTransaction(Base, UUIDMixin, TimestampMixin):
    """Un mouvement de portefeuille: crédit de vente ou retrait."""
    __tablename__ = "wallet_transactions"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[WalletTransactionType] = mapped_column(
        SAEnum(WalletTransactionType, name="wallet_transaction_type"), nullable=False
    )
    status: Mapped[WalletTransactionStatus] = mapped_column(
        SAEnum(WalletTransactionStatus, name="wallet_transaction_status"),
        default=WalletTransactionStatus.COMPLETED, nullable=False,
    )
    amount: Mapped[int] = mapped_column(Numeric(12, 0), nullable=False)
    withdrawal_method: Mapped[PaymentMethod | None] = mapped_column(
        SAEnum(PaymentMethod, name="payment_method"), nullable=True
    )
    withdrawal_destination: Mapped[str | None] = mapped_column(String(120), nullable=True)

    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<WalletTransaction type={self.type} amount={self.amount}>"
