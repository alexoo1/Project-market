"""
LocalStorageProvider: écrit les fichiers sur le disque du serveur, sous
STORAGE_LOCAL_PATH, servis ensuite via /media (voir app/main.py).
"""
from pathlib import Path

from app.core.config import settings
from app.services.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    def save(self, content: bytes, filename: str) -> str:
        directory = Path(settings.STORAGE_LOCAL_PATH)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / filename).write_bytes(content)
        return f"{settings.STORAGE_PUBLIC_BASE_URL.rstrip('/')}/{filename}"


def get_storage_provider() -> StorageProvider:
    """
    Point d'extension unique: le jour où S3/R2 est disponible, changer
    cette fonction pour retourner le vrai provider, sans toucher au
    reste du code.
    """
    return LocalStorageProvider()
