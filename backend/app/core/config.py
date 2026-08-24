"""
Configuration centralisée de Vendi Market.

Toute valeur "métier" (frais de plateforme, expiration des tokens, etc.)
doit être définie ICI et nulle part ailleurs dans le code, conformément
à la règle "pas de configuration éparpillée dans plusieurs fichiers".
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Application ---
    PROJECT_NAME: str = "Vendi Market"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True

    # --- Base de données ---
    DATABASE_URL: str = "postgresql+psycopg2://project_market:project_market@db:5432/project_market"

    # --- Sécurité / JWT ---
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # --- OTP SMS (prévu pour plus tard, non actif dans le MVP) ---
    OTP_ENABLED: bool = False
    OTP_CODE_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["*"]

    # --- Stockage d'images (abstraction, voir app/services/storage) ---
    STORAGE_PROVIDER: str = "local"  # local | s3 | r2
    STORAGE_LOCAL_PATH: str = "/app/media"
    STORAGE_PUBLIC_BASE_URL: str = "http://localhost:8000/media"
    S3_BUCKET_NAME: str | None = None
    S3_REGION: str | None = None
    S3_ACCESS_KEY_ID: str | None = None
    S3_SECRET_ACCESS_KEY: str | None = None
    S3_ENDPOINT_URL: str | None = None  # utile pour Cloudflare R2
    UPLOAD_MAX_SIZE_MB: int = 5
    UPLOAD_ALLOWED_CONTENT_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # --- Monétisation (configurable, jamais en dur dans le code métier) ---
    # Payés uniquement par l'acheteur, aucun minimum/frais fixe, le vendeur
    # reçoit toujours 100% du prix qu'il a fixé (cf. app/core/pricing.py).
    BUYER_PROTECTION_FEE_PERCENT: float = 5.0  # en pourcentage du prix article

    # --- Boosts ---
    BOOST_DURATIONS_HOURS: list[int] = [24, 72, 168]  # 24h, 3j, 7j

    # --- Devise ---
    CURRENCY_CODE: str = "XOF"
    CURRENCY_LABEL: str = "FCFA"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
