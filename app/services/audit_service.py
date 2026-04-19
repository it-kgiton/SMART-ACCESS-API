from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog, AuditEventType, AuditResult


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        event_type: str,
        action: str,
        actor_id: Optional[str] = None,
        actor_role: Optional[str] = None,
        target_id: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None,
        result: str = "success",
        school_id: Optional[str] = None,
    ) -> AuditLog:
        entry = AuditLog(
            event_type=event_type,
            actor_id=actor_id,
            actor_role=actor_role,
            target_id=target_id,
            action=action,
            details=details,
            ip_address=ip_address,
            device_info=device_info,
            result=result,
            school_id=school_id,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def list(
        self, event_type: Optional[str] = None, actor_id: Optional[str] = None,
        school_id: Optional[str] = None, skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        if event_type:
            query = query.where(AuditLog.event_type == event_type)
            count_query = count_query.where(AuditLog.event_type == event_type)
        if actor_id:
            query = query.where(AuditLog.actor_id == actor_id)
            count_query = count_query.where(AuditLog.actor_id == actor_id)
        if school_id:
            query = query.where(AuditLog.school_id == school_id)
            count_query = count_query.where(AuditLog.school_id == school_id)

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(AuditLog.timestamp.desc())
        )
        return result.scalars().all(), total
