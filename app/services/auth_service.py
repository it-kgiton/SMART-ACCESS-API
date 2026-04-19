from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, LoginRequest
from app.core.security import verify_password, hash_password, create_access_token
from app.core.exceptions import BadRequestException, UnauthorizedException, NotFoundException


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserCreate) -> User:
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        if result.scalar_one_or_none():
            raise BadRequestException("Email already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            role=data.role,
            region_id=data.region_id,
            school_id=data.school_id,
            merchant_id=data.merchant_id,
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
                "region_id": user.region_id,
                "school_id": user.school_id,
                "merchant_id": user.merchant_id,
            }
        )

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "region_id": user.region_id,
                "school_id": user.school_id,
                "merchant_id": user.merchant_id,
            },
            "access_token": token,
            "refresh_token": token,
            "expires_in": 3600,
        }

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_users(
        self, role: Optional[str] = None, school_id: Optional[str] = None,
        region_id: Optional[str] = None, skip: int = 0, limit: int = 50,
        exclude_roles: Optional[List[str]] = None,
    ) -> tuple:
        query = select(User).where(User.is_active == True)
        count_query = select(func.count(User.id)).where(User.is_active == True)

        if exclude_roles:
            query = query.where(~User.role.in_(exclude_roles))
            count_query = count_query.where(~User.role.in_(exclude_roles))
        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        if school_id:
            query = query.where(User.school_id == school_id)
            count_query = count_query.where(User.school_id == school_id)
        if region_id:
            query = query.where(User.region_id == region_id)
            count_query = count_query.where(User.region_id == region_id)

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(User.created_at.desc())
        )
        return result.scalars().all(), total

    async def update_user(self, user_id: str, **kwargs) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_profile_name(self, user_id: str, full_name: str) -> User:
        if not full_name or not full_name.strip():
            raise BadRequestException("Name cannot be empty")
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        user.full_name = full_name.strip()
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> User:
        if len(new_password) < 8:
            raise BadRequestException("New password must be at least 8 characters")
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")
        user.hashed_password = hash_password(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: str):
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User")
        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()
