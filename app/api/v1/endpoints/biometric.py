from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transaction import TransactionResponse
from app.services.transaction_service import TransactionService
from app.services.enrollment_service import EnrollmentService
from app.dependencies import get_current_device, require_any_role

router = APIRouter()


@router.post("/face-identify")
async def face_identify(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops", "merchant")),
):
    """Identify a client by face photo (1:N search). Used in POS biometric checkout."""
    service = EnrollmentService(db)
    image_bytes = await file.read()
    result = await service.identify_face(image_bytes)
    return {"success": True, "data": result}


@router.post("/face-payment")
async def face_payment(
    device_serial: str = Form(...),
    merchant_id: str = Form(...),
    amount: float = Form(...),
    file: UploadFile = File(...),
    items: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    device: dict = Depends(get_current_device),
):
    service = TransactionService(db)
    image_bytes = await file.read()
    transaction = await service.process_face_payment(
        device_serial=device_serial,
        merchant_id=merchant_id,
        amount=amount,
        image_bytes=image_bytes,
        items_json=items,
    )
    return {"success": True, "data": TransactionResponse.model_validate(transaction)}


@router.post("/fingerprint-payment")
async def fingerprint_payment(
    device_serial: str = Form(...),
    merchant_id: str = Form(...),
    amount: float = Form(...),
    file: UploadFile = File(...),
    items: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    device: dict = Depends(get_current_device),
):
    service = TransactionService(db)
    template_bytes = await file.read()
    transaction = await service.process_fingerprint_payment(
        device_serial=device_serial,
        merchant_id=merchant_id,
        amount=amount,
        template_bytes=template_bytes,
        items_json=items,
    )
    return {"success": True, "data": TransactionResponse.model_validate(transaction)}
