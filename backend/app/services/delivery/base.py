"""
Interface abstraite de livraison (spec section 14).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DeliveryQuote:
    cost: int  # FCFA
    carrier: str
    estimated_days: int


@dataclass
class DeliveryDispatchResult:
    tracking_number: str
    carrier: str
    status: str


class DeliveryProvider(ABC):
    @abstractmethod
    def quote(self, city: str, delivery_method: str) -> DeliveryQuote:
        """Retourne un devis de livraison pour une ville et un mode donnés."""
        raise NotImplementedError

    @abstractmethod
    def dispatch(self, order_id: str, address: str) -> DeliveryDispatchResult:
        """Déclenche l'expédition et retourne un numéro de suivi."""
        raise NotImplementedError
