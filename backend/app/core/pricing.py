"""
Calcul des frais plateforme — point unique de vérité, jamais dupliqué
ailleurs (spec section 13: "Créer une configuration centralisée").
"""
import math

from app.core.config import settings


def compute_buyer_protection_fee(item_price: int) -> int:
    """
    Frais de protection acheteur: strictement un pourcentage du prix article,
    payés uniquement par l'acheteur, sans minimum ni frais fixe. Le vendeur
    reçoit toujours 100% du prix qu'il a fixé (ces frais s'ajoutent au total
    payé par l'acheteur, ils ne sont jamais déduits de ce que reçoit le
    vendeur — cf. WalletService.credit_from_sale qui crédite item_price).
    """
    return math.ceil(item_price * settings.BUYER_PROTECTION_FEE_PERCENT / 100)
