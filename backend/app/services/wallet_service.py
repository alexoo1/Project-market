import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.models.enums import PaymentMethod, WalletTransactionStatus, WalletTransactionType
from app.models.order import Order
from app.models.wallet import Wallet, WalletTransaction
from app.repositories.wallet_repository import WalletRepository


class WalletService:
    def __init__(self, db: Session):
        self.db = db
        self.wallets = WalletRepository(db)

    def get_or_create_wallet(self, user_id: uuid.UUID, with_transactions: bool = False) -> Wallet:
        """
        Ne commit jamais elle-même (juste un flush) — appelée aussi bien en
        lecture seule que depuis des transactions plus larges (ex. confirm_receipt),
        c'est à l'appelant de premier niveau de commit.
        """
        wallet = self.wallets.get_by_user_id(user_id, with_transactions=with_transactions)
        if wallet:
            return wallet
        return self.wallets.create(Wallet(user_id=user_id, balance=0))

    def credit_from_sale(self, order: Order) -> WalletTransaction:
        """
        Crédite le portefeuille du vendeur du prix article (hors frais
        plateforme/livraison) — appelé uniquement quand l'acheteur confirme
        la réception (séquestre logique, cf. OrderService.confirm_receipt).
        """
        wallet = self.get_or_create_wallet(order.seller_id)
        wallet.balance = int(wallet.balance) + int(order.item_price)
        self.wallets.save(wallet)

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            order_id=order.id,
            type=WalletTransactionType.SALE_CREDIT,
            status=WalletTransactionStatus.COMPLETED,
            amount=order.item_price,
        )
        self.db.add(transaction)
        self.db.flush()
        return transaction

    def request_withdrawal(
        self, user_id: uuid.UUID, method: PaymentMethod, destination: str, amount: int
    ) -> WalletTransaction:
        wallet = self.get_or_create_wallet(user_id)
        if amount <= 0:
            raise ValidationError("Le montant du retrait doit être positif.")
        if amount > int(wallet.balance):
            raise ValidationError("Solde insuffisant pour ce retrait.")

        wallet.balance = int(wallet.balance) - amount
        self.wallets.save(wallet)

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type=WalletTransactionType.WITHDRAWAL,
            status=WalletTransactionStatus.COMPLETED,
            amount=amount,
            withdrawal_method=method,
            withdrawal_destination=destination,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(wallet)
        self.db.refresh(transaction)
        return transaction
