from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
import math
import models, schemas, crud
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recommendation Backend")

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
def get_recommendations(customer_id: str, top_k: int = 5, db: Session = Depends(get_db)):
    """
    Devuelve las top_k prendas más similares al embedding del usuario usando pgvector.
    """
    # Obtener el embedding del cliente
    customer = db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()
    if not customer or not customer.embedding:
        raise HTTPException(status_code=404, detail="Customer not found or embedding missing")
    
    # Consulta de artículos ordenados por similitud coseno usando pgvector
    query = db.query(
        models.Article.article_id,
        models.Article.prod_name,
        models.Article.embedding
    ).order_by(func.cosine_distance(models.Article.embedding, customer.embedding)).limit(top_k)
    
    recommendations = query.all()
    
    # Formatear respuesta
    result = []
    for r in recommendations:
        result.append({
            "article_id": r.article_id,
            "prod_name": r.prod_name
        })
    
    if not result:
        raise HTTPException(status_code=404, detail="No recommendations found")
    
    return {"customer_id": customer_id, "recommendations": result}