from typing import Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet, WalletLedger, LedgerType, WalletStatus
from app.models.client import Client
from app.core.exceptions import InsufficientBalanceException, BadRequestException


class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_client_id(self, client_id: str) -> Optional[Wallet]:
        result = await self.db.execute(
            select(Wallet).where(Wallet.client_id == client_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, wallet_id: str) -> Optional[Wallet]:
        result = await self.db.execute(
            select(Wallet).where(Wallet.id == wallet_id)
        )
        return result.scalar_one_or_none()

    async def topup(
        self, client_id: str, amount: float, description: Optional[str] = None,
        _auto_commit: bool = True,
    ) -> Wallet:
        if amount <= 0:
            raise BadRequestException("Top-up amount must be positive")

        wallet = await self.get_by_client_id(client_id)
        if not wallet:
            raise BadRequestException("Wallet not found")
        if wallet.status != WalletStatus.ACTIVE:
            raise BadRequestException("Wallet is not active")

        amount_decimal = Decimal(str(amount))
        balance_before = wallet.balance
        wallet.balance += amount_decimal

        ledger = WalletLedger(
            wallet_id=wallet.id,
            type=LedgerType.TOPUP,
            amount=amount_decimal,
            balance_before=balance_before,
            balance_after=wallet.balance,
            description=description or "Top-up",
        )
        self.db.add(ledger)

        # Sync balance to clients table
        client_result = await self.db.execute(
            select(Client).where(Client.id == client_id)
        )
        client = client_result.scalar_one_or_none()
        if client:
            client.balance = wallet.balance

        if _auto_commit:
            await self.db.commit()
            await self.db.refresh(wallet)
        else:
            await self.db.flush()
        return wallet

    async def debit(
        self,
        wallet_id: str,
        amount: float,
        reference_id: str,
        description: Optional[str] = None,
        _auto_commit: bool = True,
    ) -> Wallet:
        wallet = await self.get_by_id(wallet_id)
        if not wallet:
            raise BadRequestException("Wallet not found")
        if wallet.status != WalletStatus.ACTIVE:
            raise BadRequestException("Wallet is not active")

        amount_decimal = Decimal(str(amount))
        if wallet.balance < amount_decimal:
            raise InsufficientBalanceException()

        balance_before = wallet.balance
        wallet.balance -= amount_decimal

        ledger = WalletLedger(
            wallet_id=wallet.id,
            type=LedgerType.DEBIT,
            amount=amount_decimal,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_id=reference_id,
            description=description or "Payment debit",
        )
        self.db.add(ledger)

        # Sync balance to clients table
        client_result = await self.db.execute(
            select(Client).where(Client.id == wallet.client_id)
        )
        client = client_result.scalar_one_or_none()
        if client:
            client.balance = wallet.balance

        if _auto_commit:
            await self.db.commit()
            await self.db.refresh(wallet)
        else:
            await self.db.flush()
        return wallet

    async def refund(
        self,
        wallet_id: str,
        amount: float,
        reference_id: str,
        description: Optional[str] = None,
        _auto_commit: bool = True,
    ) -> Wallet:
        wallet = await self.get_by_id(wallet_id)
        if not wallet:
            raise BadRequestException("Wallet not found")

        amount_decimal = Decimal(str(amount))
        balance_before = wallet.balance
        wallet.balance += amount_decimal

        ledger = WalletLedger(
            wallet_id=wallet.id,
            type=LedgerType.REFUND,
            amount=amount_decimal,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_id=reference_id,
            description=description or "Refund",
        )
        self.db.add(ledger)

        # Sync balance to clients table
        client_result = await self.db.execute(
            select(Client).where(Client.id == wallet.client_id)
        )
        client = client_result.scalar_one_or_none()
        if client:
            client.balance = wallet.balance

        if _auto_commit:
            await self.db.commit()
            await self.db.refresh(wallet)
        else:
            await self.db.flush()
        return wallet

    async def get_ledger(
        self, wallet_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[WalletLedger], int]:
        count_query = (
            select(func.count())
            .select_from(WalletLedger)
            .where(WalletLedger.wallet_id == wallet_id)
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = (
            select(WalletLedger)
            .where(WalletLedger.wallet_id == wallet_id)
            .order_by(WalletLedger.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total
