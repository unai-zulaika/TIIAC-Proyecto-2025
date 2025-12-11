import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://usuario:contraseña@localhost:5432/HM")

# PRODUCT_IMAGES_DIR = os.getenv("PRODUCT_IMAGES_DIR", "/images")