import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.reward_repository import RewardRepository
from app.schemas.reward import RewardResponse, RewardUpdate


class RewardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._repo = RewardRepository(session)

    async def get_user_rewards(self, user_id: uuid.UUID) -> list[RewardResponse]:
        rewards = await self._repo.get_user_rewards(user_id)
        return [RewardResponse.model_validate(r) for r in rewards]

    async def update_reward(
        self, reward_id: uuid.UUID, user_id: uuid.UUID, data: RewardUpdate
    ) -> RewardResponse:
        reward = await self._repo.get_reward(reward_id, user_id)
        if not reward:
            raise NotFoundError("Reward")

        reward = await self._repo.update(reward, points_balance=data.points_balance)
        return RewardResponse.model_validate(reward)
