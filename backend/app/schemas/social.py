import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import NotificationType


class CreateReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)


class ReviewPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    order_id: uuid.UUID
    reviewer_id: uuid.UUID
    reviewee_id: uuid.UUID
    rating: int
    comment: str | None
    created_at: datetime


class FollowStatus(BaseModel):
    following: bool
    followers_count: int


class UserFollowSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    display_name: str
    profile_photo_url: str | None
    city: str | None


class CreateBoostRequest(BaseModel):
    duration_hours: int


class BoostPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    listing_id: uuid.UUID
    duration_hours: int
    starts_at: datetime
    ends_at: datetime


class NotificationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    type: NotificationType
    title: str
    body: str | None
    related_entity_id: uuid.UUID | None
    is_read: bool
    created_at: datetime
