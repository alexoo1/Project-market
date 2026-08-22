"""
Calcul des frais plateforme — point unique de vérité, jamais dupliqué
ailleurs (spec section 13: "Créer une configuration centralisée").
"""
import math

from app.core.config import settings


def compute_buyer_protection_fee(item_price: int) -> int:
    """
    Frais de protection acheteur: pourcentage du prix, avec un minimum.
    Exemple par défaut: 5%, minimum 300 FCFA.
    """
    percent_fee = math.ceil(item_price * settings.BUYER_PROTECTION_FEE_PERCENT / 100)
    return max(percent_fee, settings.BUYER_PROTECTION_FEE_MIN_XOF)
