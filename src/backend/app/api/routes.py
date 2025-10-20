from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import JSONResponse

from app.repositories.product_repo import ProductRepository, get_product_repo
from app.schemas.product import ProductOut
from app.services.image_service import ImageService, get_image_service

router = APIRouter()


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
