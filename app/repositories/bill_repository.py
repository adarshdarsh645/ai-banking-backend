import uuid
from typing import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill import Bill
from app.repositories.base import BaseRepository


class BillRepository(BaseRepository[Bill]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Bill, session)

    async def get_user_bills(self, user_id: uuid.UUID) -> Sequence[Bill]:
        stmt = select(Bill).where(Bill.user_id == user_id).order_by(Bill.due_date)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_bill(self, bill_id: uuid.UUID, user_id: uuid.UUID) -> Bill | None:
        stmt = select(Bill).where(Bill.id == bill_id, Bill.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_upcoming_bills_for_all_users(self, max_due_date: date) -> Sequence[Bill]:
        """Fetch bills due on or before `max_due_date` that are not yet paid."""
        stmt = select(Bill).where(Bill.due_date <= max_due_date, Bill.status != "paid")
        result = await self.session.execute(stmt)
        return result.scalars().all()
