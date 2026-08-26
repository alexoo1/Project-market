import uuid

from app.services.delivery.base import DeliveryDispatchResult, DeliveryProvider, DeliveryQuote

# Tarifs fixes simples pour le MVP (spec section 14: livraison à domicile,
# point relais, remise en main propre). Yango gère la livraison pour Vendi
# Market en Côte d'Ivoire — ce point de configuration unique permet de
# brancher le vrai calcul par distance/poids de leur API plus tard.
_METHOD_COSTS = {
    "home_delivery": 2000,
    "pickup_point": 1000,
    "hand_delivery": 0,
}

_CARRIER = "Yango"


class YangoDeliveryProvider(DeliveryProvider):
    def quote(self, city: str, delivery_method: str) -> DeliveryQuote:
        cost = _METHOD_COSTS.get(delivery_method, 1500)
        return DeliveryQuote(cost=cost, carrier=_CARRIER, estimated_days=2)

    def dispatch(self, order_id: str, address: str) -> DeliveryDispatchResult:
        tracking_number = f"YG-{uuid.uuid4().hex[:10].upper()}"
        return DeliveryDispatchResult(tracking_number=tracking_number, carrier=_CARRIER, status="in_transit")


def get_delivery_provider() -> DeliveryProvider:
    return YangoDeliveryProvider()
