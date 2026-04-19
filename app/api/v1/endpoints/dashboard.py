from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.dashboard import AuditLogResponse
from app.services.dashboard_service import DashboardService
from app.services.audit_service import AuditService
from app.dependencies import get_current_user, require_any_role

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    school_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub", "admin_ops")),
):
    service = DashboardService(db)
    stats = await service.get_stats(school_id=school_id)
    return {"success": True, "data": stats}


@router.get("/audit-logs")
async def list_audit_logs(
    event_type: Optional[str] = None,
    actor_id: Optional[str] = None,
    school_id: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_any_role("super_admin", "admin_hub")),
):
    service = AuditService(db)
    logs, total = await service.list(
        event_type=event_type, actor_id=actor_id,
        school_id=school_id, skip=skip, limit=limit,
    )
    return {
        "success": True,
        "data": [AuditLogResponse.model_validate(log) for log in logs],
        "total": total,
    }
