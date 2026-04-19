from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.client import Client
from app.models.merchant import Merchant
from app.models.parent import Parent
from app.models.device import Device, DeviceStatus
from app.models.transaction import Transaction, TransactionStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.approval import ApprovalRequest, ApprovalStatus


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self, school_id: Optional[str] = None) -> dict:
        # Total transactions
        q = select(func.count(Transaction.id))
        if school_id:
            q = q.where(Transaction.school_id == school_id)
        total_txn = (await self.db.execute(q)).scalar() or 0

        # Total amount
        q = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.status == TransactionStatus.SUCCESS
        )
        if school_id:
            q = q.where(Transaction.school_id == school_id)
        total_amount = float((await self.db.execute(q)).scalar())

        # Users
        total_users = (await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )).scalar() or 0

        # Merchants
        q = select(func.count(Merchant.id))
        if school_id:
            q = q.where(Merchant.school_id == school_id)
        total_merchants = (await self.db.execute(q)).scalar() or 0

        # Clients
        q = select(func.count(Client.id))
        if school_id:
            q = q.where(Client.school_id == school_id)
        total_clients = (await self.db.execute(q)).scalar() or 0

        # Parents
        q = select(func.count(Parent.id))
        if school_id:
            q = q.where(Parent.school_id == school_id)
        total_parents = (await self.db.execute(q)).scalar() or 0

        # Active devices
        q = select(func.count(Device.id)).where(Device.status == DeviceStatus.ACTIVE)
        if school_id:
            q = q.where(Device.school_id == school_id)
        active_devices = (await self.db.execute(q)).scalar() or 0

        # Pending approvals
        pending_approvals = (await self.db.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.status == ApprovalStatus.PENDING
            )
        )).scalar() or 0

        # Open tickets
        q = select(func.count(Ticket.id)).where(
            Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
        )
        if school_id:
            q = q.where(Ticket.school_id == school_id)
        open_tickets = (await self.db.execute(q)).scalar() or 0

        # Enrollment rate
        enrolled = (await self.db.execute(
            select(func.count(Client.id)).where(Client.biometric_enrolled == True)
        )).scalar() or 0
        enrollment_rate = (enrolled / total_clients * 100) if total_clients > 0 else 0

        return {
            "total_transactions": total_txn,
            "total_transaction_amount": total_amount,
            "total_users": total_users,
            "total_merchants": total_merchants,
            "total_clients": total_clients,
            "total_parents": total_parents,
            "active_devices": active_devices,
            "pending_approvals": pending_approvals,
            "open_tickets": open_tickets,
            "enrollment_rate": round(enrollment_rate, 1),
        }
