import uuid
from datetime import date
import datetime

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.budget import BudgetCreate, BudgetProgressResponse, BudgetResponse
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post(
    "",
    response_model=BudgetResponse,
    status_code=201,
    summary="Create or update a monthly budget",
)
async def upsert_budget(
    payload: BudgetCreate,
    session: DBSession,
    current_user: CurrentUser,
) -> BudgetResponse:
    service = BudgetService(session)
    return await service.upsert_budget(current_user.id, payload)


@router.get(
    "",
    response_model=list[BudgetProgressResponse],
    summary="List budget progress for a specific month/year",
)
async def list_budgets(
    session: DBSession,
    current_user: CurrentUser,
    month: int = Query(default_factory=lambda: datetime.datetime.now().month, ge=1, le=12),
    year: int = Query(default_factory=lambda: datetime.datetime.now().year, ge=2000),
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None)
) -> list[BudgetProgressResponse]:
    target_user_id = user_id or current_user.id
    service = BudgetService(session)
    return await service.get_all_budgets_progress(target_user_id, month, year)
