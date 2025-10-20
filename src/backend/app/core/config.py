from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Postgres
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fashion"
    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "app"

    # Permitir override directo (útil para sqlite en dev)
    DB_URL: Optional[str] = None

    # AWS S3
    S3_REGION: str = "eu-west-1"
    S3_BUCKET: str = "fashionai-images"
    AWS_ACCESS_KEY_ID: str = ""   # si usas IAM role, déjalo vacío
    AWS_SECRET_ACCESS_KEY: str = ""

    # App
    API_PORT: int = 8080
    ENV: str = Field(default="dev")
    CORS_ALLOW_ORIGINS: str = "*"  # coma-separado en .env si quieres restringir

    @property
    def DATABASE_URL(self) -> str:
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
