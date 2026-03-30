import uuid
from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.account import AccountCreate, AccountListResponse, AccountResponse
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post(
    "",
    response_model=AccountResponse,
    status_code=201,
    summary="Link a new bank account",
)
async def create_account(
    payload: AccountCreate,
    session: DBSession,
    current_user: CurrentUser,
) -> AccountResponse:
    """Add a new linked bank account for the authenticated user."""
    service = AccountService(session)
    return await service.create_account(payload, current_user.id)


@router.get(
    "",
    response_model=AccountListResponse,
    summary="List all accounts for current user",
)
async def list_accounts(
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    month: int | None = Query(None),
    year: int | None = Query(None)
) -> AccountListResponse:
    """Return all bank accounts belonging to the authenticated user."""
    target_user_id = user_id or current_user.id
    service = AccountService(session)
    return await service.list_accounts(target_user_id)


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Get a specific account",
)
async def get_account(
    account_id: uuid.UUID,
    session: DBSession,
    current_user: CurrentUser,
    user_id: uuid.UUID | None = Query(None)
) -> AccountResponse:
    """Fetch a single account by ID, scoped to the authenticated user."""
    target_user_id = user_id or current_user.id
    service = AccountService(session)
    return await service.get_account(account_id, target_user_id)
