from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings


def add_cors(app):
    settings = get_settings()
    origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
