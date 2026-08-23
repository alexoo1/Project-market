from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import ChangePasswordRequest, UserUpdateRequest


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def update_profile(self, user: User, payload: UserUpdateRequest) -> User:
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(user, field, value)
        self.users.save(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user: User, payload: ChangePasswordRequest) -> None:
        if not verify_password(payload.current_password, user.hashed_password):
            raise UnauthorizedError("Mot de passe actuel incorrect.")
        try:
            user.hashed_password = hash_password(payload.new_password)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        self.users.save(user)
        self.db.commit()
