import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reward import Reward
from app.repositories.base import BaseRepository


class RewardRepository(BaseRepository[Reward]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Reward, session)

    async def get_user_rewards(self, user_id: uuid.UUID) -> Sequence[Reward]:
        stmt = select(Reward).where(Reward.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_reward(self, reward_id: uuid.UUID, user_id: uuid.UUID) -> Reward | None:
        stmt = select(Reward).where(Reward.id == reward_id, Reward.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
