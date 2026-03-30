import io
import uuid
from datetime import date

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.api.deps import CurrentUser, DBSession
from app.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["Export"])


@router.get(
    "/transactions",
    summary="Export all transactions as CSV",
    response_class=Response,
)
async def export_transactions_csv(
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    format: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> Response:
    target_user_id = user_id or current_user.id
    svc = ExportService(session)
    data = await svc.export_transactions_csv(target_user_id)
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.get(
    "/insights",
    summary="Export insights report as PDF (or plain text fallback)",
    response_class=Response,
)
async def export_insights_pdf(
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    format: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> Response:
    target_user_id = user_id or current_user.id
    svc = ExportService(session)
    data = await svc.export_insights_pdf(target_user_id)

    # Detect if reportlab was available (PDF starts with %PDF)
    if data[:4] == b"%PDF":
        media_type = "application/pdf"
        filename = "insights.pdf"
    else:
        media_type = "text/plain"
        filename = "insights.txt"

    return Response(
        content=data,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
