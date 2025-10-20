from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # =========================
    # Base de datos (PostgreSQL / SQLite dev)
    # =========================
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "productos_db"
    POSTGRES_USER: str = "etl_user"
    POSTGRES_PASSWORD: str = "etl_password"

    # Permitir override directo (útil para sqlite en dev)
    DB_URL: Optional[str] = None

    # =========================
    # AWS S3 (opcional, si NO usas MinIO)
    # =========================
    S3_REGION: str = "eu-west-1"
    S3_BUCKET: str = "fashionai-images"
    AWS_ACCESS_KEY_ID: str = ""     # si usas IAM role, déjalo vacío
    AWS_SECRET_ACCESS_KEY: str = ""

    # =========================
    # MinIO (S3 local)
    # =========================
    MINIO_ENDPOINT: str = "http://minio:9000"     # p.ej. docker service → http://minio:9000 | local → http://localhost:9000
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin123"
    MINIO_BUCKET_NAME: str = "productos"

    # =========================
    # App
    # =========================
    API_PORT: int = 8080
    ENV: str = Field(default="dev")               # dev → SQLite por defecto; prod → PostgreSQL
    CORS_ALLOW_ORIGINS: str = "*"                 # coma-separado en .env si quieres restringir

    # =========================
    # Helpers
    # =========================
    @property
    def USE_MINIO(self) -> bool:
        """
        True si se ha configurado un endpoint de MinIO (S3-compatible local).
        Si quieres forzar AWS S3, deja MINIO_ENDPOINT vacío en tu .env.
        """
        return bool(self.MINIO_ENDPOINT)

    @property
    def DATABASE_URL(self) -> str:
        """
        Prioriza DB_URL (override manual), luego:
        - ENV=dev -> SQLite (archivo dev.db)
        - ENV!=dev -> PostgreSQL (asyncpg)
        """
        if self.DB_URL:
            return self.DB_URL

        if self.ENV.lower() == "dev":
            return "sqlite+aiosqlite:///./dev.db"

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Configuración Pydantic v2
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
