import uuid
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.repositories.budget_repository import BudgetRepository
from app.schemas.budget import BudgetCreate, BudgetProgressResponse, BudgetResponse
from app.services.alert_service import AlertService


class BudgetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._repo = BudgetRepository(session)
        self._alert_service = AlertService(session)

    async def upsert_budget(self, user_id: uuid.UUID, data: BudgetCreate) -> BudgetResponse:
        budget = await self._repo.upsert_budget(
            user_id=user_id,
            category=data.category,
            amount_limit=data.amount_limit,
            month=data.month,
            year=data.year,
        )
        return BudgetResponse.model_validate(budget)

    async def get_budget_progress(self, user_id: uuid.UUID, category: str, month: int, year: int) -> BudgetProgressResponse | None:
        budget = await self._repo.get_budget(user_id, category, month, year)
        if not budget:
            return None

        spent = await self._calculate_spent(user_id, category, month, year)
        progress = float(spent / budget.amount_limit) * 100 if budget.amount_limit > 0 else 0.0

        return BudgetProgressResponse(
            budget=BudgetResponse.model_validate(budget),
            spent=spent,
            progress_percentage=round(progress, 2),
        )

    async def get_all_budgets_progress(self, user_id: uuid.UUID, month: int, year: int) -> list[BudgetProgressResponse]:
        budgets = await self._repo.get_user_budgets(user_id, month, year)
        results = []
        for b in budgets:
            spent = await self._calculate_spent(user_id, b.category, month, year)
            progress = float(spent / b.amount_limit) * 100 if b.amount_limit > 0 else 0.0
            results.append(
                BudgetProgressResponse(
                    budget=BudgetResponse.model_validate(b),
                    spent=spent,
                    progress_percentage=round(progress, 2),
                )
            )
        return results

    async def check_budget_and_alert(self, user_id: uuid.UUID, category: str, month: int, year: int) -> None:
        """Called when a transaction is added/updated to recalculate and alert."""
        budget = await self._repo.get_budget(user_id, category, month, year)
        if not budget:
            return

        spent = await self._calculate_spent(user_id, category, month, year)
        await self._alert_service.check_over_budget(
            user_id=user_id,
            category=category,
            month=month,
            year=year,
            limit=budget.amount_limit,
            spent=spent,
        )

    async def _calculate_spent(self, user_id: uuid.UUID, category: str, month: int, year: int) -> Decimal:
        stmt = (
            select(func.sum(Transaction.amount))
            .join(Account, Transaction.account_id == Account.id)
            .where(
                Account.user_id == user_id,
                Transaction.category == category,
                Transaction.txn_type == "debit",
                extract('month', Transaction.txn_date) == month,
                extract('year', Transaction.txn_date) == year,
            )
        )
        result = await self.session.execute(stmt)
        val = result.scalar()
        return Decimal(val) if val else Decimal("0.00")
