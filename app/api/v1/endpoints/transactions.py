from fastapi import APIRouter, Depends
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.transaction import (
    PurchaseRequest,
    TopUpRequest,
    RefundRequest,
    TransactionResponse,
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
    result = await service.purchase(
        client_id=data.client_id,
        merchant_id=data.merchant_id,
        items=data.items,
        device_id=data.device_id,
        biometric_method=data.biometric_method,
    )
    return {"success": True, "data": TransactionResponse.model_validate(result["transaction"])}


@router.post("/topup")
async def create_topup(
    data: TopUpRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "parent")),
):
    service = TransactionService(db)
    result = await service.topup(
        client_id=data.client_id,
        parent_id=data.parent_id,
        amount=data.amount,
        payment_method=data.payment_method,
    )
    return {"success": True, "data": TransactionResponse.model_validate(result["transaction"])}


@router.post("/refund")
async def create_refund(
    data: RefundRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = TransactionService(db)
    result = await service.refund(
        transaction_id=data.transaction_id,
        reason=data.reason,
    )
    return {"success": True, "data": TransactionResponse.model_validate(result["transaction"])}


@router.get("")
async def list_transactions(
    school_id: Optional[str] = None, client_id: Optional[str] = None,
    merchant_id: Optional[str] = None, type: Optional[str] = None,
    status: Optional[str] = None, date_from: Optional[str] = None,
    date_to: Optional[str] = None, skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    def _parse_date(s: Optional[str]) -> Optional[datetime]:
        if not s:
            return None
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None

    service = TransactionService(db)
    transactions, total = await service.list_transactions(
        school_id=school_id, client_id=client_id, merchant_id=merchant_id,
        txn_type=type, status=status,
        date_from=_parse_date(date_from), date_to=_parse_date(date_to),
        skip=skip, limit=limit,
    )
    return {
        "success": True,
        "data": [TransactionResponse.model_validate(t) for t in transactions],
        "total": total,
    }


@router.get("/stats")
async def get_transaction_stats(
    school_id: Optional[str] = None,
    merchant_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "merchant", "parent")),
):
    def _parse_date(s: Optional[str]) -> Optional[datetime]:
        if not s:
            return None
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None

    service = TransactionService(db)
    stats = await service.get_stats(
        school_id=school_id, merchant_id=merchant_id,
        date_from=_parse_date(date_from), date_to=_parse_date(date_to),
    )
    return {"success": True, "data": stats}


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
