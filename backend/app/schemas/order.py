import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DeliveryMethod, OrderStatus, PaymentMethod


class PurchaseRequest(BaseModel):
    """
    Requête d'achat. Le prix n'est jamais transmis par le client — il est
    toujours recalculé côté serveur à partir de l'annonce (ou de l'offre
    acceptée) et de la configuration de frais.
    """
    delivery_method: DeliveryMethod
    delivery_address: str | None = Field(default=None, max_length=500)
    payment_method: PaymentMethod = PaymentMethod.MOCK


class PaymentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    provider: str
    provider_reference: str | None
    amount: int
    status: str


class DeliveryPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    provider: str
    cost: int
    status: str
    tracking_number: str | None
    carrier: str | None
    address: str | None


class OrderPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    buyer_id: uuid.UUID
    seller_id: uuid.UUID
    listing_id: uuid.UUID
    offer_id: uuid.UUID | None
    item_price: int
    platform_fee: int
    delivery_fee: int
    total: int
    payment_method: PaymentMethod
    delivery_method: DeliveryMethod
    delivery_address: str | None
    status: OrderStatus
    created_at: datetime
    payment: PaymentPublic | None
    delivery: DeliveryPublic | None
