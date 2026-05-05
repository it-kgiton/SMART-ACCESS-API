from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    merchant_id: str
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Decimal = Field(..., ge=100)
    cost_price: Optional[Decimal] = None
    category: Optional[str] = "lainnya"
    image_url: Optional[str] = None
    is_available: bool = True
    stock_quantity: Optional[int] = None
    min_stock: Optional[int] = None
    stock_alert_threshold: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    stock_quantity: Optional[int] = None
    min_stock: Optional[int] = None
    stock_alert_threshold: Optional[int] = None


class ProductResponse(BaseModel):
    id: str
    merchant_id: str
    name: str
    description: Optional[str]
    sku: Optional[str]
    price: float
    cost_price: Optional[float]
    category: str
    image_url: Optional[str]
    is_available: bool
    stock_quantity: Optional[int]
    min_stock: Optional[int]
    stock_alert_threshold: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    success: bool = True
    data: List[ProductResponse]
    total: int
