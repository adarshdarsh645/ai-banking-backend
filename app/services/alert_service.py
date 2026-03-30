import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.repositories.alert_repository import AlertRepository


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._repo = AlertRepository(session)

    async def check_over_budget(
        self, user_id: uuid.UUID, category: str, month: int, year: int, limit: Decimal, spent: Decimal
    ) -> Alert | None:
        """Trigger an alert if spending exceeds the budget threshold."""
        if spent > limit:
            message = f"Budget exceeded for {category} in {month}/{year}. Limit: {limit}, Spent: {spent}."
            return await self._repo.create_alert_if_not_exists(
                user_id=user_id,
                alert_type="budget_exceeded",
                message=message,
                category=category,
                month=month,
                year=year,
            )
        return None

    async def check_low_balance(
        self, user_id: uuid.UUID, account_id: uuid.UUID, balance: Decimal, threshold: Decimal = Decimal("100")
    ) -> Alert | None:
        """Trigger an alert when account balance falls below threshold."""
        if balance < threshold:
            from datetime import date
            today = date.today()
            message = f"Low balance warning: Your account balance is {balance}, below threshold of {threshold}."
            return await self._repo.create_alert_if_not_exists(
                user_id=user_id,
                alert_type="low_balance",
                message=message,
                category=str(account_id),
                month=today.month,
                year=today.year,
            )
        return None

    async def get_user_alerts(self, user_id: uuid.UUID) -> list[Alert]:
        return list(await self._repo.get_user_alerts(user_id))

    async def get_unread_alerts(self, user_id: uuid.UUID) -> list[Alert]:
        return list(await self._repo.get_unread_alerts(user_id))

    async def mark_alerts_read(self, user_id: uuid.UUID, alert_ids: list[uuid.UUID]) -> int:
        count = await self._repo.mark_alerts_read(user_id, alert_ids)
        await self.session.flush()
        return count
