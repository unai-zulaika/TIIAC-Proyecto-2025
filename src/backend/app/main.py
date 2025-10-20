from fastapi import FastAPI
from app.api.routes import router
from app.middleware.cors import add_cors
from app.core.db import engine
from app.models import Base

app = FastAPI(title="Fashion Backend", version="1.0.0")
add_cors(app)
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Crear tablas automáticamente si no existen (útil en dev/POC)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Trigger reload
# noop comment
