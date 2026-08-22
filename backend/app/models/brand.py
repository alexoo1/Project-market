from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin, UUIDMixin


class Brand(Base, UUIDMixin, TimestampMixin):
    """Marque d'un article (Nike, Zara, 'Fait main', etc.)."""
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Brand id={self.id} name={self.name!r}>"
