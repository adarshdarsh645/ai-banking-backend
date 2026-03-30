import uuid
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Account, session)

    async def get_user_accounts(self, user_id: uuid.UUID) -> Sequence[Account]:
        stmt = select(Account).where(Account.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_account_by_id(
        self, account_id: uuid.UUID, user_id: uuid.UUID
    ) -> Account | None:
        stmt = select(Account).where(
            Account.id == account_id, Account.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_account(
        self,
        user_id: uuid.UUID,
        bank_name: str,
        account_type: str,
        masked_account: str,
        currency: str,
        balance: Decimal,
    ) -> Account:
        return await self.create(
            user_id=user_id,
            bank_name=bank_name,
            account_type=account_type,
            masked_account=masked_account,
            currency=currency,
            balance=balance,
        )

    async def count_user_accounts(self, user_id: uuid.UUID) -> int:
        return await self.count(Account.user_id == user_id)
