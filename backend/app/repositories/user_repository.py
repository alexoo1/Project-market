import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Accès aux données pour User. Ne contient aucune règle métier :
    uniquement des requêtes. La logique (validation, hashing, etc.)
    vit dans app/services.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_phone(self, phone: str) -> User | None:
        return self.db.scalar(select(User).where(User.phone == phone))

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_identifier(self, identifier: str) -> User | None:
        """Recherche par téléphone OU email (login flexible)."""
        return self.db.scalar(
            select(User).where(or_(User.phone == identifier, User.email == identifier))
        )

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user
