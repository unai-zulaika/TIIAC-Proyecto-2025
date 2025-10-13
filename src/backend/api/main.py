from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from db import Base, engine, get_session
from models import Product
from schemas import ProductOut
from settings import PRODUCT_IMAGES_DIR
import os

app = FastAPI(title="Clothing Recommender API", version="0.1.0")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/get_product_data", response_model=ProductOut)
async def get_product_data(
    id: Annotated[int, Query(description="Product ID (p_id del dataset)")],
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Product).where(Product.id == id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {id} not found")
    return ProductOut.model_validate(product)

@app.get("/get_product_image")
async def get_product_image(
    id: Annotated[int, Query(description="Product ID (p_id del dataset)")],
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Product).where(Product.id == id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {id} not found")

    if product.image_url:
        return RedirectResponse(
            url=product.image_url,
            headers={"Cache-Control": "public, max-age=86400"}
        )

    if product.image_path:
        path = product.image_path
        if not os.path.isabs(path):
            path = os.path.join(PRODUCT_IMAGES_DIR, path)
        if os.path.exists(path):
            return FileResponse(path, media_type="image/jpeg",
                                headers={"Cache-Control": "public, max-age=86400"})

    return JSONResponse(status_code=404, content={"detail": f"No image for product {id}"})
