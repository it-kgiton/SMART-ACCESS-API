import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from loguru import logger

from app.models.transaction import Transaction, TransactionStatus, BiometricMethod
from app.models.device import Device, DeviceStatus
from app.models.outlet import Outlet
from app.models.customer import Customer, CustomerStatus
from app.models.wallet import Wallet, WalletStatus
from app.models.biometric import FaceCredential, FingerprintCredential, CredentialStatus
from app.services.wallet_service import WalletService
from app.services.biometric_engine import biometric_engine
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
    DeviceBlockedException,
    BiometricVerificationFailed,
    InsufficientBalanceException,
)


class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wallet_service = WalletService(db)

    async def process_face_payment(
        self,
        device_id: str,
        image_bytes: bytes,
        amount: float,
        request_reference: str,
        fallback_from: Optional[str] = None,
    ) -> dict:
        """Process face-based payment from device."""
        # Check idempotency
        existing = await self._get_by_reference(request_reference)
        if existing:
            return self._format_response(existing)

        # Validate device
        device, outlet = await self._validate_device(device_id)

        # Extract embedding from submitted image
        embedding = biometric_engine.extract_face_embedding(image_bytes)
        if embedding is None:
            txn = await self._create_failed_transaction(
                device, outlet, amount, BiometricMethod.FACE,
                request_reference, fallback_from, "No face detected in image"
            )
            return self._format_response(txn)

        # Search for matching customer
        customer, score = await self._find_customer_by_face(embedding)
        if not customer:
            txn = await self._create_failed_transaction(
                device, outlet, amount, BiometricMethod.FACE,
                request_reference, fallback_from, "Face not recognized"
            )
            return self._format_response(txn)

        # Process payment
        return await self._execute_payment(
            device, outlet, customer, amount,
            BiometricMethod.FACE, request_reference, score, fallback_from
        )

    async def process_fingerprint_payment(
        self,
        device_id: str,
        fingerprint_data: bytes,
        amount: float,
        request_reference: str,
        fallback_from: Optional[str] = None,
    ) -> dict:
        """Process fingerprint-based payment from device."""
        existing = await self._get_by_reference(request_reference)
        if existing:
            return self._format_response(existing)

        device, outlet = await self._validate_device(device_id)

        customer, score = await self._find_customer_by_fingerprint(fingerprint_data)
        if not customer:
            txn = await self._create_failed_transaction(
                device, outlet, amount, BiometricMethod.FINGERPRINT,
                request_reference, fallback_from, "Fingerprint not recognized"
            )
            return self._format_response(txn)

        return await self._execute_payment(
            device, outlet, customer, amount,
            BiometricMethod.FINGERPRINT, request_reference, score, fallback_from
        )

    async def _validate_device(self, device_id: str) -> tuple[Device, Outlet]:
        result = await self.db.execute(
            select(Device).where(Device.id == device_id)
        )
        device = result.scalar_one_or_none()
        if not device or not device.is_active:
            raise NotFoundException("Device")
        if device.status == DeviceStatus.BLOCKED:
            raise DeviceBlockedException()

        result = await self.db.execute(
            select(Outlet).where(Outlet.id == device.outlet_id)
        )
        outlet = result.scalar_one_or_none()
        if not outlet or not outlet.is_active:
            raise BadRequestException("Outlet is not active")

        return device, outlet

    async def _find_customer_by_face(
        self, embedding: np.ndarray
    ) -> tuple[Optional[Customer], float]:
        from app.config import settings

        result = await self.db.execute(
            select(FaceCredential).where(
                FaceCredential.status == CredentialStatus.ACTIVE
            )
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
                select(Customer).where(Customer.id == best_match.customer_id)
            )
            customer = cust_result.scalar_one_or_none()
            return customer, best_score

        return None, best_score

    async def _find_customer_by_fingerprint(
        self, fingerprint_data: bytes
    ) -> tuple[Optional[Customer], float]:
        from app.config import settings

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
                    select(Customer).where(Customer.id == cred.customer_id)
                )
                customer = cust_result.scalar_one_or_none()
                return customer, score

        return None, 0.0

    async def _execute_payment(
        self,
        device: Device,
        outlet: Outlet,
        customer: Customer,
        amount: float,
        method: BiometricMethod,
        request_reference: str,
        confidence_score: float,
        fallback_from: Optional[str] = None,
    ) -> dict:
        if customer.status != CustomerStatus.ACTIVE:
            txn = await self._create_failed_transaction(
                device, outlet, amount, method,
                request_reference, fallback_from, "Customer account is not active"
            )
            return self._format_response(txn)

        wallet = await self.wallet_service.get_by_customer_id(customer.id)
        if not wallet or wallet.status != WalletStatus.ACTIVE:
            txn = await self._create_failed_transaction(
                device, outlet, amount, method,
                request_reference, fallback_from, "Wallet not active"
            )
            return self._format_response(txn)

        if wallet.balance < Decimal(str(amount)):
            txn = Transaction(
                merchant_id=outlet.merchant_id,
                outlet_id=outlet.id,
                device_id=device.id,
                customer_id=customer.id,
                wallet_id=wallet.id,
                biometric_method=method,
                fallback_from=fallback_from,
                amount=Decimal(str(amount)),
                status=TransactionStatus.REJECTED,
                confidence_score=confidence_score,
                request_reference=request_reference,
                rejection_reason="Insufficient balance",
                completed_at=datetime.now(timezone.utc),
            )
            self.db.add(txn)
            await self.db.commit()
            await self.db.refresh(txn)
            return self._format_response(txn)

        # Debit wallet
        try:
            txn = Transaction(
                merchant_id=outlet.merchant_id,
                outlet_id=outlet.id,
                device_id=device.id,
                customer_id=customer.id,
                wallet_id=wallet.id,
                biometric_method=method,
                fallback_from=fallback_from,
                amount=Decimal(str(amount)),
                status=TransactionStatus.APPROVED,
                confidence_score=confidence_score,
                request_reference=request_reference,
                completed_at=datetime.now(timezone.utc),
            )
            self.db.add(txn)
            await self.db.flush()

            wallet = await self.wallet_service.debit(
                wallet.id, amount, txn.id, f"Payment at {outlet.name}"
            )

            await self.db.commit()
            await self.db.refresh(txn)

            response = self._format_response(txn)
            response["customer_name"] = customer.name
            response["balance_after"] = float(wallet.balance)
            return response

        except InsufficientBalanceException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Payment processing error: {e}")
            raise BadRequestException("Payment processing failed")

    async def _create_failed_transaction(
        self,
        device: Device,
        outlet: Outlet,
        amount: float,
        method: BiometricMethod,
        request_reference: str,
        fallback_from: Optional[str],
        reason: str,
    ) -> Transaction:
        txn = Transaction(
            merchant_id=outlet.merchant_id,
            outlet_id=outlet.id,
            device_id=device.id,
            biometric_method=method,
            fallback_from=fallback_from,
            amount=Decimal(str(amount)),
            status=TransactionStatus.REJECTED,
            request_reference=request_reference,
            rejection_reason=reason,
            completed_at=datetime.now(timezone.utc),
        )
        self.db.add(txn)
        await self.db.commit()
        await self.db.refresh(txn)
        return txn

    async def _get_by_reference(self, reference: str) -> Optional[Transaction]:
        result = await self.db.execute(
            select(Transaction).where(Transaction.request_reference == reference)
        )
        return result.scalar_one_or_none()

    def _format_response(self, txn: Transaction) -> dict:
        return {
            "transaction_id": txn.id,
            "status": txn.status,
            "amount": float(txn.amount),
            "biometric_method": txn.biometric_method,
            "rejection_reason": txn.rejection_reason,
            "confidence_score": txn.confidence_score,
            "customer_name": None,
            "balance_after": None,
        }

    async def list_transactions(
        self,
        page: int = 1,
        page_size: int = 20,
        merchant_id: Optional[str] = None,
        outlet_id: Optional[str] = None,
        device_id: Optional[str] = None,
        status: Optional[str] = None,
        biometric_method: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[list[Transaction], int]:
        query = select(Transaction)
        count_query = select(func.count()).select_from(Transaction)

        filters = []
        if merchant_id:
            filters.append(Transaction.merchant_id == merchant_id)
        if outlet_id:
            filters.append(Transaction.outlet_id == outlet_id)
        if device_id:
            filters.append(Transaction.device_id == device_id)
        if status:
            filters.append(Transaction.status == status)
        if biometric_method:
            filters.append(Transaction.biometric_method == biometric_method)
        if date_from:
            filters.append(Transaction.created_at >= date_from)
        if date_to:
            filters.append(Transaction.created_at <= date_to)

        for f in filters:
            query = query.where(f)
            count_query = count_query.where(f)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Transaction.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_stats(
        self,
        merchant_id: Optional[str] = None,
        outlet_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict:
        base_filter = []
        if merchant_id:
            base_filter.append(Transaction.merchant_id == merchant_id)
        if outlet_id:
            base_filter.append(Transaction.outlet_id == outlet_id)
        if date_from:
            base_filter.append(Transaction.created_at >= date_from)
        if date_to:
            base_filter.append(Transaction.created_at <= date_to)

        # Total count
        q = select(func.count()).select_from(Transaction)
        for f in base_filter:
            q = q.where(f)
        total = (await self.db.execute(q)).scalar()

        # Approved count
        q = select(func.count()).select_from(Transaction).where(
            Transaction.status == TransactionStatus.APPROVED
        )
        for f in base_filter:
            q = q.where(f)
        approved = (await self.db.execute(q)).scalar()

        # Total amount (approved only)
        q = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.status == TransactionStatus.APPROVED
        )
        for f in base_filter:
            q = q.where(f)
        total_amount = float((await self.db.execute(q)).scalar())

        # Face count
        q = select(func.count()).select_from(Transaction).where(
            Transaction.biometric_method == BiometricMethod.FACE
        )
        for f in base_filter:
            q = q.where(f)
        face_count = (await self.db.execute(q)).scalar()

        # Fingerprint count
        q = select(func.count()).select_from(Transaction).where(
            Transaction.biometric_method == BiometricMethod.FINGERPRINT
        )
        for f in base_filter:
            q = q.where(f)
        finger_count = (await self.db.execute(q)).scalar()

        # Fallback count
        q = select(func.count()).select_from(Transaction).where(
            Transaction.fallback_from.is_not(None)
        )
        for f in base_filter:
            q = q.where(f)
        fallback_count = (await self.db.execute(q)).scalar()

        return {
            "total_transactions": total,
            "total_approved": approved,
            "total_rejected": total - approved,
            "total_failed": 0,
            "total_amount": total_amount,
            "face_count": face_count,
            "fingerprint_count": finger_count,
            "fallback_count": fallback_count,
        }
