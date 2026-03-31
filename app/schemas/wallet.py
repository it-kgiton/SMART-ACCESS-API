from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class WalletResponse(BaseModel):
    id: str
    customer_id: str
    balance: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WalletTopUp(BaseModel):
    customer_id: str
    amount: float
    description: Optional[str] = None


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
    items: list[WalletLedgerResponse]
    total: int
    page: int
    page_size: int
