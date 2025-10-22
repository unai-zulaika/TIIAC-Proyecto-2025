# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.middleware.cors import add_cors
from app.core.db import engine
from app.models import Base

from pathlib import Path
from pydantic import BaseModel
import pandas as pd

# --- Config (si quieres, muévelo a settings) ---
CSV_PATH = Path("data/csv/articles.csv")   # columna clave: article_id
IMAGES_DIR = Path("data/img")              # imágenes: {id}.jpg / {id}.png

app = FastAPI(title="Fashion Backend", version="1.0.0")

# CORS
add_cors(app)

# Rutas del proyecto existente
app.include_router(router)

# Servir imágenes estáticas (p.ej. http://localhost:8000/images/123.jpg)
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# ---- Cache en memoria de artículos (CSV) ----
ARTICLES_INDEX: dict[str, dict] = {}

class ArticleOut(BaseModel):
    id: str
    image_url: str
    data: dict

@app.get("/health")
async def health():
    return {"status": "ok"}

# Crear tablas y precargar CSV al arrancar (útil dev/POC)
@app.on_event("startup")
async def on_startup():
    # DB (si aplica)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # CSV -> dict indexado por article_id
    if not CSV_PATH.exists():
        print(f"[WARN] CSV no encontrado: {CSV_PATH.resolve()}")
        return

    try:
        df = pd.read_csv(CSV_PATH, dtype=str).fillna("")
        if "article_id" not in df.columns:
            print("[WARN] El CSV no contiene la columna 'article_id'")
            return

        # normalizar id
        df["article_id"] = df["article_id"].astype(str).str.strip()

        global ARTICLES_INDEX
        ARTICLES_INDEX = {
            row["article_id"]: row.to_dict()
            for _, row in df.iterrows()
        }
        print(f"[INFO] Cargados {len(ARTICLES_INDEX)} artículos del CSV.")
    except Exception as e:
        print(f"[ERROR] Cargando CSV: {e}")

@app.get("/articles/{item_id}", response_model=ArticleOut)
async def get_article(item_id: str):
    item_id = str(item_id).strip()
    data = ARTICLES_INDEX.get(item_id)
    if not data:
        raise HTTPException(status_code=404, detail="ID no encontrado en CSV")

    # Construir URL pública de la imagen servida por StaticFiles
    image_url = ""
    jpg = IMAGES_DIR / f"{item_id}.jpg"
    png = IMAGES_DIR / f"{item_id}.png"
    if jpg.exists():
        image_url = f"/images/{item_id}.jpg"
    elif png.exists():
        image_url = f"/images/{item_id}.png"

    return ArticleOut(id=item_id, image_url=image_url, data=data)
