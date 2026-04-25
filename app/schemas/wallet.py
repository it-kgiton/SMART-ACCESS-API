from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class WalletResponse(BaseModel):
    id: str
    client_id: str
    balance: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WalletTopUp(BaseModel):
    client_id: str
    amount: float
    description: Optional[str] = None
    payment_method: Optional[str] = "qris"


class WalletLedgerResponse(BaseModel):
    id: str
    wallet_id: str
    type: str
    amount: float
    balance_before: float
    balance_after: float
    reference_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WalletLedgerListResponse(BaseModel):
    success: bool = True
    data: List[WalletLedgerResponse]
    total: int
