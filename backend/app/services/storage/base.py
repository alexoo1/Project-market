"""
Interface abstraite de stockage de fichiers.

Toute intégration réelle (S3, Cloudflare R2) devra implémenter cette
interface. Tant que ces accès ne sont pas disponibles, seul
LocalStorageProvider existe (fichiers écrits sur le disque du serveur).
"""
from abc import ABC, abstractmethod


class StorageProvider(ABC):
    @abstractmethod
    def save(self, content: bytes, filename: str) -> str:
        """Écrit le fichier et retourne son URL publique."""
        raise NotImplementedError
