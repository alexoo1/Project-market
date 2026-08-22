"""
Logique métier des téléversements d'images (photos d'annonces).
Ne connaît rien de FastAPI: reçoit des octets bruts, retourne des URLs.
"""
import uuid

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.services.storage.base import StorageProvider

_EXTENSION_BY_CONTENT_TYPE = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


class UploadService:
    def __init__(self, storage: StorageProvider):
        self.storage = storage

    def save_image(self, content: bytes, content_type: str | None) -> str:
        if content_type not in settings.UPLOAD_ALLOWED_CONTENT_TYPES:
            raise ValidationError(
                f"Type de fichier non autorisé: {content_type}. "
                f"Formats acceptés: {', '.join(settings.UPLOAD_ALLOWED_CONTENT_TYPES)}."
            )
        max_bytes = settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise ValidationError(f"Image trop volumineuse (max {settings.UPLOAD_MAX_SIZE_MB} Mo).")

        extension = _EXTENSION_BY_CONTENT_TYPE[content_type]
        filename = f"{uuid.uuid4().hex}.{extension}"
        return self.storage.save(content, filename)
