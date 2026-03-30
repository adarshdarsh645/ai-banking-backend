import uuid
from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.api.deps import CurrentUser, DBSession
from app.schemas.transaction import (
    CSVImportResult,
    TransactionCreate,
    TransactionFilter,
    TransactionListResponse,
    TransactionResponse,
    TransactionRecategorize,
)
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=201,
    summary="Create a transaction",
)
async def create_transaction(
    payload: TransactionCreate,
    session: DBSession,
    current_user: CurrentUser,
) -> TransactionResponse:
    """Create a single transaction for a user-owned account."""
    service = TransactionService(session)
    return await service.create_transaction(payload, current_user.id)


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List transactions with filters and pagination",
)
async def list_transactions(
    session: DBSession,
    current_user: CurrentUser,
    account_id: uuid.UUID | None = Query(default=None),
    txn_type: str | None = Query(default=None, pattern="^(debit|credit)$"),
    date_from: str | None = Query(default=None, description="YYYY-MM-DD"),
    date_to: str | None = Query(default=None, description="YYYY-MM-DD"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> TransactionListResponse:
    """
    Return paginated transactions for the current/target user.

    - Filter by `account_id`, `txn_type` (debit|credit), `date_from`, `date_to`
    - Supports `page` and `page_size` parameters
    """
    target_user_id = user_id or current_user.id

    filters = TransactionFilter(
        account_id=account_id,
        txn_type=txn_type,  # type: ignore[arg-type]
        date_from=date.fromisoformat(date_from) if date_from else None,
        date_to=date.fromisoformat(date_to) if date_to else None,
        page=page,
        page_size=page_size,
    )
    service = TransactionService(session)
    return await service.list_transactions(filters, target_user_id)


@router.get(
    "/{txn_id}",
    response_model=TransactionResponse,
    summary="Get a specific transaction",
)
async def get_transaction(
    txn_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None)
) -> TransactionResponse:
    """Fetch a single transaction by ID, scoped to the user."""
    target_user_id = user_id or current_user.id
    service = TransactionService(session)
    return await service.get_transaction(txn_id, target_user_id)


@router.put(
    "/{txn_id}/category",
    response_model=TransactionResponse,
    summary="Recategorize a transaction",
)
async def recategorize_transaction(
    txn_id: uuid.UUID,
    payload: TransactionRecategorize,
    session: DBSession,
    current_user: CurrentUser,
) -> TransactionResponse:
    """
    Update a transaction's category, recalculate budgets, and optionally create a categorization rule.
    """
    service = TransactionService(session)
    return await service.recategorize_transaction(txn_id, payload, current_user.id)


@router.post(
    "/import",
    response_model=CSVImportResult,
    status_code=200,
    summary="Bulk import transactions from a CSV file",
)
async def import_csv(
    session: DBSession,
    current_user: CurrentUser,
    account_id: uuid.UUID = Form(..., description="Target account UUID"),
    file: UploadFile = File(..., description="CSV file with transaction rows"),
) -> CSVImportResult:
    """
    Upload a CSV file to bulk-import transactions into a user account.

    **Required CSV columns:** `description`, `amount`, `txn_type`, `txn_date`

    **Optional columns:** `category`, `currency`, `merchant`, `posted_date`

    Errors are reported per-row; valid rows are still imported.
    """
    content = await file.read()
    service = TransactionService(session)
    return await service.import_csv(account_id, current_user.id, content)
