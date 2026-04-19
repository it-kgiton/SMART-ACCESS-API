from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/")
async def list_notifications(
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = NotificationService(db)
    result = await service.list_for_user(current_user["id"], skip=skip, limit=limit)
    return {
        "success": True,
        "data": [NotificationResponse.model_validate(n) for n in result["items"]],
        "total": result["total"],
        "unread_count": result["unread_count"],
    }


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = NotificationService(db)
    await service.mark_read(notification_id)
    return {"success": True, "message": "Notification marked as read"}


@router.post("/read-all")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = NotificationService(db)
    await service.mark_all_read(current_user["id"])
    return {"success": True, "message": "All notifications marked as read"}
