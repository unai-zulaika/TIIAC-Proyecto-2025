from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
import math
import models, schemas, crud
from database import engine, get_db
import numpy as np
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recommendation Backend")

# permitir frontend en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # ajustar puertos de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "🚀 FastAPI Recommendation Backend running"}

@app.get("/articles/{article_id}", response_model=schemas.Article)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.article_id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Asegurarse de que product_code sea string
    if article.product_code is not None:
        article.product_code = str(article.product_code)
    return article

@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def get_customers(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Normalizar valores booleanos: convertir NaN a None
    if customer.FN is not None and isinstance(customer.FN, float) and math.isnan(customer.FN):
        customer.FN = None
    if customer.Active is not None and isinstance(customer.Active, float) and math.isnan(customer.Active):
        customer.Active = None
    return customer

# Esto no funciona todavia, es para cuando tengamos creados los embeddings en la base de datos
@app.get("/recommendations/{customer_id}")
def get_recommendations(customer_id: str, top_k: int = 4, db: Session = Depends(get_db)):
    """
    Devuelve las top_k prendas más similares al embedding del usuario.
    Intenta usar embedding en models.Customer; si no existe, lee customer_embeddings.
    Calcula similitud coseno en Python y devuelve los top_k artículos desde article_embeddings.
    """
    # 1) Obtener embedding del cliente: primero ORM, si no existe buscar en customer_embeddings
    customer = db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()
    cust_emb = None
    if customer and getattr(customer, "embedding", None):
        cust_emb = customer.embedding
    else:
        row = db.execute(text("SELECT embedding FROM customer_embeddings WHERE customer_id = :cid"), {"cid": customer_id}).fetchone()
        if row:
            cust_emb = row[0]

    if not cust_emb:
        raise HTTPException(status_code=404, detail="Customer not found or embedding missing")

    # Normalizar a numpy array
    try:
        cust_vec = np.asarray(cust_emb, dtype=float)
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid customer embedding format")

    cust_norm = np.linalg.norm(cust_vec)
    if cust_norm == 0:
        raise HTTPException(status_code=500, detail="Customer embedding has zero norm")

    # 2) Leer embeddings de artículos desde article_embeddings (fallback seguro)
    art_rows = db.execute(text("""
        SELECT a.article_id, a.prod_name, ae.embedding
        FROM articles a
        JOIN article_embeddings ae ON a.article_id = ae.article_id
    """)).fetchall()

    if not art_rows:
        raise HTTPException(status_code=404, detail="No article embeddings found")

    # 3) Calcular similitud coseno en Python y ordenar
    sims = []
    for r in art_rows:
        aid = r[0]
        name = r[1]
        emb = r[2]
        try:
            art_vec = np.asarray(emb, dtype=float)
        except Exception:
            continue
        art_norm = np.linalg.norm(art_vec)
        if art_norm == 0:
            continue
        cos_sim = float(np.dot(cust_vec, art_vec) / (cust_norm * art_norm))
        sims.append((cos_sim, aid, name))

    if not sims:
        raise HTTPException(status_code=404, detail="No valid article embeddings to compare")

    sims.sort(key=lambda x: x[0], reverse=True)
    top = sims[:top_k]

    result = []
    for sim, aid, name in top:
        result.append({
            "article_id": int(aid),
            "prod_name": name,
            "score": sim
        })

    return {"customer_id": customer_id, "recommendations": result}

@app.get("/customers/{customer_id}/transactions")
def get_customer_transactions(customer_id: str, db: Session = Depends(get_db)):
    """
    Recupera las transacciones/interacciones de un cliente.
    - Intenta usar el modelo ORM `models.Transaction` si existe.
    - Si no existe, hace una consulta SQL directa sobre la tabla `transactions`.
    Devuelve una lista de diccionarios con las filas encontradas (puede estar vacía).
    """
    TransactionModel = getattr(models, "Transaction", None)

    # 1) Intento ORM si hay modelo
    if TransactionModel is not None:
        try:
            rows = db.query(TransactionModel).filter(TransactionModel.customer_id == customer_id).all()
            result = []
            for r in rows:
                # convertir instancia ORM a dict sin _sa_instance_state
                row_dict = {}
                for col in r.__table__.columns:
                    row_dict[col.name] = getattr(r, col.name)
                result.append(row_dict)
            return {"customer_id": customer_id, "transactions": result}
        except Exception:
            # si falla el ORM, seguimos con fallback SQL
            try:
                db.rollback()
            except Exception:
                pass

    # 2) Fallback: consulta directa a la tabla transactions
    try:
        rows = db.execute(text("SELECT * FROM transactions WHERE customer_id = :cid ORDER BY 1"), {"cid": customer_id}).fetchall()
        result = []
        for r in rows:
            if hasattr(r, "_mapping"):
                result.append(dict(r._mapping))
            else:
                try:
                    result.append(dict(r))
                except Exception:
                    # convertir por posición a dict si no es mapeable
                    result.append({str(i): v for i, v in enumerate(r)})
        return {"customer_id": customer_id, "transactions": result}
    except Exception:
        # tabla no existe o error: devolver lista vacía para no romper clientes sin transacciones
        try:
            db.rollback()
        except Exception:
            pass
        return {"customer_id": customer_id, "transactions": []}