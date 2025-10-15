from typing import Optional, Union

from pydantic import BaseModel, Field, HttpUrl


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    image_url: Optional[HttpUrl] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[HttpUrl] = None


class ProductRead(ProductBase):
    id: int

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    item_id: int
    product_code: Union[str, None] = None
    category: Union[str, None] = None
    brand: Union[str, None] = None
    color: Union[str, None] = None
    season: Union[str, None] = None
    image_s3_key: Union[str, None] = None

    class Config:
        from_attributes = True
