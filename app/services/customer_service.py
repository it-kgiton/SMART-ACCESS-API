from typing import Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, CustomerStatus
from app.models.wallet import Wallet, WalletStatus
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: CustomerCreate) -> Customer:
        customer = Customer(
            name=data.name,
            merchant_id=data.merchant_id,
            email=data.email,
            phone=data.phone,
            identity_number=data.identity_number,
        )
        self.db.add(customer)
        await self.db.flush()

        # Create wallet
        wallet = Wallet(
            customer_id=customer.id,
            balance=Decimal(str(data.initial_balance)),
        )
        self.db.add(wallet)

        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        merchant_id: Optional[str] = None,
    ) -> tuple[list[Customer], int]:
        query = select(Customer)
        count_query = select(func.count()).select_from(Customer)

        if merchant_id:
            query = query.where(Customer.merchant_id == merchant_id)
            count_query = count_query.where(Customer.merchant_id == merchant_id)

        if search:
            query = query.where(
                Customer.name.ilike(f"%{search}%")
                | Customer.email.ilike(f"%{search}%")
            )
            count_query = count_query.where(
                Customer.name.ilike(f"%{search}%")
                | Customer.email.ilike(f"%{search}%")
            )

        if status:
            query = query.where(Customer.status == status)
            count_query = count_query.where(Customer.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Customer.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(self, customer_id: str, data: CustomerUpdate) -> Optional[Customer]:
        customer = await self.get_by_id(customer_id)
        if not customer:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)

        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def delete(self, customer_id: str) -> bool:
        customer = await self.get_by_id(customer_id)
        if not customer:
            return False
        customer.status = CustomerStatus.INACTIVE
        await self.db.commit()
        return True
