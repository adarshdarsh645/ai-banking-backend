import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Alert, session)

    async def get_user_alerts(self, user_id: uuid.UUID) -> Sequence[Alert]:
        stmt = select(Alert).where(Alert.user_id == user_id).order_by(Alert.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_unread_alerts(self, user_id: uuid.UUID) -> Sequence[Alert]:
        stmt = (
            select(Alert)
            .where(Alert.user_id == user_id, Alert.is_read == False)  # noqa: E712
            .order_by(Alert.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def mark_alerts_read(self, user_id: uuid.UUID, alert_ids: list[uuid.UUID]) -> int:
        from sqlalchemy import update
        stmt = (
            update(Alert)
            .where(Alert.user_id == user_id, Alert.id.in_(alert_ids))
            .values(is_read=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_alert_by_id(self, alert_id: uuid.UUID, user_id: uuid.UUID) -> Alert | None:
        stmt = select(Alert).where(Alert.id == alert_id, Alert.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_alert(
        self, user_id: uuid.UUID, alert_type: str, category: str, month: int, year: int
    ) -> Alert | None:
        stmt = select(Alert).where(
            Alert.user_id == user_id,
            Alert.alert_type == alert_type,
            Alert.category == category,
            Alert.month == month,
            Alert.year == year,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_alert_if_not_exists(
        self, user_id: uuid.UUID, alert_type: str, message: str, category: str, month: int, year: int
    ) -> Alert | None:
        existing = await self.get_alert(user_id, alert_type, category, month, year)
        if existing:
            return None  # duplicate prevention
            
        return await self.create(
            user_id=user_id,
            alert_type=alert_type,
            message=message,
            category=category,
            month=month,
            year=year,
        )
