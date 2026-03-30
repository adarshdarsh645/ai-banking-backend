import uuid
from datetime import date
from decimal import Decimal
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Transaction, session)

    # ─── User-scoped query builder ─────────────────────────────────────────────
    def _user_stmt(self, user_id: uuid.UUID):
        return (
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id)
        )

    async def get_transactions(
        self,
        user_id: uuid.UUID,
        account_id: uuid.UUID | None = None,
        txn_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[int, Sequence[Transaction]]:
        stmt = self._user_stmt(user_id)

        if account_id:
            stmt = stmt.where(Transaction.account_id == account_id)
        if txn_type:
            stmt = stmt.where(Transaction.txn_type == txn_type)
        if date_from:
            stmt = stmt.where(Transaction.txn_date >= date_from)
        if date_to:
            stmt = stmt.where(Transaction.txn_date <= date_to)

        # total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # paginated results
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Transaction.txn_date.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        return total, result.scalars().all()

    async def get_user_transaction_by_id(
        self, txn_id: uuid.UUID, user_id: uuid.UUID
    ) -> Transaction | None:
        stmt = (
            self._user_stmt(user_id)
            .where(Transaction.id == txn_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_transaction(
        self,
        account_id: uuid.UUID,
        description: str,
        category: str,
        amount: Decimal,
        currency: str,
        txn_type: str,
        txn_date: date,
        merchant: str | None = None,
        posted_date: date | None = None,
    ) -> Transaction:
        return await self.create(
            account_id=account_id,
            description=description,
            category=category,
            amount=amount,
            currency=currency,
            txn_type=txn_type,
            merchant=merchant,
            txn_date=txn_date,
            posted_date=posted_date,
        )

    async def bulk_create(self, records: list[dict]) -> int:
        """Insert many transactions at once. Returns number of inserted rows."""
        instances = [Transaction(**rec) for rec in records]
        self.session.add_all(instances)
        await self.session.flush()
        return len(instances)

    async def get_spending_by_category(
        self, user_id: uuid.UUID, month: int | None = None, year: int | None = None
    ) -> Sequence[tuple[str, Decimal]]:
        from sqlalchemy import extract
        
        stmt = (
            select(Transaction.category, func.sum(Transaction.amount).label("total"))
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.user_id == user_id, Transaction.txn_type == "debit")
        )
        if month:
            stmt = stmt.where(extract('month', Transaction.txn_date) == month)
        if year:
            stmt = stmt.where(extract('year', Transaction.txn_date) == year)
            
        stmt = stmt.group_by(Transaction.category)
        result = await self.session.execute(stmt)
        return result.all()
