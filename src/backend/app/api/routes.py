from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.product_repo import ProductRepository, get_product_repo
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate, ProductOut
from app.services.image_service import ImageService, get_image_service

router = APIRouter()

@router.get("/health", tags=["health"]) 
def health():
    return {"status": "ok"}

@router.get("/products", response_model=list[ProductRead], tags=["products"]) 
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ProductRepository(db).list(skip=skip, limit=limit)

@router.post("/products", response_model=ProductRead, status_code=201, tags=["products"]) 
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return ProductRepository(db).create(product)

@router.get("/products/{product_id}", response_model=ProductRead, tags=["products"]) 
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = ProductRepository(db).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/products/{product_id}", response_model=ProductRead, tags=["products"]) 
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    updated = ProductRepository(db).update(product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/products/{product_id}", status_code=204, tags=["products"]) 
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = ProductRepository(db).delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return None

@router.get("/get_product_data", response_model=ProductOut)
async def get_product_data(
    id: int = Query(..., alias="id", ge=1),
    repo: ProductRepository = Depends(get_product_repo),
):
    product = await repo.get_by_id(id)
    if not product:
        raise HTTPException(status_code=404, detail="product_not_found")
    return product

@router.get("/get_product_image")
async def get_product_image(
    id: int = Query(..., alias="id", ge=1),
    repo: ProductRepository = Depends(get_product_repo),
    img: ImageService = Depends(get_image_service),
):
    product = await repo.get_by_id(id)
    if not product:
        raise HTTPException(status_code=404, detail="product_not_found")

    if not product.image_s3_key:
        raise HTTPException(status_code=404, detail="image_not_found")

    url = img.get_presigned_url(product.image_s3_key)
    return JSONResponse({"product_id": id, "image_url": url})
