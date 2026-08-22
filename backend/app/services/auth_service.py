"""
Logique métier de l'authentification.

Le service orchestre le repository + la sécurité (hash, JWT). Les routers
ne font qu'appeler ces méthodes et traduire les exceptions en réponses HTTP.
"""
import uuid

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError, ValidationError
from app.core.security import (
    TokenType,
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: RegisterRequest) -> User:
        if self.users.get_by_phone(data.phone):
            raise ConflictError("Un compte existe déjà avec ce numéro de téléphone.")
        if data.email and self.users.get_by_email(data.email):
            raise ConflictError("Un compte existe déjà avec cet email.")

        try:
            hashed = hash_password(data.password)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        user = User(
            first_name=data.first_name,
            display_name=data.display_name,
            phone=data.phone,
            email=data.email,
            hashed_password=hashed,
            city=data.city,
            district=data.district,
        )
        user = self.users.create(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, identifier: str, password: str) -> User:
        user = self.users.get_by_identifier(identifier)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Identifiants invalides.")
        if not user.is_active:
            raise UnauthorizedError("Ce compte est désactivé.")
        return user

    def issue_tokens(self, user: User) -> tuple[str, str]:
        access = create_access_token(str(user.id))
        refresh = create_refresh_token(str(user.id))
        return access, refresh

    def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        """Vérifie le refresh token et émet une nouvelle paire de tokens (rotation)."""
        try:
            user_id = decode_token(refresh_token, TokenType.REFRESH)
        except JWTError as exc:
            raise UnauthorizedError("Refresh token invalide ou expiré.") from exc

        user = self.users.get_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise UnauthorizedError("Utilisateur introuvable ou désactivé.")

        return self.issue_tokens(user)

    def get_current_user(self, access_token: str) -> User:
        try:
            user_id = decode_token(access_token, TokenType.ACCESS)
        except JWTError as exc:
            raise UnauthorizedError("Token invalide ou expiré.") from exc

        user = self.users.get_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise UnauthorizedError("Utilisateur introuvable ou désactivé.")
        return user

    def create_password_reset_token(self, identifier: str) -> str | None:
        """
        Retourne un reset token si l'utilisateur existe.
        Ne révèle jamais si l'identifiant existe ou non (le router renvoie
        toujours un succès générique, pour éviter l'énumération de comptes).
        """
        user = self.users.get_by_identifier(identifier)
        if not user:
            return None
        return create_password_reset_token(str(user.id))

    def reset_password(self, reset_token: str, new_password: str) -> None:
        try:
            user_id = decode_token(reset_token, TokenType.PASSWORD_RESET)
        except JWTError as exc:
            raise UnauthorizedError("Lien de réinitialisation invalide ou expiré.") from exc

        user = self.users.get_by_id(uuid.UUID(user_id))
        if not user:
            raise UnauthorizedError("Utilisateur introuvable.")

        user.hashed_password = hash_password(new_password)
        self.users.save(user)
        self.db.commit()
