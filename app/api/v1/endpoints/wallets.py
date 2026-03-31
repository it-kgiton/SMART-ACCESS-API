from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.wallet import (
    WalletResponse,
    WalletTopUp,
    WalletLedgerResponse,
    WalletLedgerListResponse,
)
from app.services.wallet_service import WalletService
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/{customer_id}", response_model=WalletResponse)
async def get_wallet(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = WalletService(db)
    wallet = await service.get_by_customer_id(customer_id)
    if not wallet:
        raise NotFoundException("Wallet")
    return wallet


@router.post("/topup", response_model=WalletResponse)
async def topup_wallet(
    data: WalletTopUp,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = WalletService(db)
    wallet = await service.topup(data.customer_id, data.amount, data.description)
    return wallet


@router.get("/{customer_id}/ledger", response_model=WalletLedgerListResponse)
async def get_wallet_ledger(
    customer_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = WalletService(db)
    wallet = await service.get_by_customer_id(customer_id)
    if not wallet:
        raise NotFoundException("Wallet")
    items, total = await service.get_ledger(wallet.id, page=page, page_size=page_size)
    return WalletLedgerListResponse(
        items=[WalletLedgerResponse.model_validate(l) for l in items],
        total=total,
        page=page,
        page_size=page_size,
    )
