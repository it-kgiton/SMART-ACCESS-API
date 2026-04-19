from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.schemas.enrollment import (
    FaceEnrollmentResponse,
    FingerprintEnrollmentResponse,
    EnrollmentStatusResponse,
)
from app.services.enrollment_service import EnrollmentService
from app.dependencies import get_current_user, require_any_role

router = APIRouter()


@router.post("/face/{client_id}", response_model=FaceEnrollmentResponse)
async def enroll_face(
    client_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = EnrollmentService(db)
    image_bytes = await file.read()
    result = await service.enroll_face(client_id, image_bytes)
    return result


@router.post("/fingerprint/{client_id}", response_model=FingerprintEnrollmentResponse)
async def enroll_fingerprint(
    client_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = EnrollmentService(db)
    template_bytes = await file.read()
    result = await service.enroll_fingerprint(client_id, template_bytes)
    return result


@router.delete("/face/{client_id}")
async def revoke_face(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = EnrollmentService(db)
    await service.revoke_face(client_id)
    return {"success": True, "message": "Face credential revoked"}


@router.delete("/fingerprint/{client_id}")
async def revoke_fingerprint(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = EnrollmentService(db)
    await service.revoke_fingerprint(client_id)
    return {"success": True, "message": "Fingerprint credential revoked"}


@router.get("/status/{client_id}", response_model=EnrollmentStatusResponse)
async def get_enrollment_status(
    client_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = EnrollmentService(db)
    status = await service.get_status(client_id)
    if not status:
        raise NotFoundException("Client")
    return status
