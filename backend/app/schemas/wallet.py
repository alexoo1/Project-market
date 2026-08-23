import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PaymentMethod, WalletTransactionStatus, WalletTransactionType


class WithdrawalRequest(BaseModel):
    method: PaymentMethod
    destination: str = Field(min_length=3, max_length=120)
    amount: int = Field(gt=0)


class WalletTransactionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: WalletTransactionType
    status: WalletTransactionStatus
    amount: int
    order_id: uuid.UUID | None
    withdrawal_method: PaymentMethod | None
    withdrawal_destination: str | None
    created_at: datetime


class WalletPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: int
    transactions: list[WalletTransactionPublic]
