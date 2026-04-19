from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.transaction import (
    PurchaseRequest,
    TopUpRequest,
    RefundRequest,
    TransactionResponse,
    TransactionStatsResponse,
)
from app.services.transaction_service import TransactionService
from app.dependencies import get_current_user, require_any_role

router = APIRouter()


@router.post("/purchase")
async def create_purchase(
    data: PurchaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "merchant")),
):
    service = TransactionService(db)
    transaction = await service.purchase(data)
    return {"success": True, "data": TransactionResponse.model_validate(transaction)}


@router.post("/topup")
async def create_topup(
    data: TopUpRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "parent")),
):
    service = TransactionService(db)
    transaction = await service.topup(data)
    return {"success": True, "data": TransactionResponse.model_validate(transaction)}


@router.post("/refund")
async def create_refund(
    data: RefundRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = TransactionService(db)
    transaction = await service.refund(data)
    return {"success": True, "data": TransactionResponse.model_validate(transaction)}


@router.get("/")
async def list_transactions(
    school_id: Optional[str] = None, client_id: Optional[str] = None,
    merchant_id: Optional[str] = None, type: Optional[str] = None,
    status: Optional[str] = None, date_from: Optional[str] = None,
    date_to: Optional[str] = None, skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TransactionService(db)
    transactions, total = await service.list_transactions(
        school_id=school_id, client_id=client_id, merchant_id=merchant_id,
        type=type, status=status, date_from=date_from, date_to=date_to,
        skip=skip, limit=limit,
    )
    return {
        "success": True,
        "data": [TransactionResponse.model_validate(t) for t in transactions],
        "total": total,
    }


@router.get("/stats", response_model=TransactionStatsResponse)
async def get_transaction_stats(
    school_id: Optional[str] = None,
    merchant_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "merchant")),
):
    service = TransactionService(db)
    stats = await service.get_stats(
        school_id=school_id, merchant_id=merchant_id,
        date_from=date_from, date_to=date_to,
    )
    return stats


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = TransactionService(db)
    transaction = await service.get_by_id(transaction_id)
    if not transaction:
        raise NotFoundException("Transaction")
    return transaction
