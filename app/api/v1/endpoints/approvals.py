from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.core.database import get_db
from app.schemas.approval import ApprovalCreate, ApprovalDecision, ApprovalResponse
from app.schemas.auth import UserCreate
from app.services.approval_service import ApprovalService
from app.services.auth_service import AuthService
from app.dependencies import get_current_user, require_any_role

router = APIRouter()


@router.post("/")
async def create_approval(
    data: ApprovalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ApprovalService(db)
    approval = await service.create(data, requestor_id=current_user["sub"])
    return {"success": True, "data": ApprovalResponse.model_validate(approval)}


@router.get("/")
async def list_approvals(
    status: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = ApprovalService(db)
    approvals, total = await service.list(status=status, skip=skip, limit=limit)
    return {
        "success": True,
        "data": [ApprovalResponse.model_validate(a) for a in approvals],
        "total": total,
    }


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(
    approval_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ApprovalService(db)
    approval = await service.get_by_id(approval_id)
    return approval


@router.post("/{approval_id}/decide")
async def decide_approval(
    approval_id: str, data: ApprovalDecision,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin")),
):
    service = ApprovalService(db)
    approval = await service.decide(approval_id, data, approver_id=current_user["sub"])

    # If approved and it's a user creation request, auto-create the user
    if data.decision == "approved" and approval.request_type == "create_admin_ops" and approval.entity_data:
        user_data = UserCreate(**json.loads(approval.entity_data))
        auth_service = AuthService(db)
        await auth_service.register(user_data)

    return {"success": True, "data": ApprovalResponse.model_validate(approval)}
