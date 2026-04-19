from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import BadRequestException
from app.schemas.auth import (
    LoginRequest, LoginResponse, UserCreate, UserResponse, UserUpdate,
    ProfileUpdateName, ProfileChangePassword, UserListResponse,
)
from app.services.auth_service import AuthService
from app.dependencies import get_current_user, require_role, require_any_role

router = APIRouter()


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.login(data)
    return {"success": True, "data": result}


@router.post("/users", response_model=UserResponse)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
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


@router.patch("/me/name")
async def update_my_name(
    data: ProfileUpdateName,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = AuthService(db)
    user = await service.update_profile_name(current_user["sub"], data.full_name)
    return {"success": True, "data": UserResponse.model_validate(user)}


@router.post("/me/change-password")
async def change_my_password(
    data: ProfileChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if data.new_password != data.confirm_password:
        raise BadRequestException("Passwords do not match")
    service = AuthService(db)
    await service.change_password(current_user["sub"], data.current_password, data.new_password)
    return {"success": True, "message": "Password changed"}


@router.get("/users")
async def list_users(
    role: str = None, school_id: str = None, region_id: str = None,
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = AuthService(db)
    users, total = await service.list_users(
        role=role, school_id=school_id, region_id=region_id, skip=skip, limit=limit,
    )
    return {"success": True, "data": [UserResponse.model_validate(u) for u in users], "total": total}


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    from app.core.exceptions import NotFoundException
    service = AuthService(db)
    user = await service.get_user_by_id(user_id)
    if not user:
        raise NotFoundException("User")
    return user


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = AuthService(db)
    user = await service.update_user(user_id, **data.model_dump(exclude_unset=True))
    return {"success": True, "data": UserResponse.model_validate(user)}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("super_admin")),
):
    service = AuthService(db)
    await service.delete_user(user_id)
    return {"success": True, "message": "User deactivated"}
