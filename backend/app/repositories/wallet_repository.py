import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.wallet import Wallet


class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID, with_transactions: bool = False) -> Wallet | None:
        stmt = select(Wallet).where(Wallet.user_id == user_id)
        if with_transactions:
            stmt = stmt.options(selectinload(Wallet.transactions))
        return self.db.scalar(stmt)

    def create(self, wallet: Wallet) -> Wallet:
        self.db.add(wallet)
        self.db.flush()
        return wallet

    def save(self, wallet: Wallet) -> Wallet:
        self.db.add(wallet)
        self.db.flush()
        return wallet
