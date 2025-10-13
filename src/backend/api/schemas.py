from pydantic import BaseModel

class ProductOut(BaseModel):
    id: int
    title: str
    brand: str | None = None
    category: str | None = None
    price: float | None = None
    description: str | None = None
    image_url: str | None = None

    class Config:
        from_attributes = True
