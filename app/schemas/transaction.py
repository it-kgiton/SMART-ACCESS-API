from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TransactionItemResponse(BaseModel):
    id: str
    product_id: Optional[str]
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float

    model_config = {"from_attributes": True}


class TransactionResponse(BaseModel):
    id: str
    transaction_ref: str
    type: str
    client_id: Optional[str] = None
    merchant_id: Optional[str] = None
    parent_id: Optional[str] = None
    school_id: Optional[str] = None
    device_id: Optional[str] = None
    amount: float
    fee_amount: float
    status: str
    payment_method: Optional[str] = None
    biometric_method: Optional[str] = None
    confidence_score: Optional[float] = None
    offline_flag: bool = False
    rejection_reason: Optional[str] = None
    reference_transaction_id: Optional[str] = None
    items: List[TransactionItemResponse] = []
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    success: bool = True
    data: List[TransactionResponse]
    total: int


class PurchaseItemRequest(BaseModel):
    product_id: Optional[str] = None
    product_name: str
    quantity: int = 1
    unit_price: float


class PurchaseRequest(BaseModel):
    merchant_id: str
    client_id: str
    device_id: Optional[str] = None
    items: List[PurchaseItemRequest]
    biometric_method: Optional[str] = "fingerprint_face"


class TopUpRequest(BaseModel):
    client_id: str
    parent_id: str
    amount: float
    payment_method: str = "qris"


class RefundRequest(BaseModel):
    transaction_id: str
    reason: Optional[str] = None


class PaymentResponse(BaseModel):
    success: bool = True
    data: dict


class TransactionStatsResponse(BaseModel):
    total_transactions: int
    total_success: int
    total_failed: int
    total_refunded: int
    total_amount: float
    total_fee: float
    period_start: datetime
    period_end: datetime
