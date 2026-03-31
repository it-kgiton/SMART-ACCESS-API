from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransactionResponse(BaseModel):
    id: str
    merchant_id: str
    outlet_id: str
    device_id: str
    customer_id: Optional[str] = None
    wallet_id: Optional[str] = None
    biometric_method: str
    fallback_from: Optional[str] = None
    amount: float
    status: str
    confidence_score: Optional[float] = None
    request_reference: str
    rejection_reason: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int


class PaymentRequest(BaseModel):
    device_code: str
    amount: float
    biometric_method: str  # "face" or "fingerprint"
    request_reference: str
    fallback_from: Optional[str] = None


class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    customer_name: Optional[str] = None
    amount: float
    balance_after: Optional[float] = None
    biometric_method: str
    rejection_reason: Optional[str] = None
    confidence_score: Optional[float] = None


class TransactionStatsResponse(BaseModel):
    total_transactions: int
    total_approved: int
    total_rejected: int
    total_failed: int
    total_amount: float
    face_count: int
    fingerprint_count: int
    fallback_count: int
    period_start: datetime
    period_end: datetime
