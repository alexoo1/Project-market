import uuid

from app.services.delivery.base import DeliveryDispatchResult, DeliveryProvider, DeliveryQuote

# Tarifs fixes simples pour le MVP (spec section 14: livraison à domicile,
# point relais, remise en main propre). Le point de configuration unique
# permet de brancher un vrai calcul par distance/poids plus tard.
_METHOD_COSTS = {
    "home_delivery": 2000,
    "pickup_point": 1000,
    "hand_delivery": 0,
}


class MockDeliveryProvider(DeliveryProvider):
    def quote(self, city: str, delivery_method: str) -> DeliveryQuote:
        cost = _METHOD_COSTS.get(delivery_method, 1500)
        return DeliveryQuote(cost=cost, carrier="Livreur Project Market", estimated_days=2)

    def dispatch(self, order_id: str, address: str) -> DeliveryDispatchResult:
        tracking_number = f"PM-{uuid.uuid4().hex[:10].upper()}"
        return DeliveryDispatchResult(tracking_number=tracking_number, carrier="Livreur Project Market", status="in_transit")


def get_delivery_provider() -> DeliveryProvider:
    return MockDeliveryProvider()
