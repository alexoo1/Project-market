import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.models.enums import ListingStatus, NotificationType, OfferProposedBy, OfferStatus
from app.models.offer import Offer
from app.repositories.listing_repository import ListingRepository
from app.repositories.offer_repository import OfferRepository
from app.services.notification_service import NotificationService


class OfferService:
    def __init__(self, db: Session):
        self.db = db
        self.offers = OfferRepository(db)
        self.listings = ListingRepository(db)
        self.notifications = NotificationService(db)

    def create_offer(self, buyer_id: uuid.UUID, listing_id: uuid.UUID, amount: int) -> Offer:
        listing = self.listings.get_by_id(listing_id)
        if not listing:
            raise NotFoundError("Annonce introuvable.")
        if listing.seller_id == buyer_id:
            raise ValidationError("Tu ne peux pas faire une offre sur ta propre annonce.")
        if listing.status != ListingStatus.ACTIVE:
            raise ValidationError("Cette annonce n'est plus disponible.")

        existing = self.offers.get_active_offer_for(listing_id, buyer_id)
        if existing:
            raise ConflictError("Tu as déjà une offre en cours sur cette annonce.")

        offer = Offer(
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            amount=amount,
            status=OfferStatus.PENDING,
            proposed_by=OfferProposedBy.BUYER,
        )
        offer = self.offers.create(offer)
        self.notifications.notify(
            listing.seller_id, NotificationType.NEW_OFFER,
            "Nouvelle offre reçue", f"{amount} FCFA sur '{listing.title}'",
            related_entity_id=offer.id, auto_commit=False,
        )
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def _get_offer_or_404(self, offer_id: uuid.UUID) -> Offer:
        offer = self.offers.get_by_id(offer_id)
        if not offer:
            raise NotFoundError("Offre introuvable.")
        return offer

    def _assert_responder(self, offer: Offer, current_user_id: uuid.UUID) -> None:
        """
        Seule la partie qui N'A PAS fait la dernière proposition peut
        répondre (accepter / refuser / contrer) — cf. spec section 9.
        """
        if offer.status not in (OfferStatus.PENDING, OfferStatus.COUNTERED):
            raise ValidationError("Cette offre n'est plus modifiable.")

        expected_responder_id = offer.seller_id if offer.proposed_by == OfferProposedBy.BUYER else offer.buyer_id
        if current_user_id != expected_responder_id:
            raise ForbiddenError("Ce n'est pas à toi de répondre à cette offre.")

    def accept_offer(self, offer_id: uuid.UUID, current_user_id: uuid.UUID) -> Offer:
        offer = self._get_offer_or_404(offer_id)
        self._assert_responder(offer, current_user_id)

        offer.status = OfferStatus.ACCEPTED
        self.offers.save(offer)

        listing = self.listings.get_by_id(offer.listing_id)
        if listing:
            listing.status = ListingStatus.RESERVED
            self.listings.save(listing)

        notify_target = offer.buyer_id if offer.proposed_by == OfferProposedBy.BUYER else offer.seller_id
        self.notifications.notify(
            notify_target, NotificationType.OFFER_ACCEPTED,
            "Offre acceptée", f"Ton offre de {int(offer.amount)} FCFA a été acceptée",
            related_entity_id=offer.id, auto_commit=False,
        )

        self.db.commit()
        self.db.refresh(offer)
        return offer

    def reject_offer(self, offer_id: uuid.UUID, current_user_id: uuid.UUID) -> Offer:
        offer = self._get_offer_or_404(offer_id)
        self._assert_responder(offer, current_user_id)

        offer.status = OfferStatus.REJECTED
        self.offers.save(offer)

        notify_target = offer.buyer_id if offer.proposed_by == OfferProposedBy.BUYER else offer.seller_id
        self.notifications.notify(
            notify_target, NotificationType.OFFER_REJECTED,
            "Offre refusée", f"Ton offre de {int(offer.amount)} FCFA a été refusée",
            related_entity_id=offer.id, auto_commit=False,
        )
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def counter_offer(self, offer_id: uuid.UUID, current_user_id: uuid.UUID, amount: int) -> Offer:
        original = self._get_offer_or_404(offer_id)
        self._assert_responder(original, current_user_id)

        original.status = OfferStatus.COUNTERED
        self.offers.save(original)

        countered_by = (
            OfferProposedBy.SELLER if original.proposed_by == OfferProposedBy.BUYER else OfferProposedBy.BUYER
        )
        new_offer = Offer(
            listing_id=original.listing_id,
            buyer_id=original.buyer_id,
            seller_id=original.seller_id,
            parent_offer_id=original.id,
            amount=amount,
            status=OfferStatus.PENDING,
            proposed_by=countered_by,
        )
        new_offer = self.offers.create(new_offer)

        notify_target = new_offer.seller_id if countered_by == OfferProposedBy.BUYER else new_offer.buyer_id
        self.notifications.notify(
            notify_target, NotificationType.OFFER_COUNTERED,
            "Contre-offre reçue", f"Nouvelle proposition: {amount} FCFA",
            related_entity_id=new_offer.id, auto_commit=False,
        )
        self.db.commit()
        self.db.refresh(new_offer)
        return new_offer

    def list_for_listing(self, listing_id: uuid.UUID) -> list[Offer]:
        return self.offers.list_for_listing(listing_id)

    def list_for_user(self, user_id: uuid.UUID) -> list[Offer]:
        return self.offers.list_for_user(user_id)
