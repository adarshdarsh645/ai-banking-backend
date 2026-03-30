import uuid
from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.alert import AlertResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get(
    "",
    response_model=list[AlertResponse],
    summary="List all user alerts (latest first)",
)
async def list_alerts(
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> list[AlertResponse]:
    target_user_id = user_id or current_user.id
    service = AlertService(session)
    return [AlertResponse.model_validate(a) for a in await service.get_user_alerts(target_user_id)]


@router.get(
    "/unread",
    response_model=list[AlertResponse],
    summary="List unread alerts only",
)
async def list_unread_alerts(
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> list[AlertResponse]:
    target_user_id = user_id or current_user.id
    service = AlertService(session)
    return [AlertResponse.model_validate(a) for a in await service.get_unread_alerts(target_user_id)]


@router.post(
    "/mark-read",
    summary="Mark selected alerts as read",
)
async def mark_alerts_read(
    alert_ids: list[uuid.UUID],
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None)
) -> dict:
    target_user_id = user_id or current_user.id
    service = AlertService(session)
    count = await service.mark_alerts_read(target_user_id, alert_ids)
    return {"marked_read": count}
