from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import UserCreate, LoginRequest
from app.core.security import verify_password, hash_password, create_access_token
from app.core.exceptions import BadRequestException, UnauthorizedException


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserCreate) -> User:
        # Check existing
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if result.scalar_one_or_none():
            raise BadRequestException("Email already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            name=data.name,
            role=data.role,
            merchant_id=data.merchant_id,
            outlet_id=data.outlet_id,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def login(self, data: LoginRequest) -> dict:
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()

        token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "role": user.role,
                "merchant_id": user.merchant_id,
                "outlet_id": user.outlet_id,
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_merchant_admin(self, merchant_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(
                User.merchant_id == merchant_id,
                User.role == "merchant_admin",
            )
        )
        return result.scalar_one_or_none()

    async def update_admin_name(self, merchant_id: str, name: str) -> User:
        from app.core.exceptions import NotFoundException
        user = await self.get_merchant_admin(merchant_id)
        if not user:
            raise NotFoundException("Merchant admin account")
        user.name = name
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def reset_admin_password(
        self, merchant_id: str, new_password: str
    ) -> User:
        from app.core.exceptions import NotFoundException, BadRequestException
        if len(new_password) < 8:
            raise BadRequestException("Password must be at least 8 characters")
        user = await self.get_merchant_admin(merchant_id)
        if not user:
            raise NotFoundException("Merchant admin account")
        user.hashed_password = hash_password(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user
