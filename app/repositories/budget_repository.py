import uuid
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Budget, session)

    async def get_user_budgets(
        self, user_id: uuid.UUID, month: int | None = None, year: int | None = None
    ) -> Sequence[Budget]:
        stmt = select(Budget).where(Budget.user_id == user_id)
        if month is not None:
            stmt = stmt.where(Budget.month == month)
        if year is not None:
            stmt = stmt.where(Budget.year == year)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_budget(
        self, user_id: uuid.UUID, category: str, month: int, year: int
    ) -> Budget | None:
        stmt = select(Budget).where(
            Budget.user_id == user_id,
            Budget.category == category,
            Budget.month == month,
            Budget.year == year,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_budget(
        self, user_id: uuid.UUID, category: str, amount_limit: Decimal, month: int, year: int
    ) -> Budget:
        budget = await self.get_budget(user_id, category, month, year)
        if budget:
            budget.amount_limit = amount_limit
            await self.session.flush()
            return budget
        
        return await self.create(
            user_id=user_id,
            category=category,
            amount_limit=amount_limit,
            month=month,
            year=year,
        )
