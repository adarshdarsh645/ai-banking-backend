import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.budget_repository import BudgetRepository
from app.repositories.insights_repository import InsightsRepository
from app.schemas.insight import (
    BurnRateItem,
    BurnRateResponse,
    CashflowMonth,
    CashflowResponse,
    CategorySpend,
    CategorySpendResponse,
    MerchantSpend,
    TopMerchantsResponse,
)


class InsightsService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = InsightsRepository(session)
        self._budget_repo = BudgetRepository(session)

    async def get_cashflow(self, user_id: uuid.UUID) -> CashflowResponse:
        rows = await self._repo.get_cashflow_by_month(user_id)
        # Aggregate into (year, month) buckets
        buckets: dict[tuple, dict] = {}
        for row in rows:
            key = (int(row.year), int(row.month))
            if key not in buckets:
                buckets[key] = {"income": Decimal(0), "expense": Decimal(0)}
            if row.txn_type == "credit":
                buckets[key]["income"] += Decimal(str(row.total))
            else:
                buckets[key]["expense"] += Decimal(str(row.total))

        data = [
            CashflowMonth(year=k[0], month=k[1], income=v["income"], expense=v["expense"])
            for k, v in sorted(buckets.items())
        ]
        return CashflowResponse(data=data)

    async def get_top_merchants(self, user_id: uuid.UUID, limit: int = 10) -> TopMerchantsResponse:
        rows = await self._repo.get_top_merchants(user_id, limit)
        data = [
            MerchantSpend(merchant=r.merchant or "Unknown", total=Decimal(str(r.total)))
            for r in rows
        ]
        return TopMerchantsResponse(data=data)

    async def get_category_spend(self, user_id: uuid.UUID) -> CategorySpendResponse:
        rows = await self._repo.get_category_spend(user_id)
        data = [
            CategorySpend(category=r.category, total=Decimal(str(r.total)))
            for r in rows
        ]
        return CategorySpendResponse(data=data)

    async def get_burn_rate(self, user_id: uuid.UUID) -> BurnRateResponse:
        from datetime import date
        today = date.today()
        budgets = await self._budget_repo.get_user_budgets(user_id)
        
        # Pre-load category spend for current month ONLY (not all-time)
        spend_rows = await self._repo.get_category_spend_by_month(user_id, today.month, today.year)
        spend_map = {r.category: Decimal(str(r.total)) for r in spend_rows}

        data = []
        for b in budgets:
            if b.month != today.month or b.year != today.year:
                continue
            spent = spend_map.get(b.category, Decimal(0))
            limit = Decimal(str(b.amount_limit))
            pct = float(spent / limit * 100) if limit > 0 else 0.0
            data.append(BurnRateItem(
                category=b.category,
                budget_limit=limit,
                spent=spent,
                progress_pct=round(pct, 2),
            ))
        return BurnRateResponse(data=data)
