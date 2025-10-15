from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.db import get_session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, skip: int = 0, limit: int = 100):
        stmt = select(Product).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_by_id(self, item_id: int) -> ProductOut | None:
        stmt = select(Product).where(Product.item_id == item_id)
        res = await self.session.execute(stmt)
        obj = res.scalar_one_or_none()
        if not obj:
            return None
        return ProductOut.model_validate(obj)

    async def create(self, product_in: ProductCreate):
        product = Product(
            name=product_in.name,
            description=product_in.description,
            price=product_in.price,
            image_url=str(product_in.image_url) if product_in.image_url else None,
        )
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product_id: int, product_in: ProductUpdate):
        product = await self.get_by_id(product_id)
        if not product:
            return None
        for field, value in product_in.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete(self, product_id: int) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            return False
        await self.session.delete(product)
        await self.session.commit()
        return True


def get_product_repo(session: AsyncSession = Depends(get_session)) -> ProductRepository:
    return ProductRepository(session)
