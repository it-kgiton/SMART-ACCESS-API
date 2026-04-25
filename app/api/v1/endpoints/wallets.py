from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
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
from app.services.notification_service import NotificationService
from app.models.client import Client
from app.models.parent import Parent
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/{client_id}", response_model=WalletResponse)
async def get_wallet(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = WalletService(db)
    wallet = await service.get_by_client_id(client_id)
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
    wallet = await service.topup(data.client_id, data.amount, data.description)

    # Send top-up notification to parent
    client_result = await db.execute(select(Client).where(Client.id == data.client_id))
    client = client_result.scalar_one_or_none()
    if client and client.parent_id:
        parent_result = await db.execute(select(Parent).where(Parent.id == client.parent_id))
        parent = parent_result.scalar_one_or_none()
        if parent and parent.user_id:
            amount_fmt = f"Rp {int(data.amount):,}".replace(",", ".")
            notif_service = NotificationService(db)
            await notif_service.create(
                recipient_user_id=parent.user_id,
                notification_type="topup",
                title="Top-Up Berhasil",
                message=f"Saldo {client.name} berhasil diisi sebesar {amount_fmt}.",
                reference_type="wallet",
                reference_id=wallet.id,
            )

    return wallet


@router.get("/{client_id}/ledger", response_model=WalletLedgerListResponse)
async def get_wallet_ledger(
    client_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = WalletService(db)
    wallet = await service.get_by_client_id(client_id)
    if not wallet:
        raise NotFoundException("Wallet")
    items, total = await service.get_ledger(wallet.id, page=page, page_size=page_size)
    return WalletLedgerListResponse(
        data=[WalletLedgerResponse.model_validate(l) for l in items],
        total=total,
    )
