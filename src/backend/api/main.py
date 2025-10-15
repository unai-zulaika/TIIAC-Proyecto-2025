from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
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
