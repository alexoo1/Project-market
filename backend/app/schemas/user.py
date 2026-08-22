import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserPublic(BaseModel):
    """Représentation publique d'un utilisateur (visible par les autres)."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    profile_photo_url: str | None
    city: str | None
    bio: str | None
    average_rating: float
    review_count: int
    created_at: datetime


class UserMe(UserPublic):
    """Représentation complète, réservée au propriétaire du compte."""
    first_name: str
    phone: str
    email: str | None
    district: str | None
    is_verified: bool
    updated_at: datetime
