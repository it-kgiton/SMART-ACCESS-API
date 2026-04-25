from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.exceptions import NotFoundException


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ProductCreate) -> Product:
        product = Product(
            merchant_id=data.merchant_id,
            name=data.name,
            description=data.description,
            price=data.price,
            category=data.category or "lainnya",
            image_url=data.image_url,
            is_available=data.is_available,
            stock_quantity=data.stock_quantity,
        )
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, merchant_id: Optional[str] = None, category: Optional[str] = None,
        available_only: bool = False, search: Optional[str] = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(Product)
        count_query = select(func.count(Product.id))

        if merchant_id:
            query = query.where(Product.merchant_id == merchant_id)
            count_query = count_query.where(Product.merchant_id == merchant_id)
        if category:
            query = query.where(Product.category == category)
            count_query = count_query.where(Product.category == category)
        if available_only:
            query = query.where(Product.is_available.is_(True))
            count_query = count_query.where(Product.is_available.is_(True))
        if search:
            pattern = f"%{search}%"
            query = query.where(Product.name.ilike(pattern))
            count_query = count_query.where(Product.name.ilike(pattern))

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(Product.created_at.desc())
        )
        return result.scalars().all(), total

    async def update(self, product_id: str, data: ProductUpdate) -> Product:
        product = await self.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product")
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product_id: str) -> bool:
        product = await self.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product")
        await self.db.delete(product)
        await self.db.commit()
        return True
