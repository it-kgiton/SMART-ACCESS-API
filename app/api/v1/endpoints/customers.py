from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException, ForbiddenException
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
)
from app.services.customer_service import CustomerService
from app.dependencies import (
    get_current_user,
    require_any_role,
    is_merchant_admin,
    get_user_merchant_id,
)

router = APIRouter()


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    merchant_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = CustomerService(db)

    # Merchant admin is scoped to their own merchant's customers
    if is_merchant_admin(current_user):
        merchant_id = get_user_merchant_id(current_user)

    items, total = await service.list(
        page=page, page_size=page_size, search=search, status=status,
        merchant_id=merchant_id,
    )
    responses = []
    for c in items:
        resp = CustomerResponse(
            id=c.id,
            merchant_id=c.merchant_id,
            external_id=c.external_id,
            name=c.name,
            email=c.email,
            phone=c.phone,
            identity_number=c.identity_number,
            photo_url=c.photo_url,
            status=c.status,
            has_face_credential=c.face_credential is not None,
            has_fingerprint_credential=c.fingerprint_credential is not None,
            wallet_balance=float(c.wallet.balance) if c.wallet else None,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        responses.append(resp)

    return CustomerListResponse(
        items=responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = CustomerService(db)
    c = await service.get_by_id(customer_id)
    if not c:
        raise NotFoundException("Customer")

    # Merchant admin can only view their own customers
    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if c.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only view your own customers")

    return CustomerResponse(
        id=c.id,
        merchant_id=c.merchant_id,
        external_id=c.external_id,
        name=c.name,
        email=c.email,
        phone=c.phone,
        identity_number=c.identity_number,
        photo_url=c.photo_url,
        status=c.status,
        has_face_credential=c.face_credential is not None,
        has_fingerprint_credential=c.fingerprint_credential is not None,
        wallet_balance=float(c.wallet.balance) if c.wallet else None,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    """Platform admin can create for any merchant. Merchant admin auto-assigns to their merchant."""
    if is_merchant_admin(current_user):
        data.merchant_id = get_user_merchant_id(current_user)

    service = CustomerService(db)
    c = await service.create(data)
    return CustomerResponse(
        id=c.id,
        merchant_id=c.merchant_id,
        external_id=c.external_id,
        name=c.name,
        email=c.email,
        phone=c.phone,
        identity_number=c.identity_number,
        photo_url=c.photo_url,
        status=c.status,
        has_face_credential=False,
        has_fingerprint_credential=False,
        wallet_balance=float(data.initial_balance),
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = CustomerService(db)
    c = await service.get_by_id(customer_id)
    if not c:
        raise NotFoundException("Customer")

    # Merchant admin can only update their own customers
    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if c.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only update your own customers")

    c = await service.update(customer_id, data)
    return CustomerResponse(
        id=c.id,
        merchant_id=c.merchant_id,
        external_id=c.external_id,
        name=c.name,
        email=c.email,
        phone=c.phone,
        identity_number=c.identity_number,
        photo_url=c.photo_url,
        status=c.status,
        has_face_credential=c.face_credential is not None,
        has_fingerprint_credential=c.fingerprint_credential is not None,
        wallet_balance=float(c.wallet.balance) if c.wallet else None,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    service = CustomerService(db)
    c = await service.get_by_id(customer_id)
    if not c:
        raise NotFoundException("Customer")

    # Merchant admin can only delete their own customers
    if is_merchant_admin(current_user):
        user_merchant_id = get_user_merchant_id(current_user)
        if c.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only manage your own customers")

    deleted = await service.delete(customer_id)
    if not deleted:
        raise NotFoundException("Customer")
    return {"message": "Customer deactivated"}
