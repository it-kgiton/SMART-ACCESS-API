from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import BadRequestException, ForbiddenException
from app.schemas.auth import (
    LoginRequest, LoginResponse,
    UserCreate, UserResponse,
    MerchantAdminUpdateName, MerchantAdminResetPassword,
    ProfileUpdateName, ProfileChangePassword,
)
from app.services.auth_service import AuthService
from app.dependencies import (
    get_current_user, require_role, require_any_role,
    is_platform_admin, is_merchant_admin, get_user_merchant_id,
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.login(data)
    return result


@router.post("/users", response_model=UserResponse)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Only platform_admin can create new user accounts (merchant_admin, operator, etc)."""
    service = AuthService(db)
    user = await service.register(data)
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = AuthService(db)
    user = await service.get_user_by_id(current_user["sub"])
    return user


@router.get("/users/by-merchant/{merchant_id}", response_model=UserResponse)
async def get_merchant_admin(
    merchant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Get the merchant_admin account linked to a merchant."""
    from app.core.exceptions import NotFoundException
    service = AuthService(db)
    user = await service.get_merchant_admin(merchant_id)
    if not user:
        raise NotFoundException("Merchant admin account")
    return user


@router.patch("/users/by-merchant/{merchant_id}/name", response_model=UserResponse)
async def update_merchant_admin_name(
    merchant_id: str,
    data: MerchantAdminUpdateName,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Update the name of the merchant_admin account."""
    service = AuthService(db)
    user = await service.update_admin_name(merchant_id, data.name)
    return user


@router.post("/users/by-merchant/{merchant_id}/reset-password", response_model=UserResponse)
async def reset_merchant_admin_password(
    merchant_id: str,
    data: MerchantAdminResetPassword,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("platform_admin")),
):
    """Reset the password of the merchant_admin account."""
    if data.new_password != data.confirm_password:
        raise BadRequestException("Passwords do not match")
    service = AuthService(db)
    user = await service.reset_admin_password(merchant_id, data.new_password)
    return user


# ── Outlet admin management ──

@router.get("/users/by-outlet/{outlet_id}", response_model=UserResponse)
async def get_outlet_admin(
    outlet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    """Get the outlet_manager account linked to an outlet."""
    from app.core.exceptions import NotFoundException
    service = AuthService(db)
    user = await service.get_outlet_admin(outlet_id)
    if not user:
        raise NotFoundException("Outlet admin account")

    # Merchant admin can only see admin accounts for their own outlets
    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if user.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only view admin accounts for your own outlets")

    return user


@router.patch("/users/by-outlet/{outlet_id}/name", response_model=UserResponse)
async def update_outlet_admin_name(
    outlet_id: str,
    data: MerchantAdminUpdateName,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    """Update the name of the outlet_manager account."""
    if is_merchant_admin(current_user):
        service = AuthService(db)
        admin = await service.get_outlet_admin(outlet_id)
        if admin and admin.merchant_id != get_user_merchant_id(current_user):
            raise ForbiddenException("You can only update admin accounts for your own outlets")

    service = AuthService(db)
    user = await service.update_outlet_admin_name(outlet_id, data.name)
    return user


@router.post("/users/by-outlet/{outlet_id}/reset-password", response_model=UserResponse)
async def reset_outlet_admin_password(
    outlet_id: str,
    data: MerchantAdminResetPassword,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    """Reset the password of the outlet_manager account."""
    if data.new_password != data.confirm_password:
        raise BadRequestException("Passwords do not match")

    if is_merchant_admin(current_user):
        service = AuthService(db)
        admin = await service.get_outlet_admin(outlet_id)
        if admin and admin.merchant_id != get_user_merchant_id(current_user):
            raise ForbiddenException("You can only reset passwords for your own outlet accounts")

    service = AuthService(db)
    user = await service.reset_outlet_admin_password(outlet_id, data.new_password)
    return user


# ── Profile ──

@router.patch("/profile/name", response_model=UserResponse)
async def update_profile_name(
    data: ProfileUpdateName,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update the display name of the currently logged-in user."""
    service = AuthService(db)
    user = await service.update_profile_name(current_user["sub"], data.name)
    return user


@router.post("/profile/change-password", response_model=UserResponse)
async def change_password(
    data: ProfileChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Change the password of the currently logged-in user."""
    if data.new_password != data.confirm_password:
        raise BadRequestException("Passwords do not match")
    service = AuthService(db)
    user = await service.change_password(current_user["sub"], data.current_password, data.new_password)
    return user
