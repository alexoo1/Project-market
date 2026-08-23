import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.pricing import compute_buyer_protection_fee
from app.models.enums import ListingStatus, NotificationType, OfferStatus, OrderStatus
from app.models.order import Delivery, Order, Payment
from app.repositories.listing_repository import ListingRepository
from app.repositories.offer_repository import OfferRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.order import PurchaseRequest
from app.services.delivery.mock_provider import get_delivery_provider
from app.services.notification_service import NotificationService
from app.services.payment.mock_provider import get_payment_provider
from app.services.wallet_service import WalletService


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.orders = OrderRepository(db)
        self.listings = ListingRepository(db)
        self.offers = OfferRepository(db)
        self.payment_provider = get_payment_provider()
        self.delivery_provider = get_delivery_provider()
        self.notifications = NotificationService(db)
        self.wallet = WalletService(db)

    def _build_order(
        self,
        buyer_id: uuid.UUID,
        seller_id: uuid.UUID,
        listing_id: uuid.UUID,
        item_price: int,
        offer_id: uuid.UUID | None,
        data: PurchaseRequest,
    ) -> Order:
        # Tout est recalculé côté serveur (spec section 20) — le client ne
        # fournit que le choix de livraison/paiement, jamais de montant.
        platform_fee = compute_buyer_protection_fee(item_price)
        delivery_quote = self.delivery_provider.quote("", data.delivery_method.value)
        total = item_price + platform_fee + delivery_quote.cost

        order = Order(
            buyer_id=buyer_id,
            seller_id=seller_id,
            listing_id=listing_id,
            offer_id=offer_id,
            item_price=item_price,
            platform_fee=platform_fee,
            delivery_fee=delivery_quote.cost,
            total=total,
            payment_method=data.payment_method,
            delivery_method=data.delivery_method,
            delivery_address=data.delivery_address,
            status=OrderStatus.PENDING_PAYMENT,
        )
        return order

    def create_order_from_listing(self, buyer_id: uuid.UUID, listing_id: uuid.UUID, data: PurchaseRequest) -> Order:
        listing = self.listings.get_by_id(listing_id)
        if not listing:
            raise NotFoundError("Annonce introuvable.")
        if listing.seller_id == buyer_id:
            raise ValidationError("Tu ne peux pas acheter ta propre annonce.")
        if listing.status != ListingStatus.ACTIVE:
            raise ValidationError("Cette annonce n'est plus disponible à l'achat.")

        order = self._build_order(buyer_id, listing.seller_id, listing.id, int(listing.price), None, data)
        order = self.orders.create(order)

        listing.status = ListingStatus.RESERVED
        self.listings.save(listing)

        self.db.commit()
        self.db.refresh(order)
        return order

    def create_order_from_offer(self, buyer_id: uuid.UUID, offer_id: uuid.UUID, data: PurchaseRequest) -> Order:
        offer = self.offers.get_by_id(offer_id)
        if not offer:
            raise NotFoundError("Offre introuvable.")
        if offer.buyer_id != buyer_id:
            raise ForbiddenError("Cette offre ne t'appartient pas.")
        if offer.status != OfferStatus.ACCEPTED:
            raise ValidationError("Cette offre n'a pas été acceptée.")

        listing = self.listings.get_by_id(offer.listing_id)
        if not listing:
            raise NotFoundError("Annonce introuvable.")

        order = self._build_order(
            buyer_id, offer.seller_id, listing.id, int(offer.amount), offer.id, data
        )
        order = self.orders.create(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order(self, order_id: uuid.UUID, current_user_id: uuid.UUID) -> Order:
        order = self.orders.get_by_id(order_id, with_relations=True)
        if not order:
            raise NotFoundError("Commande introuvable.")
        if current_user_id not in (order.buyer_id, order.seller_id):
            raise ForbiddenError("Tu n'as pas accès à cette commande.")
        return order

    def pay_order(self, order_id: uuid.UUID, current_user_id: uuid.UUID) -> Order:
        order = self.get_order(order_id, current_user_id)
        if order.buyer_id != current_user_id:
            raise ForbiddenError("Seul l'acheteur peut payer cette commande.")
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise ValidationError("Cette commande n'est pas en attente de paiement.")

        result = self.payment_provider.create_payment(str(order.id), int(order.total))
        payment = Payment(
            order_id=order.id,
            provider="mock",
            provider_reference=result.provider_reference,
            amount=order.total,
            status="succeeded" if result.success else "failed",
        )
        self.db.add(payment)

        if result.success:
            order.status = OrderStatus.PAID
        self.orders.save(order)

        if result.success:
            self.notifications.notify(
                order.seller_id, NotificationType.ORDER_PAID, "Commande payée",
                f"Une commande de {int(order.total)} FCFA a été payée, prépare l'expédition",
                related_entity_id=order.id, auto_commit=False,
            )

        self.db.commit()
        self.db.refresh(order)
        return order

    def ship_order(self, order_id: uuid.UUID, current_user_id: uuid.UUID) -> Order:
        order = self.get_order(order_id, current_user_id)
        if order.seller_id != current_user_id:
            raise ForbiddenError("Seul le vendeur peut expédier cette commande.")
        if order.status != OrderStatus.PAID:
            raise ValidationError("Cette commande doit être payée avant expédition.")

        dispatch = self.delivery_provider.dispatch(str(order.id), order.delivery_address or "")
        delivery = Delivery(
            order_id=order.id,
            provider="mock",
            cost=order.delivery_fee,
            status="in_transit",
            tracking_number=dispatch.tracking_number,
            carrier=dispatch.carrier,
            address=order.delivery_address,
        )
        self.db.add(delivery)

        order.status = OrderStatus.SHIPPED
        self.orders.save(order)

        self.notifications.notify(
            order.buyer_id, NotificationType.ORDER_SHIPPED, "Commande expédiée",
            f"Numéro de suivi: {dispatch.tracking_number}",
            related_entity_id=order.id, auto_commit=False,
        )

        self.db.commit()
        self.db.refresh(order)
        return order

    def confirm_receipt(self, order_id: uuid.UUID, current_user_id: uuid.UUID) -> Order:
        order = self.get_order(order_id, current_user_id)
        if order.buyer_id != current_user_id:
            raise ForbiddenError("Seul l'acheteur peut confirmer la réception.")
        if order.status != OrderStatus.SHIPPED:
            raise ValidationError("Cette commande n'est pas encore expédiée.")

        # Débloque les fonds vers le vendeur (paiement séquestre logique, spec section 12):
        # simule l'appel au provider de paiement, puis crédite le portefeuille vendeur
        # (seul solde réellement suivi côté plateforme tant que payout_seller est mocké).
        self.payment_provider.payout_seller(str(order.id), str(order.seller_id), int(order.item_price))
        self.wallet.credit_from_sale(order)

        order.status = OrderStatus.COMPLETED
        self.orders.save(order)

        listing = self.listings.get_by_id(order.listing_id)
        if listing:
            listing.status = ListingStatus.SOLD
            self.listings.save(listing)

        if order.delivery:
            order.delivery.status = "delivered"
            self.db.add(order.delivery)

        self.notifications.notify(
            order.seller_id, NotificationType.ORDER_COMPLETED, "Vente terminée",
            "L'acheteur a confirmé la réception, les fonds sont débloqués",
            related_entity_id=order.id, auto_commit=False,
        )

        self.db.commit()
        self.db.refresh(order)
        return order

    def cancel_order(self, order_id: uuid.UUID, current_user_id: uuid.UUID) -> Order:
        order = self.get_order(order_id, current_user_id)
        if order.buyer_id != current_user_id:
            raise ForbiddenError("Seul l'acheteur peut annuler cette commande.")
        if order.status != OrderStatus.PENDING_PAYMENT:
            raise ValidationError("Seule une commande non payée peut être annulée.")

        order.status = OrderStatus.CANCELLED
        self.orders.save(order)

        listing = self.listings.get_by_id(order.listing_id)
        if listing and listing.status == ListingStatus.RESERVED:
            listing.status = ListingStatus.ACTIVE
            self.listings.save(listing)

        self.db.commit()
        self.db.refresh(order)
        return order

    def list_my_purchases(self, user_id: uuid.UUID) -> list[Order]:
        return self.orders.list_for_buyer(user_id)

    def list_my_sales(self, user_id: uuid.UUID) -> list[Order]:
        return self.orders.list_for_seller(user_id)
