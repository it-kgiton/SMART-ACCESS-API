from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType
from app.core.exceptions import NotFoundException


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, recipient_user_id: str, notification_type: str,
        title: str, message: str,
        reference_type: Optional[str] = None, reference_id: Optional[str] = None,
    ) -> Notification:
        notification = Notification(
            recipient_user_id=recipient_user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def list_for_user(
        self, user_id: str, skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(Notification).where(
            Notification.recipient_user_id == user_id
        )
        count_query = select(func.count(Notification.id)).where(
            Notification.recipient_user_id == user_id
        )
        unread_query = select(func.count(Notification.id)).where(
            Notification.recipient_user_id == user_id,
            Notification.is_read == False,
        )

        total = (await self.db.execute(count_query)).scalar()
        unread_count = (await self.db.execute(unread_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
        )
        return result.scalars().all(), total, unread_count

    async def mark_read(self, notification_id: str, user_id: str) -> Notification:
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.recipient_user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise NotFoundException("Notification")
        notification.is_read = True
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_all_read(self, user_id: str):
        from sqlalchemy import update as sql_update
        await self.db.execute(
            sql_update(Notification)
            .where(
                Notification.recipient_user_id == user_id,
                Notification.is_read == False,
            )
            .values(is_read=True)
        )
        await self.db.commit()
