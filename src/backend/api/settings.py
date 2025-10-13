import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://usuario:contraseña@localhost:5432/HM"
)
PRODUCT_IMAGES_DIR = os.getenv("PRODUCT_IMAGES_DIR", "/images")
