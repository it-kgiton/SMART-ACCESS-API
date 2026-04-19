import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from loguru import logger

from app.models.transaction import Transaction, TransactionItem, TransactionType, TransactionStatus, BiometricMethod
from app.models.device import Device, DeviceStatus
from app.models.client import Client, ClientStatus
from app.models.merchant import Merchant
from app.models.wallet import Wallet, WalletStatus
from app.models.biometric import FaceCredential, FingerprintCredential, CredentialStatus
from app.services.wallet_service import WalletService
from app.services.biometric_engine import biometric_engine
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    InsufficientBalanceException,
)


def _generate_ref(txn_type: str) -> str:
    short_id = uuid.uuid4().hex[:12].upper()
    prefix = {"topup": "TU", "purchase": "PR", "refund": "RF", "withdrawal": "WD"}.get(txn_type, "TX")
    return f"{prefix}-{short_id}"


class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wallet_service = WalletService(db)

    # ── Purchase (biometric / PIN) ──

    async def purchase(
        self,
        client_id: str,
        merchant_id: str,
        items: list,
        device_id: Optional[str] = None,
        biometric_method: Optional[str] = "fingerprint_face",
    ) -> dict:
        client = await self._get_client(client_id)
        merchant = await self._get_merchant(merchant_id)

        total = Decimal("0.00")
        txn_items = []
        for item in items:
            subtotal = Decimal(str(item.unit_price)) * item.quantity
            total += subtotal
            txn_items.append(TransactionItem(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
                subtotal=subtotal,
            ))

        # Check daily spending limit
        if client.daily_spending_limit:
            today_spent = await self._get_today_spent(client_id)
            if today_spent + total > client.daily_spending_limit:
                raise BadRequestException("Daily spending limit exceeded")

        wallet = await self.wallet_service.get_by_client_id(client_id)
        if not wallet or wallet.status != WalletStatus.ACTIVE:
            raise BadRequestException("Wallet not active")
        if wallet.balance < total:
            raise InsufficientBalanceException()

        txn = Transaction(
            transaction_ref=_generate_ref("purchase"),
            type=TransactionType.PURCHASE,
            client_id=client_id,
            merchant_id=merchant_id,
            school_id=client.school_id,
            device_id=device_id,
            amount=total,
            fee_amount=Decimal("0.00"),
            status=TransactionStatus.SUCCESS,
            biometric_method=biometric_method,
            completed_at=datetime.now(timezone.utc),
        )
        for ti in txn_items:
            txn.items.append(ti)

        self.db.add(txn)
        await self.db.flush()

        wallet = await self.wallet_service.debit(
            wallet.id, float(total), txn.id, f"Purchase at {merchant.business_name}"
        )

        # Credit merchant balance
        merchant.balance += total
        await self.db.commit()
        await self.db.refresh(txn)

        return {
            "transaction": txn,
            "balance_after": float(wallet.balance),
        }

    # ── Top-up ──

    async def topup(
        self,
        client_id: str,
        parent_id: str,
        amount: float,
        payment_method: str = "qris",
    ) -> dict:
        client = await self._get_client(client_id)

        txn = Transaction(
            transaction_ref=_generate_ref("topup"),
            type=TransactionType.TOPUP,
            client_id=client_id,
            parent_id=parent_id,
            school_id=client.school_id,
            amount=Decimal(str(amount)),
            fee_amount=Decimal("0.00"),
            status=TransactionStatus.SUCCESS,
            payment_method=payment_method,
            completed_at=datetime.now(timezone.utc),
        )
        self.db.add(txn)
        await self.db.flush()

        wallet = await self.wallet_service.topup(
            client_id, amount, f"Top-up via {payment_method}"
        )

        await self.db.commit()
        await self.db.refresh(txn)

        return {
            "transaction": txn,
            "balance_after": float(wallet.balance),
        }

    # ── Refund ──

    async def refund(
        self, transaction_id: str, reason: Optional[str] = None
    ) -> dict:
        result = await self.db.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        original_txn = result.scalar_one_or_none()
        if not original_txn:
            raise NotFoundException("Transaction")
        if original_txn.type != TransactionType.PURCHASE:
            raise BadRequestException("Only purchase transactions can be refunded")
        if original_txn.status == TransactionStatus.REFUNDED:
            raise BadRequestException("Transaction already refunded")

        refund_txn = Transaction(
            transaction_ref=_generate_ref("refund"),
            type=TransactionType.REFUND,
            client_id=original_txn.client_id,
            merchant_id=original_txn.merchant_id,
            school_id=original_txn.school_id,
            amount=original_txn.amount,
            fee_amount=Decimal("0.00"),
            status=TransactionStatus.SUCCESS,
            reference_transaction_id=original_txn.id,
            rejection_reason=reason,
            completed_at=datetime.now(timezone.utc),
        )
        self.db.add(refund_txn)

        # Refund to client wallet
        wallet = await self.wallet_service.get_by_client_id(original_txn.client_id)
        if wallet:
            await self.wallet_service.refund(
                wallet.id, float(original_txn.amount), refund_txn.id, "Refund"
            )

        # Debit merchant balance
        if original_txn.merchant_id:
            merchant_result = await self.db.execute(
                select(Merchant).where(Merchant.id == original_txn.merchant_id)
            )
            merchant = merchant_result.scalar_one_or_none()
            if merchant:
                merchant.balance -= original_txn.amount

        original_txn.status = TransactionStatus.REFUNDED
        await self.db.commit()
        await self.db.refresh(refund_txn)

        return {"transaction": refund_txn}

    # ── Biometric payment from device ──

    async def process_face_payment(
        self, device_id: str, image_bytes: bytes, amount: float,
    ) -> dict:
        device = await self._get_device(device_id)

        if not biometric_engine.is_ready:
            raise BadRequestException("Biometric engine is not initialized")

        embedding = biometric_engine.extract_face_embedding(image_bytes)
        if embedding is None:
            raise BadRequestException("No face detected")

        client, score = await self._find_client_by_face(embedding)
        if not client:
            raise BadRequestException("Face not recognized")

        return await self._execute_biometric_payment(
            client, device, amount, "fingerprint_face", score
        )

    async def process_fingerprint_payment(
        self, device_id: str, fingerprint_data: bytes, amount: float,
    ) -> dict:
        device = await self._get_device(device_id)

        client, score = await self._find_client_by_fingerprint(fingerprint_data)
        if not client:
            raise BadRequestException("Fingerprint not recognized")

        return await self._execute_biometric_payment(
            client, device, amount, "fingerprint_face", score
        )

    # ── List / Stats ──

    async def list_transactions(
        self, school_id: Optional[str] = None, client_id: Optional[str] = None,
        merchant_id: Optional[str] = None, txn_type: Optional[str] = None,
        status: Optional[str] = None, date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None, skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(Transaction)
        count_query = select(func.count(Transaction.id))

        filters = []
        if school_id:
            filters.append(Transaction.school_id == school_id)
        if client_id:
            filters.append(Transaction.client_id == client_id)
        if merchant_id:
            filters.append(Transaction.merchant_id == merchant_id)
        if txn_type:
            filters.append(Transaction.type == txn_type)
        if status:
            filters.append(Transaction.status == status)
        if date_from:
            filters.append(Transaction.created_at >= date_from)
        if date_to:
            filters.append(Transaction.created_at <= date_to)

        for f in filters:
            query = query.where(f)
            count_query = count_query.where(f)

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def get_stats(
        self, school_id: Optional[str] = None, merchant_id: Optional[str] = None,
        date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
    ) -> dict:
        base_filter = []
        if school_id:
            base_filter.append(Transaction.school_id == school_id)
        if merchant_id:
            base_filter.append(Transaction.merchant_id == merchant_id)
        if date_from:
            base_filter.append(Transaction.created_at >= date_from)
        if date_to:
            base_filter.append(Transaction.created_at <= date_to)

        async def _count(extra_filters=None):
            q = select(func.count(Transaction.id))
            for f in base_filter:
                q = q.where(f)
            for f in (extra_filters or []):
                q = q.where(f)
            return (await self.db.execute(q)).scalar()

        async def _sum(extra_filters=None):
            q = select(func.coalesce(func.sum(Transaction.amount), 0))
            for f in base_filter:
                q = q.where(f)
            for f in (extra_filters or []):
                q = q.where(f)
            return float((await self.db.execute(q)).scalar())

        total = await _count()
        success = await _count([Transaction.status == TransactionStatus.SUCCESS])
        failed = await _count([Transaction.status == TransactionStatus.FAILED])
        refunded = await _count([Transaction.status == TransactionStatus.REFUNDED])
        total_amount = await _sum([Transaction.status == TransactionStatus.SUCCESS])
        total_fee = await _sum([Transaction.status == TransactionStatus.SUCCESS, Transaction.fee_amount > 0])

        return {
            "total_transactions": total,
            "total_success": success,
            "total_failed": failed,
            "total_refunded": refunded,
            "total_amount": total_amount,
            "total_fee": total_fee,
        }

    # ── Private helpers ──

    async def _get_client(self, client_id: str) -> Client:
        result = await self.db.execute(
            select(Client).where(Client.id == client_id)
        )
        client = result.scalar_one_or_none()
        if not client:
            raise NotFoundException("Client")
        if client.status != ClientStatus.ACTIVE:
            raise BadRequestException("Client account is not active")
        return client

    async def _get_merchant(self, merchant_id: str) -> Merchant:
        result = await self.db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        merchant = result.scalar_one_or_none()
        if not merchant:
            raise NotFoundException("Merchant")
        return merchant

    async def _get_device(self, device_id: str) -> Device:
        result = await self.db.execute(
            select(Device).where(Device.id == device_id)
        )
        device = result.scalar_one_or_none()
        if not device or not device.is_active:
            raise NotFoundException("Device")
        if device.status == DeviceStatus.BLOCKED:
            raise BadRequestException("Device is blocked")
        return device

    async def _get_today_spent(self, client_id: str) -> Decimal:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.client_id == client_id,
                Transaction.type == TransactionType.PURCHASE,
                Transaction.status == TransactionStatus.SUCCESS,
                Transaction.created_at >= today_start,
            )
        )
        return Decimal(str(result.scalar()))

    async def _find_client_by_face(
        self, embedding: np.ndarray
    ) -> tuple[Optional[Client], float]:
        from app.config import settings

        result = await self.db.execute(
            select(FaceCredential).where(FaceCredential.status == CredentialStatus.ACTIVE)
        )
        credentials = result.scalars().all()

        best_match = None
        best_score = 0.0

        for cred in credentials:
            stored_embedding = np.frombuffer(cred.embedding, dtype=np.float32)
            score = biometric_engine.compare_face_embeddings(embedding, stored_embedding)
            if score > best_score:
                best_score = score
                best_match = cred

        if best_match and best_score >= settings.FACE_SIMILARITY_THRESHOLD:
            cust_result = await self.db.execute(
                select(Client).where(Client.id == best_match.client_id)
            )
            client = cust_result.scalar_one_or_none()
            return client, best_score

        return None, best_score

    async def _find_client_by_fingerprint(
        self, fingerprint_data: bytes
    ) -> tuple[Optional[Client], float]:
        result = await self.db.execute(
            select(FingerprintCredential).where(
                FingerprintCredential.status == CredentialStatus.ACTIVE
            )
        )
        credentials = result.scalars().all()

        for cred in credentials:
            is_match, score = biometric_engine.match_fingerprint(
                fingerprint_data, cred.template_data
            )
            if is_match:
                cust_result = await self.db.execute(
                    select(Client).where(Client.id == cred.client_id)
                )
                client = cust_result.scalar_one_or_none()
                return client, score

        return None, 0.0

    async def _execute_biometric_payment(
        self, client: Client, device: Device, amount: float,
        biometric_method: str, confidence_score: float,
    ) -> dict:
        wallet = await self.wallet_service.get_by_client_id(client.id)
        if not wallet or wallet.status != WalletStatus.ACTIVE:
            raise BadRequestException("Wallet not active")
        if wallet.balance < Decimal(str(amount)):
            raise InsufficientBalanceException()

        merchant_id = device.merchant_id

        txn = Transaction(
            transaction_ref=_generate_ref("purchase"),
            type=TransactionType.PURCHASE,
            client_id=client.id,
            merchant_id=merchant_id,
            school_id=client.school_id,
            device_id=device.id,
            amount=Decimal(str(amount)),
            fee_amount=Decimal("0.00"),
            status=TransactionStatus.SUCCESS,
            biometric_method=biometric_method,
            confidence_score=confidence_score,
            completed_at=datetime.now(timezone.utc),
        )
        self.db.add(txn)
        await self.db.flush()

        wallet = await self.wallet_service.debit(
            wallet.id, amount, txn.id, "Biometric payment"
        )

        if merchant_id:
            merchant = await self._get_merchant(merchant_id)
            merchant.balance += Decimal(str(amount))

        await self.db.commit()
        await self.db.refresh(txn)

        return {
            "transaction": txn,
            "client_name": client.name,
            "balance_after": float(wallet.balance),
        }
