from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, DeviceBlockedException


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
        if user_role != required_role and user_role != "platform_admin":
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(f"Role '{required_role}' required")
        return current_user
    return role_checker


def require_any_role(*allowed_roles: str):
    """Allow access if user has any of the specified roles. platform_admin always passes."""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "")
        if user_role == "platform_admin":
            return current_user
        if user_role not in allowed_roles:
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(f"One of {allowed_roles} roles required")
        return current_user
    return role_checker


def is_platform_admin(user: dict) -> bool:
    return user.get("role") == "platform_admin"


def is_merchant_admin(user: dict) -> bool:
    return user.get("role") == "merchant_admin"


def is_outlet_manager(user: dict) -> bool:
    return user.get("role") == "outlet_manager"


def get_user_merchant_id(user: dict) -> Optional[str]:
    """Get the merchant_id from the current user's token. Returns None for platform_admin."""
    return user.get("merchant_id")


def get_user_outlet_id(user: dict) -> Optional[str]:
    """Get the outlet_id from the current user's token. Returns None if not set."""
    return user.get("outlet_id")
