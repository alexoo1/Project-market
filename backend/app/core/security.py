"""
Utilitaires de sécurité: hashing des mots de passe et gestion des JWT.

Deux types de tokens sont émis :
- access token  : courte durée de vie, utilisé pour authentifier les requêtes.
- refresh token : longue durée de vie, utilisé uniquement pour obtenir un
  nouvel access token via /auth/refresh.
"""
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# bcrypt tronque silencieusement au-delà de 72 octets: on refuse
# explicitement les mots de passe trop longs plutôt que de les tronquer.
_MAX_PASSWORD_BYTES = 72


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > _MAX_PASSWORD_BYTES:
        raise ValueError("Le mot de passe est trop long (72 octets maximum).")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),  # utile plus tard pour la révocation
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str) -> str:
    return _create_token(
        user_id, TokenType.ACCESS, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        user_id, TokenType.REFRESH, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def create_password_reset_token(user_id: str) -> str:
    return _create_token(
        user_id,
        TokenType.PASSWORD_RESET,
        timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str, expected_type: TokenType) -> str:
    """
    Décode un token et retourne le user_id (subject).
    Lève une JWTError si le token est invalide, expiré, ou du mauvais type.
    """
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != expected_type.value:
        raise JWTError("Type de token invalide")
    subject = payload.get("sub")
    if not subject:
        raise JWTError("Token sans sujet")
    return subject
