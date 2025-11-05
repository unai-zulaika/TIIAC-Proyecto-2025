# api_search.py
from pathlib import Path
from typing import List, Optional, Dict, Any
import io
import numpy as np
import torch
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ---- Módulos de tu proyecto ----
from autoencoder import Encoder
import normalization

APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = APP_DIR / "encoder.pth"            # pesos del encoder entrenado
EMB_PATH   = APP_DIR / "image_embeddings.npz"   # embeddings + ids precomputados

# ---- Estado global cargado al importar el módulo ----
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_encoder_model: Optional[torch.nn.Module] = None
_emb_matrix: Optional[np.ndarray] = None
_emb_ids: Optional[List[str]] = None
_embedding_dim: Optional[int] = None

def _load_encoder(emb_dim: int = 256) -> torch.nn.Module:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No existe el modelo: {MODEL_PATH}")
    model = Encoder(emb_dim=emb_dim)
    state = torch.load(MODEL_PATH, map_location=device)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    model.load_state_dict(state, strict=False)
    model.to(device)
    model.eval()
    return model

def _load_index() -> (np.ndarray, List[str]):
    if not EMB_PATH.exists():
        raise FileNotFoundError(f"No existe el índice: {EMB_PATH}")
    npz = np.load(EMB_PATH, allow_pickle=True)
    embeddings = npz["embeddings"].astype(np.float32)  # [N, D]
    ids = list(npz["ids"])                              # [N]
    # normaliza para coseno
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms
    return embeddings, ids

def _ensure_loaded():
    global _encoder_model, _emb_matrix, _emb_ids, _embedding_dim
    if _encoder_model is None:
        _encoder_model = _load_encoder(emb_dim=256)
    if _emb_matrix is None or _emb_ids is None:
        _emb_matrix, _emb_ids = _load_index()
        _embedding_dim = int(_emb_matrix.shape[1])

def _preprocess_image_bytes(file_bytes: bytes) -> torch.Tensor:
    try:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except Exception as e:
        raise ValueError(f"Imagen inválida: {e}")

    # Usa el transform ya definido en normalization.py
    # OJO: ContrastiveTransform devuelve dos vistas; aquí usamos base_transform.
    transform = normalization.base_transform

    tensor = transform(img).unsqueeze(0)  # [1, C, H, W]
    return tensor.to(device)

def _embed_tensor(tensor: torch.Tensor) -> np.ndarray:
    if _encoder_model is None:
        raise RuntimeError("Encoder no cargado")
    with torch.no_grad():
        z = _encoder_model(tensor)  # [1, D]
    vec = z.detach().cpu().numpy().astype(np.float32)[0]
    # safety: normaliza
    n = np.linalg.norm(vec)
    if n > 0:
        vec = vec / n
    return vec

def _topk_cosine(query: np.ndarray, matrix: np.ndarray, ids: List[str], k: int = 5):
    scores = matrix @ query  # coseno si están normalizados
    k = max(1, int(k))
    if k >= scores.shape[0]:
        top_idx = np.argsort(-scores)
    else:
        top_idx = np.argpartition(-scores, k)[:k]
        top_idx = top_idx[np.argsort(-scores[top_idx])]
    return [{"id": str(ids[i]), "score": float(scores[i])} for i in top_idx]

# ---------- FUNCIÓN PÚBLICA (llamable desde cualquier parte del backend) ----------
def search_topk_from_bytes(image_bytes: bytes, k: int = 5) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo: carga modelos/índice si hace falta, 
    preprocesa imagen, embebe y retorna top-k vecinos más cercanos.
    Devuelve: {"query_embedding_dim": D, "topk": [{"id": "...", "score": 0.xx}, ...]}
    """
    _ensure_loaded()
    tensor = _preprocess_image_bytes(image_bytes)
    q = _embed_tensor(tensor)
    res = _topk_cosine(q, _emb_matrix, _emb_ids, k=k)  # type: ignore
    return {"query_embedding_dim": int(q.shape[0]), "topk": res}

# ---------- API ASGI (opcional para consumo HTTP) ----------
app = FastAPI(title="Image Embedding Search API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajusta si necesitas restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup_event():
    _ensure_loaded()

@app.get("/health")
def health():
    size = None if _emb_matrix is None else int(_emb_matrix.shape[0])
    return {"status": "ok", "model_loaded": _encoder_model is not None, "index_size": size}

@app.post("/search")
async def search(file: UploadFile = File(...), k: int = 5):
    content = await file.read()
    try:
        out = search_topk_from_bytes(content, k=k)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse(content=out)

@app.post("/reload")
def reload_index():
    global _emb_matrix, _emb_ids, _embedding_dim
    _emb_matrix, _emb_ids = _load_index()
    _embedding_dim = int(_emb_matrix.shape[1])
    return {"status": "reloaded", "index_size": int(_emb_matrix.shape[0])}
