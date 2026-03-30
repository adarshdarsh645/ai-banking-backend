"""
background_tasks.py — Periodic background checks for budgets and balances.
Runs inside app lifespan alongside the bill_reminder_job.
"""
import asyncio
from decimal import Decimal

from app.db.database import AsyncSessionLocal
from app.services.alert_service import AlertService
from app.repositories.insights_repository import InsightsRepository
from app.repositories.budget_repository import BudgetRepository
from app.repositories.user_repository import UserRepository


async def budget_and_balance_check_job() -> None:
    """
    Runs every 6 hours.
    - Checks each user's account balances → low_balance alerts
    - Checks each user's active budgets vs spending → budget_exceeded alerts
    """
    while True:
        try:
            async with AsyncSessionLocal() as session:
                alert_service = AlertService(session)
                insights_repo = InsightsRepository(session)
                budget_repo = BudgetRepository(session)
                user_repo = UserRepository(session)

                users = await user_repo.get_all_users()

                for user in users:
                    # 1. Low balance check
                    accounts = await insights_repo.get_user_accounts_balance(user.id)
                    for account in accounts:
                        balance = Decimal(str(account.balance))
                        if balance < Decimal("100"):
                            await alert_service.check_low_balance(
                                user_id=user.id,
                                account_id=account.id,
                                balance=balance,
                            )

                    # 2. Budget exceeded check
                    from datetime import date
                    today = date.today()
                    budgets = await budget_repo.get_user_budgets(
                        user.id, month=today.month, year=today.year
                    )
                    category_spend = await insights_repo.get_category_spend(user.id)
                    spend_map = {r.category: Decimal(str(r.total)) for r in category_spend}

                    for budget in budgets:
                        spent = spend_map.get(budget.category, Decimal("0"))
                        limit = Decimal(str(budget.amount_limit))
                        await alert_service.check_over_budget(
                            user_id=user.id,
                            category=budget.category,
                            month=today.month,
                            year=today.year,
                            limit=limit,
                            spent=spent,
                        )

                await session.commit()
        except Exception:
            pass  # Fail gracefully

        await asyncio.sleep(6 * 3600)  # every 6 hours
