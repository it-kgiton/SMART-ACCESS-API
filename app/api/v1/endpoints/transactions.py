from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transaction import (
    TransactionResponse,
    TransactionListResponse,
    TransactionStatsResponse,
)
from app.services.transaction_service import TransactionService
from app.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    merchant_id: Optional[str] = None,
    outlet_id: Optional[str] = None,
    device_id: Optional[str] = None,
    status: Optional[str] = None,
    biometric_method: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TransactionService(db)
    items, total = await service.list_transactions(
        page=page,
        page_size=page_size,
        merchant_id=merchant_id,
        outlet_id=outlet_id,
        device_id=device_id,
        status=status,
        biometric_method=biometric_method,
        date_from=date_from,
        date_to=date_to,
    )
    return TransactionListResponse(
        items=[TransactionResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=TransactionStatsResponse)
async def get_transaction_stats(
    merchant_id: Optional[str] = None,
    outlet_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TransactionService(db)
    stats = await service.get_stats(
        merchant_id=merchant_id,
        outlet_id=outlet_id,
        date_from=date_from,
        date_to=date_to,
    )
    now = datetime.utcnow()
    return TransactionStatsResponse(
        **stats,
        period_start=date_from or datetime(2024, 1, 1),
        period_end=date_to or now,
    )
