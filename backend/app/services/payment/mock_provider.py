"""
MockPaymentProvider: simule un paiement réussi immédiatement, pour
permettre de tester tout le parcours acheteur→vendeur sans intégration
réelle (spec section 12: "N'intègre pas de faux appels API réels si
nous n'avons pas encore les identifiants ou documentations officielles").
"""
import uuid

from app.services.payment.base import PaymentProvider, PaymentResult


class MockPaymentProvider(PaymentProvider):
    def create_payment(self, order_id: str, amount: int, payer_phone: str | None = None) -> PaymentResult:
        reference = f"mock_pay_{uuid.uuid4().hex[:12]}"
        return PaymentResult(success=True, provider_reference=reference, raw_status="succeeded")

    def verify_payment(self, provider_reference: str) -> PaymentResult:
        return PaymentResult(success=True, provider_reference=provider_reference, raw_status="succeeded")

    def refund_payment(self, provider_reference: str, amount: int) -> PaymentResult:
        reference = f"mock_refund_{uuid.uuid4().hex[:12]}"
        return PaymentResult(success=True, provider_reference=reference, raw_status="refunded")

    def payout_seller(self, order_id: str, seller_id: str, amount: int) -> PaymentResult:
        reference = f"mock_payout_{uuid.uuid4().hex[:12]}"
        return PaymentResult(success=True, provider_reference=reference, raw_status="paid_out")


def get_payment_provider() -> PaymentProvider:
    """
    Point d'extension unique: le jour où Wave/Orange Money/MTN sont
    disponibles, changer cette fonction pour retourner le vrai provider
    (éventuellement basé sur la méthode de paiement choisie), sans
    toucher au reste du code.
    """
    return MockPaymentProvider()
