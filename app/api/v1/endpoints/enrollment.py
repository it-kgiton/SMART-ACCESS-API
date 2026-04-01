from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException
from app.schemas.enrollment import (
    FaceEnrollmentResponse,
    FingerprintEnrollmentResponse,
    EnrollmentStatusResponse,
    FaceVerifyResponse,
)
from app.services.enrollment_service import EnrollmentService
from app.services.customer_service import CustomerService
from app.dependencies import (
    get_current_user,
    require_any_role,
    is_merchant_admin,
    get_user_merchant_id,
)

router = APIRouter()


async def _check_customer_access(customer_id: str, current_user: dict, db: AsyncSession):
    """Verify merchant_admin can only access their own merchant's customers."""
    if is_merchant_admin(current_user):
        service = CustomerService(db)
        customer = await service.get_by_id(customer_id)
        if not customer:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Customer")
        user_merchant_id = get_user_merchant_id(current_user)
        if customer.merchant_id != user_merchant_id:
            raise ForbiddenException("You can only manage enrollment for your own customers")


@router.post("/face/{customer_id}", response_model=FaceEnrollmentResponse)
async def enroll_face(
    customer_id: str,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    await _check_customer_access(customer_id, current_user, db)

    image_bytes = await image.read()
    service = EnrollmentService(db)
    credential = await service.enroll_face(
        customer_id, image_bytes, enrolled_by=current_user.get("sub")
    )
    return FaceEnrollmentResponse(
        credential_id=credential.id,
        customer_id=credential.customer_id,
        quality_score=credential.quality_score,
        status=credential.status,
        enrolled_at=credential.enrolled_at,
    )


@router.post("/fingerprint/{customer_id}", response_model=FingerprintEnrollmentResponse)
async def enroll_fingerprint(
    customer_id: str,
    template: UploadFile = File(...),
    finger_index: int = Form(1),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    await _check_customer_access(customer_id, current_user, db)

    template_data = await template.read()
    service = EnrollmentService(db)
    credential = await service.enroll_fingerprint(
        customer_id,
        template_data,
        finger_index=finger_index,
        enrolled_by=current_user.get("sub"),
    )
    return FingerprintEnrollmentResponse(
        credential_id=credential.id,
        customer_id=credential.customer_id,
        finger_index=credential.finger_index,
        quality_score=credential.quality_score,
        status=credential.status,
        enrolled_at=credential.enrolled_at,
    )


@router.get("/status/{customer_id}", response_model=EnrollmentStatusResponse)
async def get_enrollment_status(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    await _check_customer_access(customer_id, current_user, db)

    service = EnrollmentService(db)
    status = await service.get_enrollment_status(customer_id)
    return status


@router.post("/face/{customer_id}/revoke")
async def revoke_face(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    await _check_customer_access(customer_id, current_user, db)

    service = EnrollmentService(db)
    success = await service.revoke_face(customer_id)
    if not success:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Face credential")
    return {"message": "Face credential revoked"}


@router.post("/fingerprint/{customer_id}/revoke")
async def revoke_fingerprint(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    await _check_customer_access(customer_id, current_user, db)

    service = EnrollmentService(db)
    success = await service.revoke_fingerprint(customer_id)
    if not success:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Fingerprint credential")
    return {"message": "Fingerprint credential revoked"}


@router.post("/face/{customer_id}/verify", response_model=FaceVerifyResponse)
async def verify_face(
    customer_id: str,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("platform_admin", "merchant_admin")),
):
    """Verify a face image against a customer's enrolled face credential.
    Returns similarity score, match result, and quality assessment."""
    await _check_customer_access(customer_id, current_user, db)

    image_bytes = await image.read()
    service = EnrollmentService(db)
    result = await service.verify_face(customer_id, image_bytes)
    return FaceVerifyResponse(**result)
