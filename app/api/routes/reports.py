import uuid
from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.report import ReportResponse, SpendingByCategory

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/spending-by-category",
    response_model=ReportResponse,
    summary="Get spending grouped by category",
)
async def spending_by_category(
    session: DBSession,
    current_user: CurrentUser,
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000),
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None)
) -> ReportResponse:
    target_user_id = user_id or current_user.id
    repo = TransactionRepository(session)
    rows = await repo.get_spending_by_category(target_user_id, month, year)
    
    spending = [
        SpendingByCategory(category=row[0], total_spent=row[1])
        for row in rows
    ]
    
    return ReportResponse(
        month=month,
        year=year,
        spending=spending,
    )
