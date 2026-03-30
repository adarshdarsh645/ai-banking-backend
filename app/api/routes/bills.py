import uuid
from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.services.bill_service import BillService

router = APIRouter(prefix="/bills", tags=["Bills"])


@router.post(
    "",
    response_model=BillResponse,
    status_code=201,
    summary="Create a new bill",
)
async def create_bill(
    payload: BillCreate, session: DBSession, current_user: CurrentUser
) -> BillResponse:
    service = BillService(session)
    return await service.create_bill(current_user.id, payload)


@router.get(
    "",
    response_model=list[BillResponse],
    summary="List all bills for user",
)
async def list_bills(
    session: DBSession, current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> list[BillResponse]:
    target_user_id = user_id or current_user.id
    service = BillService(session)
    return await service.get_user_bills(target_user_id)


@router.put(
    "/{bill_id}",
    response_model=BillResponse,
    summary="Update a bill",
)
async def update_bill(
    bill_id: uuid.UUID,
    payload: BillUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> BillResponse:
    service = BillService(session)
    return await service.update_bill(bill_id, current_user.id, payload)


@router.delete(
    "/{bill_id}",
    status_code=204,
    summary="Delete a bill",
)
async def delete_bill(
    bill_id: uuid.UUID, session: DBSession, current_user: CurrentUser
) -> None:
    service = BillService(session)
    await service.delete_bill(bill_id, current_user.id)
