import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ListingCondition, ListingStatus
from app.schemas.user import UserPublic


class ListingImageInput(BaseModel):
    url: str
    position: int = 0


class ListingImagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    url: str
    position: int


class ListingCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10, max_length=3000)
    category_id: uuid.UUID
    brand_id: uuid.UUID | None = None
    size: str | None = Field(default=None, max_length=30)
    color: str | None = Field(default=None, max_length=50)
    condition: ListingCondition
    price: int = Field(gt=0, le=50_000_000, description="Prix en FCFA")
    city: str = Field(min_length=2, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    images: list[ListingImageInput] = Field(min_length=1, max_length=8)

    @field_validator("images")
    @classmethod
    def normalize_positions(cls, v: list[ListingImageInput]) -> list[ListingImageInput]:
        for idx, img in enumerate(v):
            img.position = idx
        return v


class ListingUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, min_length=10, max_length=3000)
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    size: str | None = None
    color: str | None = None
    condition: ListingCondition | None = None
    price: int | None = Field(default=None, gt=0, le=50_000_000)
    city: str | None = None
    district: str | None = None
    status: ListingStatus | None = None


class ListingCardPublic(BaseModel):
    """Représentation compacte pour le feed / la recherche (grille de cartes)."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    price: int
    condition: ListingCondition
    city: str
    status: ListingStatus
    cover_image_url: str | None
    created_at: datetime


class ListingDetailPublic(BaseModel):
    """Représentation complète pour la fiche produit."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    price: int
    size: str | None
    color: str | None
    condition: ListingCondition
    city: str
    district: str | None
    status: ListingStatus
    view_count: int
    favorite_count: int
    created_at: datetime
    images: list[ListingImagePublic]
    seller: UserPublic


class ListingSearchParams(BaseModel):
    q: str | None = None
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    size: str | None = None
    condition: ListingCondition | None = None
    color: str | None = None
    city: str | None = None
    price_min: int | None = Field(default=None, ge=0)
    price_max: int | None = Field(default=None, ge=0)
    sort: str = Field(default="recent", pattern="^(recent|price_asc|price_desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)


class PaginatedListings(BaseModel):
    items: list[ListingCardPublic]
    page: int
    page_size: int
    total: int
    has_next: bool
