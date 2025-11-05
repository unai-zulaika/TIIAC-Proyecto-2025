# app/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import io
import numpy as np
import torch
from PIL import Image

# ---- Tu stack existente ----
from app.api.routes import router
from app.middleware.cors import add_cors
from app.core.db import engine
from app.models import Base

# ---- Importar desde app/entrenamiento ----
from app.entrenamiento.autoencoder import Encoder
from app.entrenamiento import normalization

# =======================
#   Rutas y constantes
# =======================
APP_DIR = Path(__file__).resolve().parent            # .../app
ENTRENAMIENTO_DIR = APP_DIR / "entrenamiento"        # .../app/entrenamiento

# Datos existentes
CSV_PATH = Path("data/csv/articles.csv")             # columna: article_id
IMAGES_DIR = Path("data/img")                        # {id}.jpg / {id}.png

# Visual search (dentro de app/entrenamiento)
MODEL_PATH = ENTRENAMIENTO_DIR / "encoder.pth"
EMB_PATH   = ENTRENAMIENTO_DIR / "image_embeddings.npz"
EMB_DIM    = 256
IMAGE_SIZE = 224

# =======================
#   App & CORS
# =======================
app = FastAPI(title="Fashion Backend", version="1.0.0")
add_cors(app)
app.include_router(router)

# Servir imágenes estáticas (p.ej. http://host:port/images/123.jpg)
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# =======================
#   Artículos (CSV)
# =======================
ARTICLES_INDEX: dict[str, dict] = {}

class ArticleOut(BaseModel):
    id: str
    image_url: str
    data: dict

@app.on_event("startup")
async def on_startup():
    # Crear tablas (si aplica)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Cargar CSV
    if not CSV_PATH.exists():
        print(f"[WARN] CSV no encontrado: {CSV_PATH.resolve()}")
    else:
        try:
            df = pd.read_csv(CSV_PATH, dtype=str).fillna("")
            if "article_id" not in df.columns:
                print("[WARN] El CSV no contiene la columna 'article_id'")
            else:
                df["article_id"] = df["article_id"].astype(str).str.strip()
                global ARTICLES_INDEX
                ARTICLES_INDEX = {
                    row["article_id"]: row.to_dict()
                    for _, row in df.iterrows()
                }
                print(f"[INFO] Cargados {len(ARTICLES_INDEX)} artículos del CSV.")
        except Exception as e:
            print(f"[ERROR] Cargando CSV: {e}")

    # Intentar precargar índice visual (opcional)
    try:
        _ensure_loaded()
        print(f"[INFO] Visual index cargado: "
              f"{_emb_matrix.shape if _emb_matrix is not None else None}")
    except Exception as e:
        print(f"[WARN] Visual search no disponible aún: {e}")

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

# =======================
#   Visual Search
# =======================
_encoder_model: torch.nn.Module | None = None
_emb_matrix: np.ndarray | None = None
_emb_ids: list[str] | None = None
_embedding_dim: int | None = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def _load_encoder(emb_dim: int = EMB_DIM) -> torch.nn.Module:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modelo no encontrado: {MODEL_PATH}")
    model = Encoder(emb_dim=emb_dim)
    state = torch.load(MODEL_PATH, map_location=_device)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    model.load_state_dict(state, strict=False)
    model.to(_device)
    model.eval()
    return model

def _load_index() -> tuple[np.ndarray, list[str]]:
    if not EMB_PATH.exists():
        raise FileNotFoundError(f"Embeddings NPZ no encontrado: {EMB_PATH}")
    npz = np.load(EMB_PATH, allow_pickle=True)
    embs = npz["embeddings"].astype(np.float32)   # [N, D]
    ids = list(npz["ids"])                         # [N]
    # Normalizar para coseno
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embs = embs / norms
    return embs, ids

def _ensure_loaded():
    global _encoder_model, _emb_matrix, _emb_ids, _embedding_dim
    if _encoder_model is None:
        _encoder_model = _load_encoder(EMB_DIM)
    if _emb_matrix is None or _emb_ids is None:
        _emb_matrix, _emb_ids = _load_index()
        _embedding_dim = int(_emb_matrix.shape[1])

def _preprocess_image_bytes(file_bytes: bytes) -> torch.Tensor:
    try:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except Exception as e:
        raise ValueError(f"Imagen inválida: {e}")
    # Usa tu transform de inferencia ya definido en normalization.py
    transform = normalization.base_transform
    tensor = transform(img).unsqueeze(0)  # [1, C, H, W]
    return tensor.to(_device)

def _embed_tensor(tensor: torch.Tensor) -> np.ndarray:
    if _encoder_model is None:
        raise RuntimeError("Encoder no cargado")
    with torch.no_grad():
        z = _encoder_model(tensor)  # [1, D]
    vec = z.detach().cpu().numpy().astype(np.float32)[0]
    # Normalize safety
    n = np.linalg.norm(vec)
    if n > 0:
        vec = vec / n
    return vec

def _topk_cosine(query: np.ndarray, matrix: np.ndarray, ids: list[str], k: int = 5):
    scores = matrix @ query  # coseno si ambos normalizados
    k = max(1, int(k))
    if k >= scores.shape[0]:
        top_idx = np.argsort(-scores)
    else:
        top_idx = np.argpartition(-scores, k)[:k]
        top_idx = top_idx[np.argsort(-scores[top_idx])]
    return [{"id": str(ids[i]), "score": float(scores[i])} for i in top_idx]

def search_topk_from_bytes(image_bytes: bytes, k: int = 5) -> dict:
    _ensure_loaded()
    tensor = _preprocess_image_bytes(image_bytes)
    q = _embed_tensor(tensor)
    res = _topk_cosine(q, _emb_matrix, _emb_ids, k=k)  # type: ignore
    return {"query_embedding_dim": int(q.shape[0]), "topk": res}

class VisualSearchOut(BaseModel):
    query_embedding_dim: int
    topk: list[dict]

@app.post("/visual/search", response_model=VisualSearchOut)
async def visual_search(file: UploadFile = File(...), k: int = 5):
    """
    Recibe una imagen, calcula el embedding y devuelve los k más cercanos del índice.
    """
    content = await file.read()
    try:
        # Realiza la búsqueda de las imágenes más cercanas
        out = search_topk_from_bytes(content, k=k)
        
        # Obtener los detalles completos de cada artículo recomendado
        topk_details = []
        for result in out["topk"]:
            # LIMPIAR LA EXTENSIÓN DEL ID
            article_id = result["id"]
            # Remover .jpg o .png si existe
            cleaned_id = article_id.replace(".jpg", "").replace(".png", "")
            
            # Buscar en el índice con el ID limpio
            article_data = ARTICLES_INDEX.get(cleaned_id, {})
            
            # Obtener la URL de la imagen usando el ID limpio
            image_url = ""
            jpg = IMAGES_DIR / f"{cleaned_id}.jpg"
            png = IMAGES_DIR / f"{cleaned_id}.png"
            if jpg.exists():
                image_url = f"/images/{cleaned_id}.jpg"
            elif png.exists():
                image_url = f"/images/{cleaned_id}.png"
            
            # Añadir los detalles del artículo a la respuesta
            topk_details.append({
                "id": cleaned_id,  # Devolver el ID limpio
                "image_url": image_url,
                "data": article_data,
                "score": result["score"]
            })
        
        return JSONResponse(content={"query_embedding_dim": out["query_embedding_dim"], "topk": topk_details})

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/visual/reload")
async def visual_reload():
    """Recarga el NPZ de embeddings sin reiniciar el contenedor."""
    global _emb_matrix, _emb_ids, _embedding_dim
    _emb_matrix, _emb_ids = _load_index()
    _embedding_dim = int(_emb_matrix.shape[1])
    return {"status": "reloaded", "index_size": int(_emb_matrix.shape[0])}

@app.get("/health")
async def health():
    size = None if _emb_matrix is None else int(_emb_matrix.shape[0])
    return {"status": "ok", "visual_index_size": size}
