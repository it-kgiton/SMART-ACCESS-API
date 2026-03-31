from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transaction import PaymentResponse
from app.services.transaction_service import TransactionService
from app.dependencies import get_current_device

router = APIRouter()


@router.post("/face-payment", response_model=PaymentResponse)
async def face_payment(
    image: UploadFile = File(...),
    amount: float = Form(...),
    request_reference: str = Form(...),
    fallback_from: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    device: dict = Depends(get_current_device),
):
    """Device-facing endpoint for face-based payment."""
    image_bytes = await image.read()
    service = TransactionService(db)
    result = await service.process_face_payment(
        device_id=device["sub"],
        image_bytes=image_bytes,
        amount=amount,
        request_reference=request_reference,
        fallback_from=fallback_from,
    )
    return result


@router.post("/fingerprint-payment", response_model=PaymentResponse)
async def fingerprint_payment(
    template: UploadFile = File(...),
    amount: float = Form(...),
    request_reference: str = Form(...),
    fallback_from: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    device: dict = Depends(get_current_device),
):
    """Device-facing endpoint for fingerprint-based payment."""
    template_data = await template.read()
    service = TransactionService(db)
    result = await service.process_fingerprint_payment(
        device_id=device["sub"],
        fingerprint_data=template_data,
        amount=amount,
        request_reference=request_reference,
        fallback_from=fallback_from,
    )
    return result
