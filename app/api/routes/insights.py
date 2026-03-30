import uuid
from typing import Any
from datetime import date

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DBSession
from app.schemas.insight import (
    BurnRateResponse,
    CashflowResponse,
    CategorySpendResponse,
    TopMerchantsResponse,
)
from app.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get(
    "/cashflow",
    response_model=CashflowResponse,
    summary="Income vs expense per month",
)
async def get_cashflow(
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> CashflowResponse:
    target_user_id = user_id or current_user.id
    return await InsightsService(session).get_cashflow(target_user_id)


@router.get(
    "/top-merchants",
    response_model=TopMerchantsResponse,
    summary="Top merchants by total spend",
)
async def get_top_merchants(
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> TopMerchantsResponse:
    target_user_id = user_id or current_user.id
    return await InsightsService(session).get_top_merchants(target_user_id)


@router.get(
    "/category-spend",
    response_model=CategorySpendResponse,
    summary="Spend grouped by category",
)
async def get_category_spend(
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> CategorySpendResponse:
    target_user_id = user_id or current_user.id
    return await InsightsService(session).get_category_spend(target_user_id)


@router.get(
    "/burn-rate",
    response_model=BurnRateResponse,
    summary="Current month spend vs budget limits",
)
async def get_burn_rate(
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> BurnRateResponse:
    target_user_id = user_id or current_user.id
    return await InsightsService(session).get_burn_rate(target_user_id)
