from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException


async def get_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    return db


async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException()
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")
    return payload


async def get_current_device(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Device not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if payload is None:
        raise UnauthorizedException("Invalid or expired device token")
    if payload.get("type") != "device":
        raise UnauthorizedException("Not a device token")
    return payload


def require_role(required_role: str):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        if user_role != required_role and user_role != "super_admin":
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(f"Role '{required_role}' required")
        return current_user
    return role_checker


def require_any_role(*allowed_roles: str):
    """Allow access if user has any of the specified roles. super_admin always passes."""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        if user_role == "super_admin":
            return current_user
        if user_role not in allowed_roles:
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(f"One of {allowed_roles} roles required")
        return current_user
    return role_checker


def is_super_admin(user: dict) -> bool:
    return user.get("role") == "super_admin"


def is_admin_hub(user: dict) -> bool:
    return user.get("role") == "admin_hub"


def is_admin_ops(user: dict) -> bool:
    return user.get("role") == "admin_ops"


def is_merchant(user: dict) -> bool:
    return user.get("role") == "merchant"


def is_parent(user: dict) -> bool:
    return user.get("role") == "parent"


def get_user_merchant_id(user: dict) -> Optional[str]:
    return user.get("merchant_id")


def get_user_school_id(user: dict) -> Optional[str]:
    return user.get("school_id")


def get_user_region_id(user: dict) -> Optional[str]:
    return user.get("region_id")
