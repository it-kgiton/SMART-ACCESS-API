from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import ApprovalRequest, ApprovalStatus
from app.schemas.approval import ApprovalCreate, ApprovalDecision
from app.core.exceptions import NotFoundException, BadRequestException


class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ApprovalCreate, requestor_id: str) -> ApprovalRequest:
        approval = ApprovalRequest(
            request_type=data.request_type,
            requestor_id=requestor_id,
            entity_type=data.entity_type,
            entity_data=data.entity_data,
        )
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def get_by_id(self, approval_id: str) -> Optional[ApprovalRequest]:
        result = await self.db.execute(
            select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, status: Optional[str] = None, skip: int = 0, limit: int = 50,
    ) -> tuple:
        query = select(ApprovalRequest)
        count_query = select(func.count(ApprovalRequest.id))

        if status:
            query = query.where(ApprovalRequest.status == status)
            count_query = count_query.where(ApprovalRequest.status == status)

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.offset(skip).limit(limit).order_by(ApprovalRequest.requested_at.desc())
        )
        return result.scalars().all(), total

    async def decide(
        self, approval_id: str, data: ApprovalDecision, approver_id: str
    ) -> ApprovalRequest:
        approval = await self.get_by_id(approval_id)
        if not approval:
            raise NotFoundException("Approval request")
        if approval.status != ApprovalStatus.PENDING:
            raise BadRequestException("Approval request is not pending")

        approval.status = data.decision
        approval.approver_id = approver_id
        approval.decided_at = datetime.now(timezone.utc)
        approval.decision_note = data.decision_note
        await self.db.commit()
        await self.db.refresh(approval)
        return approval
