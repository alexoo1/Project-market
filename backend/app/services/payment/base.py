"""
Interface abstraite de paiement (spec section 12).

Toute intégration réelle (Wave, Orange Money, MTN Mobile Money, carte
bancaire) devra implémenter cette interface. Tant que les accès
officiels ne sont pas disponibles, seul MockPaymentProvider existe.

Modèle de séquestre logique: le paiement de l'acheteur est considéré
comme "bloqué" par la plateforme jusqu'à confirmation de réception par
l'acheteur, moment où `payout_seller` est appelé.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentResult:
    success: bool
    provider_reference: str
    raw_status: str


class PaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, order_id: str, amount: int, payer_phone: str | None = None) -> PaymentResult:
        """Initie un paiement pour le montant total de la commande (FCFA)."""
        raise NotImplementedError

    @abstractmethod
    def verify_payment(self, provider_reference: str) -> PaymentResult:
        """Vérifie le statut d'un paiement déjà initié."""
        raise NotImplementedError

    @abstractmethod
    def refund_payment(self, provider_reference: str, amount: int) -> PaymentResult:
        """Rembourse tout ou partie d'un paiement (litige, annulation)."""
        raise NotImplementedError

    @abstractmethod
    def payout_seller(self, order_id: str, seller_id: str, amount: int) -> PaymentResult:
        """Débloque les fonds vers le vendeur après confirmation de réception."""
        raise NotImplementedError
