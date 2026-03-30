import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate, AccountListResponse, AccountResponse


class AccountService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = AccountRepository(session)

    async def create_account(
        self, data: AccountCreate, user_id: uuid.UUID
    ) -> AccountResponse:
        account = await self._repo.create_account(
            user_id=user_id,
            bank_name=data.bank_name,
            account_type=data.account_type,
            masked_account=data.masked_account,
            currency=data.currency,
            balance=data.balance,
        )
        return AccountResponse.model_validate(account)

    async def list_accounts(self, user_id: uuid.UUID) -> AccountListResponse:
        accounts = await self._repo.get_user_accounts(user_id)
        return AccountListResponse(
            total=len(accounts),
            items=[AccountResponse.model_validate(a) for a in accounts],
        )

    async def get_account(
        self, account_id: uuid.UUID, user_id: uuid.UUID
    ) -> AccountResponse:
        account = await self._repo.get_user_account_by_id(account_id, user_id)
        if not account:
            raise NotFoundError("Account")
        return AccountResponse.model_validate(account)
