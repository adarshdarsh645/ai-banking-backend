import uuid
from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.reward import RewardResponse, RewardUpdate
from app.services.reward_service import RewardService

router = APIRouter(prefix="/rewards", tags=["Rewards"])


@router.get(
    "",
    response_model=list[RewardResponse],
    summary="Get user rewards points balances",
)
async def list_rewards(
    session: DBSession, current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> list[RewardResponse]:
    target_user_id = user_id or current_user.id
    service = RewardService(session)
    return await service.get_user_rewards(target_user_id)


@router.put(
    "/{reward_id}",
    response_model=RewardResponse,
    summary="Update reward points",
)
async def update_reward(
    reward_id: uuid.UUID,
    payload: RewardUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> RewardResponse:
    service = RewardService(session)
    return await service.update_reward(reward_id, current_user.id, payload)
