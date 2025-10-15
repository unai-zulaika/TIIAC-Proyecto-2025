from pydantic import BaseModel
from typing import Optional

# --- ARTÍCULOS ---
class ArticleBase(BaseModel):
    product_code: Optional[str]
    prod_name: Optional[str]
    product_type_no: Optional[int]
    product_type_name: Optional[str]
    product_group_name: Optional[str]

class Article(ArticleBase):
    article_id: int

    class Config:
        from_attributes = True  # ⚠️ Pydantic v2 usa from_attributes en lugar de orm_mode


# --- CUSTOMERS ---
class CustomerBase(BaseModel):
    FN: Optional[bool]
    Active: Optional[bool]
    club_member_status: Optional[str]
    fashion_news_frequency: Optional[str]
    age: Optional[int]
    postal_code: Optional[str]

class Customer(CustomerBase):
    customer_id: int

    class Config:
        from_attributes = True


# --- INTERACTIONS ---
class InteractionBase(BaseModel):
    customer_id: int
    article_id: int
    rating: Optional[float]

class Interaction(InteractionBase):
    id: int

    class Config:
        from_attributes = True
