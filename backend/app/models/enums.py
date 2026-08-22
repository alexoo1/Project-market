from enum import Enum


class ListingCondition(str, Enum):
    NEW_WITH_TAG = "new_with_tag"          # Neuf avec étiquette
    NEW_WITHOUT_TAG = "new_without_tag"    # Neuf sans étiquette
    VERY_GOOD = "very_good"                # Très bon état
    GOOD = "good"                          # Bon état
    SATISFACTORY = "satisfactory"          # Satisfaisant


class ListingStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RESERVED = "reserved"     # offre acceptée, en attente de paiement/livraison
    SOLD = "sold"
    HIDDEN = "hidden"         # masquée par le vendeur ou la modération


class OfferStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTERED = "countered"
    EXPIRED = "expired"
    PURCHASED = "purchased"


class OfferProposedBy(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"


class OrderStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    SELLER_CONFIRMATION = "seller_confirmation"
    READY_FOR_DELIVERY = "ready_for_delivery"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    BUYER_CONFIRMED = "buyer_confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    MOCK = "mock"
    WAVE = "wave"
    ORANGE_MONEY = "orange_money"
    MTN_MOBILE_MONEY = "mtn_mobile_money"
    CARD = "card"


class DeliveryMethod(str, Enum):
    HOME_DELIVERY = "home_delivery"
    PICKUP_POINT = "pickup_point"
    HAND_DELIVERY = "hand_delivery"


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class NotificationType(str, Enum):
    NEW_OFFER = "new_offer"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_REJECTED = "offer_rejected"
    OFFER_COUNTERED = "offer_countered"
    NEW_MESSAGE = "new_message"
    ORDER_PAID = "order_paid"
    ORDER_SHIPPED = "order_shipped"
    ORDER_COMPLETED = "order_completed"
    NEW_REVIEW = "new_review"
    NEW_FOLLOWER = "new_follower"
